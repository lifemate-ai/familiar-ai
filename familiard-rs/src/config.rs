//! Configuration — behavior-parity with the Python daemon's FamiliardConfig.
//!
//! Same file (`~/.familiar_ai/familiard.conf`, `key = value` lines), same
//! `FAMILIARD_*` env overrides, same defaults. A user can swap the Python
//! daemon for this binary without touching their config.

use std::collections::HashMap;
use std::path::PathBuf;

pub const DESIRE_WAKE_THRESHOLD: f64 = 0.6;

#[derive(Debug, Clone)]
pub struct FamiliardConfig {
    pub interoception_path: PathBuf,
    pub socket_path: PathBuf,
    pub self_state_path: PathBuf,
    pub desires_path: PathBuf,
    pub commitments_db_path: PathBuf,

    pub sample_interval_sec: f64,
    pub scheduler_interval_sec: f64,

    /// Active bands as (start_minute, end_minute) of local day.
    pub active_bands: Vec<(u32, u32)>,
    pub band_interval_sec: f64,
    pub offband_chance_day: f64,
    pub offband_chance_night: f64,
    pub night_start_hour: u32,
    pub night_end_hour: u32,

    pub quiet_start_hour: u32,
    pub quiet_end_hour: u32,

    pub reminder_wake_cooldown_sec: f64,
    pub desire_wake_cooldown_sec: f64,

    pub offline_decay: bool,
    pub offline_decay_step_sec: f64,
    pub offline_grace_sec: f64,
}

fn state_dir() -> PathBuf {
    let home = std::env::var_os("HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."));
    home.join(".familiar_ai")
}

impl Default for FamiliardConfig {
    fn default() -> Self {
        let dir = state_dir();
        Self {
            interoception_path: dir.join("interoception.json"),
            socket_path: dir.join("familiard.sock"),
            self_state_path: dir.join("self_state.json"),
            desires_path: dir.join("desires.json"),
            commitments_db_path: dir.join("commitments.db"),
            sample_interval_sec: 10.0,
            scheduler_interval_sec: 5.0,
            active_bands: parse_bands("07:00-09:00,12:00-13:00,18:00-24:00"),
            band_interval_sec: 1200.0,
            offband_chance_day: 0.5,
            offband_chance_night: 0.1,
            night_start_hour: 0,
            night_end_hour: 7,
            quiet_start_hour: 23,
            quiet_end_hour: 7,
            reminder_wake_cooldown_sec: 60.0,
            desire_wake_cooldown_sec: 120.0,
            offline_decay: true,
            offline_decay_step_sec: 600.0,
            offline_grace_sec: 60.0,
        }
    }
}

/// Parse "07:00-09:00,18:30-24:00" into minute-of-day ranges (invalid parts skipped).
pub fn parse_bands(raw: &str) -> Vec<(u32, u32)> {
    let mut bands = Vec::new();
    for part in raw.split(',') {
        let part = part.trim();
        let Some((start_s, end_s)) = part.split_once('-') else {
            continue;
        };
        let (Some(start), Some(end)) = (parse_hhmm(start_s), parse_hhmm(end_s)) else {
            continue;
        };
        if start < end && end <= 24 * 60 {
            bands.push((start, end));
        }
    }
    bands
}

fn parse_hhmm(raw: &str) -> Option<u32> {
    let raw = raw.trim();
    let (hh, mm) = raw.split_once(':').unwrap_or((raw, "0"));
    let hour: u32 = hh.trim().parse().ok()?;
    let minute: u32 = mm.trim().parse().ok()?;
    if minute < 60 {
        Some(hour * 60 + minute)
    } else {
        None
    }
}

impl FamiliardConfig {
    /// Load from the conf file with `FAMILIARD_*` env overrides (env beats file).
    pub fn load(conf_path: Option<PathBuf>) -> Self {
        let mut cfg = Self::default();
        let path = conf_path.unwrap_or_else(|| {
            std::env::var("FAMILIARD_CONF")
                .ok()
                .filter(|v| !v.trim().is_empty())
                .map(PathBuf::from)
                .unwrap_or_else(|| state_dir().join("familiard.conf"))
        });

        let mut raw: HashMap<String, String> = HashMap::new();
        if let Ok(text) = std::fs::read_to_string(&path) {
            for line in text.lines() {
                let line = line.trim();
                if line.is_empty() || line.starts_with('#') {
                    continue;
                }
                if let Some((key, value)) = line.split_once('=') {
                    raw.insert(key.trim().to_lowercase(), value.trim().to_string());
                }
            }
        }
        for (env_key, value) in std::env::vars() {
            if let Some(key) = env_key.strip_prefix("FAMILIARD_") {
                raw.insert(key.to_lowercase(), value);
            }
        }

        let f = |key: &str, current: f64| -> f64 {
            raw.get(key).and_then(|v| v.parse().ok()).unwrap_or(current)
        };
        let i = |key: &str, current: u32| -> u32 {
            raw.get(key).and_then(|v| v.parse().ok()).unwrap_or(current)
        };
        let p = |key: &str, current: PathBuf| -> PathBuf {
            raw.get(key)
                .filter(|v| !v.is_empty())
                .map(PathBuf::from)
                .unwrap_or(current)
        };

        cfg.interoception_path = p("interoception_path", cfg.interoception_path);
        cfg.socket_path = p("socket_path", cfg.socket_path);
        cfg.self_state_path = p("self_state_path", cfg.self_state_path);
        cfg.desires_path = p("desires_path", cfg.desires_path);
        cfg.commitments_db_path = p("commitments_db_path", cfg.commitments_db_path);
        cfg.sample_interval_sec = f("sample_interval_sec", cfg.sample_interval_sec);
        cfg.scheduler_interval_sec = f("scheduler_interval_sec", cfg.scheduler_interval_sec);
        if let Some(bands) = raw.get("active_bands") {
            cfg.active_bands = parse_bands(bands);
        }
        cfg.band_interval_sec = f("band_interval_sec", cfg.band_interval_sec);
        cfg.offband_chance_day = f("offband_chance_day", cfg.offband_chance_day);
        cfg.offband_chance_night = f("offband_chance_night", cfg.offband_chance_night);
        cfg.night_start_hour = i("night_start_hour", cfg.night_start_hour);
        cfg.night_end_hour = i("night_end_hour", cfg.night_end_hour);
        cfg.quiet_start_hour = i("quiet_start_hour", cfg.quiet_start_hour);
        cfg.quiet_end_hour = i("quiet_end_hour", cfg.quiet_end_hour);
        cfg.reminder_wake_cooldown_sec =
            f("reminder_wake_cooldown_sec", cfg.reminder_wake_cooldown_sec);
        cfg.desire_wake_cooldown_sec = f("desire_wake_cooldown_sec", cfg.desire_wake_cooldown_sec);
        if let Some(v) = raw.get("offline_decay") {
            cfg.offline_decay = matches!(
                v.trim().to_lowercase().as_str(),
                "1" | "true" | "yes" | "on"
            );
        }
        cfg.offline_decay_step_sec = f("offline_decay_step_sec", cfg.offline_decay_step_sec);
        cfg.offline_grace_sec = f("offline_grace_sec", cfg.offline_grace_sec);
        cfg
    }
}

/// True when `hour` falls in [start, end), wrapping over midnight.
pub fn in_hour_window(hour: u32, start: u32, end: u32) -> bool {
    if start <= end {
        (start..end).contains(&hour)
    } else {
        hour >= start || hour < end
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_bands_valid_and_garbage() {
        assert_eq!(
            parse_bands("07:00-09:00,18:30-24:00"),
            vec![(420, 540), (1110, 1440)]
        );
        assert!(parse_bands("").is_empty());
        assert!(parse_bands("garbage,09:00-08:00").is_empty());
        // 25:00 start makes start >= end impossible only when end <= 24:00;
        // 25:00-26:00 is rejected by the end <= 24h rule.
        assert!(parse_bands("25:00-26:00").is_empty());
    }

    #[test]
    fn conf_file_with_env_override() {
        let dir = tempfile::tempdir().unwrap();
        let conf = dir.path().join("familiard.conf");
        std::fs::write(
            &conf,
            "# comment\nband_interval_sec = 600\nactive_bands = 08:00-10:00\noffline_decay = off\n",
        )
        .unwrap();
        std::env::set_var("FAMILIARD_BAND_INTERVAL_SEC", "300");
        let cfg = FamiliardConfig::load(Some(conf));
        std::env::remove_var("FAMILIARD_BAND_INTERVAL_SEC");
        assert_eq!(cfg.band_interval_sec, 300.0); // env beats file
        assert_eq!(cfg.active_bands, vec![(480, 600)]);
        assert!(!cfg.offline_decay);
    }

    #[test]
    fn hour_window_wraps_midnight() {
        assert!(in_hour_window(2, 23, 7));
        assert!(in_hour_window(23, 23, 7));
        assert!(!in_hour_window(12, 23, 7));
        assert!(in_hour_window(12, 8, 18));
    }
}
