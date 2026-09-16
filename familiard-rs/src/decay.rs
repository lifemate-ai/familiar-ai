//! Offline self-state decay — settle toward baseline while no cortex runs.
//!
//! Baselines and step rate mirror familiar_neighbor.mind.self_state; drift
//! here is cosmetic (the cortex re-settles on its next turn anyway).

use std::path::Path;

use crate::interoception::write_json_atomic;

const BASELINES: [(&str, f64); 6] = [
    ("arousal", 0.35),
    ("fatigue", 0.2),
    ("social_pull", 0.35),
    ("sensor_confidence", 0.7),
    ("unresolved_tension", 0.2),
    ("focus_stability", 0.5),
];
const SETTLE_RATE: f64 = 0.08;
const MAX_STEPS: u32 = 200;

/// Settle self_state.json toward baseline by `steps` decay steps.
/// Returns true when the file was updated.
pub fn apply_offline_settle(path: &Path, steps: u32) -> bool {
    if steps == 0 || !path.exists() {
        return false;
    }
    let Ok(text) = std::fs::read_to_string(path) else {
        return false;
    };
    let Ok(mut values) = serde_json::from_str::<serde_json::Value>(&text) else {
        return false;
    };
    let Some(map) = values.as_object_mut() else {
        return false;
    };
    let mut changed = false;
    for (key, baseline) in BASELINES {
        let Some(current) = map.get(key).and_then(|v| v.as_f64()) else {
            continue;
        };
        let mut settled = current;
        for _ in 0..steps.min(MAX_STEPS) {
            settled += (baseline - settled) * SETTLE_RATE;
        }
        if (settled - current).abs() > 1e-9 {
            map.insert(key.to_string(), serde_json::json!(settled.clamp(0.0, 1.0)));
            changed = true;
        }
    }
    if changed {
        changed = write_json_atomic(path, &values).is_ok();
    }
    changed
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn settle_moves_toward_baseline() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("self_state.json");
        std::fs::write(
            &path,
            r#"{"arousal": 0.9, "unresolved_tension": 0.8, "fatigue": 0.2}"#,
        )
        .unwrap();
        assert!(apply_offline_settle(&path, 3));
        let values: serde_json::Value =
            serde_json::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
        let arousal = values["arousal"].as_f64().unwrap();
        assert!(arousal < 0.9 && arousal > 0.35);
        let fatigue = values["fatigue"].as_f64().unwrap();
        assert!((fatigue - 0.2).abs() < 1e-9); // at baseline: unchanged
    }

    #[test]
    fn settle_noops_safely() {
        let dir = tempfile::tempdir().unwrap();
        assert!(!apply_offline_settle(&dir.path().join("missing.json"), 5));
        let path = dir.path().join("self_state.json");
        std::fs::write(&path, r#"{"arousal": 0.35}"#).unwrap();
        assert!(!apply_offline_settle(&path, 0));
        std::fs::write(&path, "not json").unwrap();
        assert!(!apply_offline_settle(&path, 2));
    }
}
