//! familiard — the always-on body daemon (Rust port of familiar_agent/familiard.py).
//!
//! Same contract, one static binary: interoception sampling to the payload
//! file MCPInteroceptionProvider reads, wake events (reminder / desire /
//! band_tick) over the Unix socket WakeListener connects to, and offline
//! self-state decay gated on "no cortex connected". Read-only toward all
//! cortex-owned state. A wake only accelerates the cortex's idle poll —
//! every behavioral gate re-checks in the cortex.

mod config;
mod decay;
mod interoception;
mod scheduler;

use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use chrono::Timelike;
use tokio::io::AsyncWriteExt;
use tokio::net::{UnixListener, UnixStream};
use tokio::sync::Mutex;

use config::FamiliardConfig;
use scheduler::BandSchedulerState;

type Clients = Arc<Mutex<Vec<tokio::net::unix::OwnedWriteHalf>>>;

struct Daemon {
    config: FamiliardConfig,
    clients: Clients,
    last_wake_at: Mutex<HashMap<String, Instant>>,
    last_client_seen: Mutex<Instant>,
    last_decay_applied: Mutex<Instant>,
}

impl Daemon {
    fn new(config: FamiliardConfig) -> Self {
        Self {
            config,
            clients: Arc::new(Mutex::new(Vec::new())),
            last_wake_at: Mutex::new(HashMap::new()),
            last_client_seen: Mutex::new(Instant::now()),
            last_decay_applied: Mutex::new(Instant::now()),
        }
    }

    /// Rate-limited push of a wake event to all connected cortices.
    /// No clients → no emit AND no cooldown burn (an event nobody heard
    /// doesn't count, so a cortex connecting later gets woken promptly).
    async fn emit_wake(&self, reason: &str) {
        let mut clients = self.clients.lock().await;
        if clients.is_empty() {
            return;
        }
        let cooldown = match reason {
            "reminder" => self.config.reminder_wake_cooldown_sec,
            "desire" => self.config.desire_wake_cooldown_sec,
            _ => 30.0,
        };
        {
            let mut last_map = self.last_wake_at.lock().await;
            if let Some(last) = last_map.get(reason) {
                if last.elapsed().as_secs_f64() < cooldown {
                    return;
                }
            }
            last_map.insert(reason.to_string(), Instant::now());
        }
        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_secs_f64())
            .unwrap_or(0.0);
        let line = format!(
            "{}\n",
            serde_json::json!({"type": "wake", "reason": reason, "ts": ts})
        );
        let mut alive = Vec::new();
        let count = clients.len();
        for mut writer in clients.drain(..) {
            if writer.write_all(line.as_bytes()).await.is_ok() {
                alive.push(writer);
            }
        }
        *clients = alive;
        eprintln!("familiard: wake emitted: {reason} -> {count} client(s)");
    }

    async fn sampler_loop(self: Arc<Self>) {
        loop {
            let payload = interoception::build_payload(
                interoception::read_cpu_load_fraction(),
                interoception::read_mem_free_fraction(),
                interoception::local_hour(),
                self.config.quiet_start_hour,
                self.config.quiet_end_hour,
            );
            if let Err(exc) =
                interoception::write_json_atomic(&self.config.interoception_path, &payload)
            {
                eprintln!("familiard: interoception sample failed: {exc}");
            }
            tokio::time::sleep(Duration::from_secs_f64(
                self.config.sample_interval_sec.max(0.05),
            ))
            .await;
        }
    }

    async fn scheduler_loop(self: Arc<Self>) {
        use rand::SeedableRng;

        let mut band_state = BandSchedulerState::new();
        // StdRng is Send (ThreadRng is not, and this future crosses awaits).
        let mut rng = rand::rngs::StdRng::from_entropy();
        let started = Instant::now();
        loop {
            let now_ts = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map(|d| d.as_secs_f64())
                .unwrap_or(0.0);
            if scheduler::read_due_commitments(&self.config.commitments_db_path, now_ts) {
                self.emit_wake("reminder").await;
            }
            if scheduler::read_desire_pressure(&self.config.desires_path) {
                self.emit_wake("desire").await;
            }
            let local = chrono::Local::now();
            let minute_of_day = local.hour() * 60 + local.minute();
            if scheduler::decide_band_pulse(
                &self.config,
                &mut band_state,
                minute_of_day,
                local.hour(),
                started.elapsed().as_secs_f64(),
                &mut rng,
            ) {
                self.emit_wake("band_tick").await;
            }
            tokio::time::sleep(Duration::from_secs_f64(
                self.config.scheduler_interval_sec.max(0.05),
            ))
            .await;
        }
    }

    async fn decay_loop(self: Arc<Self>) {
        if !self.config.offline_decay {
            return;
        }
        loop {
            let cortex_offline = {
                let clients = self.clients.lock().await;
                let last_seen = self.last_client_seen.lock().await;
                clients.is_empty()
                    && last_seen.elapsed().as_secs_f64() >= self.config.offline_grace_sec
            };
            let mut last_applied = self.last_decay_applied.lock().await;
            if cortex_offline {
                let steps = (last_applied.elapsed().as_secs_f64()
                    / self.config.offline_decay_step_sec) as u32;
                if steps > 0 {
                    if decay::apply_offline_settle(&self.config.self_state_path, steps) {
                        eprintln!("familiard: offline settle applied ({steps} step(s))");
                    }
                    *last_applied = Instant::now();
                }
            } else {
                *last_applied = Instant::now();
            }
            drop(last_applied);
            tokio::time::sleep(Duration::from_secs_f64(
                self.config.offline_decay_step_sec.clamp(1.0, 60.0),
            ))
            .await;
        }
    }

    async fn accept_loop(self: Arc<Self>, listener: UnixListener) {
        loop {
            match listener.accept().await {
                Ok((stream, _)) => {
                    let (mut read_half, write_half) = stream.into_split();
                    {
                        let mut clients = self.clients.lock().await;
                        clients.push(write_half);
                        *self.last_client_seen.lock().await = Instant::now();
                        eprintln!("familiard: cortex connected ({} client(s))", clients.len());
                    }
                    // Drain the read side until EOF so disconnects are noticed.
                    let daemon = Arc::clone(&self);
                    tokio::spawn(async move {
                        use tokio::io::AsyncReadExt;
                        let mut buf = [0u8; 256];
                        while matches!(read_half.read(&mut buf).await, Ok(n) if n > 0) {}
                        *daemon.last_client_seen.lock().await = Instant::now();
                        // Dead write halves are pruned on the next emit.
                    });
                }
                Err(exc) => {
                    eprintln!("familiard: accept failed: {exc}");
                    tokio::time::sleep(Duration::from_secs(1)).await;
                }
            }
        }
    }
}

async fn bind_socket(config: &FamiliardConfig) -> std::io::Result<UnixListener> {
    if let Some(parent) = config.socket_path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    if config.socket_path.exists() {
        // A live daemon would accept the probe; a stale socket must go.
        match tokio::time::timeout(
            Duration::from_secs(1),
            UnixStream::connect(&config.socket_path),
        )
        .await
        {
            Ok(Ok(_)) => {
                return Err(std::io::Error::new(
                    std::io::ErrorKind::AddrInUse,
                    format!(
                        "familiard already running on {}",
                        config.socket_path.display()
                    ),
                ));
            }
            _ => {
                let _ = std::fs::remove_file(&config.socket_path);
            }
        }
    }
    UnixListener::bind(&config.socket_path)
}

#[tokio::main]
async fn main() {
    let config = FamiliardConfig::load(None);
    let listener = match bind_socket(&config).await {
        Ok(listener) => listener,
        Err(exc) => {
            eprintln!("familiard: {exc}");
            std::process::exit(1);
        }
    };
    eprintln!(
        "familiard: wake socket listening at {}",
        config.socket_path.display()
    );
    let socket_path = config.socket_path.clone();
    let daemon = Arc::new(Daemon::new(config));

    let tasks = vec![
        tokio::spawn(Arc::clone(&daemon).sampler_loop()),
        tokio::spawn(Arc::clone(&daemon).scheduler_loop()),
        tokio::spawn(Arc::clone(&daemon).decay_loop()),
        tokio::spawn(Arc::clone(&daemon).accept_loop(listener)),
    ];

    let mut sigterm = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate())
        .expect("signal handler");
    tokio::select! {
        _ = tokio::signal::ctrl_c() => {},
        _ = sigterm.recv() => {},
    }
    eprintln!("familiard: shutting down");
    for task in tasks {
        task.abort();
    }
    let _ = std::fs::remove_file(&socket_path);
}
