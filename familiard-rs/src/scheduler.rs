//! Wake scheduling — read-only probes of cortex state + the band scheduler.
//!
//! Contract parity with the Python daemon: the daemon never decides, it
//! nudges; every behavioral gate re-checks in the cortex on wake.

use std::path::Path;

use rand::Rng;

use crate::config::{in_hour_window, FamiliardConfig, DESIRE_WAKE_THRESHOLD};

#[derive(Debug, Default)]
pub struct BandSchedulerState {
    pub last_band_pulse: f64,
    pub last_offband_hour: i64,
}

impl BandSchedulerState {
    pub fn new() -> Self {
        Self {
            last_band_pulse: 0.0,
            last_offband_hour: -1,
        }
    }
}

/// One scheduling decision: should a band_tick pulse fire right now?
///
/// In an active band: fire every `band_interval_sec`. Off-band: at most one
/// probabilistic attempt per hour (day/night chance).
pub fn decide_band_pulse(
    config: &FamiliardConfig,
    state: &mut BandSchedulerState,
    minute_of_day: u32,
    hour: u32,
    monotonic_now: f64,
    rng: &mut impl Rng,
) -> bool {
    let in_band = config
        .active_bands
        .iter()
        .any(|&(start, end)| (start..end).contains(&minute_of_day));
    if in_band {
        if monotonic_now - state.last_band_pulse >= config.band_interval_sec {
            state.last_band_pulse = monotonic_now;
            return true;
        }
        return false;
    }
    if state.last_offband_hour == i64::from(hour) {
        return false;
    }
    state.last_offband_hour = i64::from(hour);
    let night = in_hour_window(hour, config.night_start_hour, config.night_end_hour);
    let chance = if night {
        config.offband_chance_night
    } else {
        config.offband_chance_day
    };
    if rng.gen::<f64>() < chance {
        state.last_band_pulse = monotonic_now;
        return true;
    }
    false
}

/// True when any persisted desire level sits at/above the wake threshold.
/// Read-only; the cortex re-derives the effective dominant desire itself.
pub fn read_desire_pressure(desires_path: &Path) -> bool {
    let Ok(text) = std::fs::read_to_string(desires_path) else {
        return false;
    };
    let Ok(value) = serde_json::from_str::<serde_json::Value>(&text) else {
        return false;
    };
    let levels = value.get("desires").unwrap_or(&value);
    let Some(map) = levels.as_object() else {
        return false;
    };
    map.values()
        .filter_map(|v| v.as_f64())
        .any(|level| level >= DESIRE_WAKE_THRESHOLD)
}

/// True when any active commitment is due (SQLite read-only; never writes).
pub fn read_due_commitments(db_path: &Path, now: f64) -> bool {
    if !db_path.exists() {
        return false;
    }
    let flags = rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY;
    let Ok(conn) = rusqlite::Connection::open_with_flags(db_path, flags) else {
        return false;
    };
    let _ = conn.busy_timeout(std::time::Duration::from_secs(1));
    let count: Result<i64, _> = conn.query_row(
        "SELECT COUNT(*) FROM runtime_commitments \
         WHERE status IN ('open', 'snoozed') \
           AND due_at IS NOT NULL AND due_at <= ?1 \
           AND (snooze_until IS NULL OR snooze_until <= ?1)",
        [now],
        |row| row.get(0),
    );
    matches!(count, Ok(n) if n > 0)
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::rngs::StdRng;
    use rand::SeedableRng;

    fn cfg() -> FamiliardConfig {
        FamiliardConfig {
            active_bands: vec![(8 * 60, 10 * 60)],
            band_interval_sec: 100.0,
            offband_chance_day: 1.0,
            offband_chance_night: 0.0,
            night_start_hour: 0,
            night_end_hour: 7,
            ..Default::default()
        }
    }

    #[test]
    fn band_pulse_fires_on_interval_inside_band() {
        let config = cfg();
        let mut state = BandSchedulerState::new();
        let mut rng = StdRng::seed_from_u64(0);
        assert!(decide_band_pulse(
            &config,
            &mut state,
            8 * 60,
            8,
            1000.0,
            &mut rng
        ));
        assert!(!decide_band_pulse(
            &config,
            &mut state,
            8 * 60 + 1,
            8,
            1050.0,
            &mut rng
        ));
        assert!(decide_band_pulse(
            &config,
            &mut state,
            8 * 60 + 2,
            8,
            1100.0,
            &mut rng
        ));
    }

    #[test]
    fn offband_rolls_once_per_hour_with_day_night_chance() {
        let config = cfg();
        let mut state = BandSchedulerState::new();
        let mut rng = StdRng::seed_from_u64(0);
        // Daytime off-band with chance 1.0: first check of the hour fires...
        assert!(decide_band_pulse(
            &config,
            &mut state,
            14 * 60,
            14,
            0.0,
            &mut rng
        ));
        // ...but not twice within the same hour.
        assert!(!decide_band_pulse(
            &config,
            &mut state,
            14 * 60 + 30,
            14,
            10.0,
            &mut rng
        ));
        // Night hour with chance 0.0: never fires.
        assert!(!decide_band_pulse(
            &config,
            &mut state,
            3 * 60,
            3,
            20.0,
            &mut rng
        ));
    }

    #[test]
    fn desire_pressure_threshold() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("desires.json");
        std::fs::write(&path, r#"{"desires": {"curiosity": 0.3}}"#).unwrap();
        assert!(!read_desire_pressure(&path));
        std::fs::write(&path, r#"{"desires": {"curiosity": 0.7}}"#).unwrap();
        assert!(read_desire_pressure(&path));
        std::fs::write(&path, "not json").unwrap();
        assert!(!read_desire_pressure(&path));
        assert!(!read_desire_pressure(&dir.path().join("missing.json")));
    }

    #[test]
    fn due_commitments_read_only_probe() {
        let dir = tempfile::tempdir().unwrap();
        let db = dir.path().join("commitments.db");
        let conn = rusqlite::Connection::open(&db).unwrap();
        conn.execute_batch(
            "CREATE TABLE runtime_commitments (
                id TEXT PRIMARY KEY, summary TEXT, kind TEXT, status TEXT,
                due_at REAL, priority INTEGER, created_by TEXT, person TEXT,
                created_at REAL, updated_at REAL, completed_at REAL,
                snooze_until REAL, last_reminded_at REAL,
                reminder_count INTEGER DEFAULT 0, metadata_json TEXT
            );",
        )
        .unwrap();
        assert!(!read_due_commitments(&db, 1000.0));
        conn.execute(
            "INSERT INTO runtime_commitments (id, summary, kind, status, due_at, priority,
             created_by, created_at, updated_at, metadata_json)
             VALUES ('c1', 'water plants', 'reminder', 'open', 900.0, 1, 'agent', 1.0, 1.0, '{}')",
            [],
        )
        .unwrap();
        assert!(read_due_commitments(&db, 1000.0));
        // Snoozed into the future → not due.
        conn.execute(
            "UPDATE runtime_commitments SET snooze_until = 2000.0 WHERE id = 'c1'",
            [],
        )
        .unwrap();
        assert!(!read_due_commitments(&db, 1000.0));
        assert!(!read_due_commitments(
            &dir.path().join("missing.db"),
            1000.0
        ));
    }
}
