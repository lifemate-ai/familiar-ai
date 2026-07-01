//! Interoception sampling — same payload shape and mapping formulas as the
//! Python daemon, consumable by MCPInteroceptionProvider unchanged.

use std::path::Path;

use chrono::{Local, Utc};
use serde_json::json;

use crate::config::in_hour_window;

fn clamp01(value: f64) -> f64 {
    value.clamp(0.0, 1.0)
}

/// 1-minute load average normalized by core count; 0.0 when unavailable.
pub fn read_cpu_load_fraction() -> f64 {
    let mut loads = [0f64; 3];
    // SAFETY: getloadavg writes up to 3 doubles into the provided buffer.
    let n = unsafe { libc::getloadavg(loads.as_mut_ptr(), 3) };
    if n < 1 {
        return 0.0;
    }
    let cores = std::thread::available_parallelism()
        .map(|c| c.get() as f64)
        .unwrap_or(1.0);
    (loads[0] / cores).max(0.0)
}

/// MemAvailable/MemTotal from /proc/meminfo; 0.5 when unavailable (parity).
pub fn read_mem_free_fraction() -> f64 {
    let Ok(text) = std::fs::read_to_string("/proc/meminfo") else {
        return 0.5;
    };
    let mut total = None;
    let mut available = None;
    for line in text.lines() {
        let parse = |prefix: &str| -> Option<f64> {
            line.strip_prefix(prefix)?
                .split_whitespace()
                .next()?
                .parse()
                .ok()
        };
        if total.is_none() {
            total = parse("MemTotal:");
        }
        if available.is_none() {
            available = parse("MemAvailable:");
        }
        if let (Some(t), Some(a)) = (total, available) {
            if t > 0.0 {
                return clamp01(a / t);
            }
        }
    }
    0.5
}

/// Map raw body metrics to the provider's signal shape (formula parity).
pub fn build_payload(
    cpu_load: f64,
    mem_free: f64,
    hour: u32,
    quiet_start: u32,
    quiet_end: u32,
) -> serde_json::Value {
    let quiet = in_hour_window(hour, quiet_start, quiet_end);
    let arousal = clamp01(cpu_load);
    let mem_pressure = 1.0 - clamp01(mem_free);
    let energy = clamp01(0.85 - 0.35 * arousal - if quiet { 0.23 } else { 0.0 });
    let cognitive_load = clamp01(0.6 * arousal + 0.4 * mem_pressure);
    let body_stress = clamp01(0.5 * arousal + 0.35 * mem_pressure);
    let social_openness = clamp01(0.6 - if quiet { 0.18 } else { 0.0 } - 0.25 * body_stress);
    json!({
        "signal": {
            "observed_at": Utc::now().to_rfc3339(),
            "local_hour": hour,
            "quiet_hours": quiet,
            "energy": energy,
            "cognitive_load": cognitive_load,
            "body_stress": body_stress,
            "social_openness": social_openness,
            "raw_metrics": {
                "cpu_load_fraction": (arousal * 10000.0).round() / 10000.0,
                "mem_free_fraction": (clamp01(mem_free) * 10000.0).round() / 10000.0,
            },
        }
    })
}

pub fn local_hour() -> u32 {
    use chrono::Timelike;
    Local::now().hour()
}

/// Atomic write: tmp + rename, matching the Python daemon.
pub fn write_json_atomic(path: &Path, payload: &serde_json::Value) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let tmp = path.with_extension("json.tmp");
    std::fs::write(&tmp, serde_json::to_string(payload)?)?;
    std::fs::rename(&tmp, path)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn payload_quiet_hours_lower_energy() {
        let night = build_payload(0.1, 0.8, 2, 23, 7);
        let day = build_payload(0.1, 0.8, 14, 23, 7);
        assert_eq!(night["signal"]["quiet_hours"], true);
        assert_eq!(day["signal"]["quiet_hours"], false);
        let e_night = night["signal"]["energy"].as_f64().unwrap();
        let e_day = day["signal"]["energy"].as_f64().unwrap();
        assert!(e_night < e_day);
    }

    #[test]
    fn payload_fields_clamped_and_shaped() {
        let p = build_payload(5.0, -1.0, 12, 23, 7); // silly inputs clamp
        let s = &p["signal"];
        for key in ["energy", "cognitive_load", "body_stress", "social_openness"] {
            let v = s[key].as_f64().unwrap();
            assert!((0.0..=1.0).contains(&v), "{key} out of range: {v}");
        }
        assert_eq!(s["raw_metrics"]["cpu_load_fraction"], 1.0);
        assert!(s["observed_at"].as_str().unwrap().contains('T'));
    }

    #[test]
    fn atomic_write_roundtrip() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("interoception.json");
        let payload = build_payload(0.3, 0.6, 10, 23, 7);
        write_json_atomic(&path, &payload).unwrap();
        let read: serde_json::Value =
            serde_json::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
        assert_eq!(read["signal"]["local_hour"], 10);
    }
}
