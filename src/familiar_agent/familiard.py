"""familiard — the always-on body daemon (Loop 0 of the nervous system).

The LLM cortex runs turns; *this* process keeps the body alive between and
without them. It owns, at a few hertz and with zero LLM calls:

- **Interoception sampling**: CPU / memory / time-of-day → a semantic body
  signal written where ``MCPInteroceptionProvider`` already reads it, so the
  cortex needs no new code to feel it.
- **Wake scheduling**: due commitments, desire threshold crossings, and
  schedule-band pulses become wake events pushed over a Unix socket. A wake
  only *accelerates* the cortex's own idle poll — every behavioral gate
  (reminder backoff, quiet hours, auto_desire, precedence) stays in the
  cortex, which re-checks them on wake. The daemon never decides, it nudges.
- **Offline affect decay**: while no cortex is connected, ``self_state.json``
  settles toward baseline on wall-clock time — feelings fade during sleep
  instead of freezing.

Read-only by design toward cortex-owned state: desires.json and
commitments.db are only ever read (the desire file has 18 cortex-side write
sites and a non-atomic saver; two writers would corrupt it), and
observations.db is never opened at all (its single connection sets no
busy_timeout). The daemon's only writes are its own payload file and the
offline self-state settle, which is gated on "no cortex connected".

Run with ``uv run familiard``; stop with SIGINT/SIGTERM. Configuration comes
from ``~/.familiar_ai/familiard.conf`` (key = value lines) with env
overrides; see ``FamiliardConfig``.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
import random
import signal
import sqlite3
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_STATE_DIR = Path.home() / ".familiar_ai"
_DEFAULT_CONF_PATH = _STATE_DIR / "familiard.conf"

# Desire threshold mirrors familiar_neighbor.mind.desires.TRIGGER_THRESHOLD.
# Kept as a literal on purpose: the daemon must not import the cortex's mind
# packages (it reads their *files*, not their code), and the cortex re-checks
# the real threshold on wake anyway — a stale mirror only costs a spare nudge.
_DESIRE_WAKE_THRESHOLD = 0.6


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def _parse_bands(raw: str) -> list[tuple[int, int]]:
    """Parse "07:00-09:00,18:00-24:00" into [(start_minute, end_minute)]."""
    bands: list[tuple[int, int]] = []
    for part in raw.split(","):
        part = part.strip()
        if not part or "-" not in part:
            continue
        try:
            start_s, end_s = part.split("-", 1)
            sh, sm = (start_s.strip().split(":") + ["0"])[:2]
            eh, em = (end_s.strip().split(":") + ["0"])[:2]
            start = int(sh) * 60 + int(sm)
            end = int(eh) * 60 + int(em)
        except ValueError:
            continue
        if 0 <= start < end <= 24 * 60:
            bands.append((start, end))
    return bands


@dataclass(slots=True)
class FamiliardConfig:
    interoception_path: Path = _STATE_DIR / "interoception.json"
    socket_path: Path = _STATE_DIR / "familiard.sock"
    self_state_path: Path = _STATE_DIR / "self_state.json"
    desires_path: Path = _STATE_DIR / "desires.json"
    commitments_db_path: Path = _STATE_DIR / "commitments.db"

    sample_interval_sec: float = 10.0
    scheduler_interval_sec: float = 5.0

    # Active bands: within these local-time windows the daemon emits a
    # band_tick pulse every band_interval_sec. Outside them, at most one
    # probabilistic pulse per hour (day/night chance), kokone-style.
    active_bands: list[tuple[int, int]] = field(
        default_factory=lambda: _parse_bands("07:00-09:00,12:00-13:00,18:00-24:00")
    )
    band_interval_sec: float = 1200.0
    offband_chance_day: float = 0.5
    offband_chance_night: float = 0.1
    night_start_hour: int = 0
    night_end_hour: int = 7

    # Quiet hours for the interoception signal (mirrors the cortex default).
    quiet_start_hour: int = 23
    quiet_end_hour: int = 7

    # Wake rate limits per reason.
    reminder_wake_cooldown_sec: float = 60.0
    desire_wake_cooldown_sec: float = 120.0

    # Offline decay: apply one settle step toward baseline per this many
    # seconds of no-cortex wall-clock (matches SelfState's per-event 0.08
    # step at a "several times an hour" cadence).
    offline_decay: bool = True
    offline_decay_step_sec: float = 600.0
    offline_grace_sec: float = 60.0

    @classmethod
    def load(cls, conf_path: Path | None = None) -> FamiliardConfig:
        """Read key=value config with env overrides (FAMILIARD_<KEY>)."""
        cfg = cls()
        path = conf_path or Path(os.environ.get("FAMILIARD_CONF", "").strip() or _DEFAULT_CONF_PATH)
        raw: dict[str, str] = {}
        if path.exists():
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    raw[key.strip().lower()] = value.strip()
            except Exception as exc:  # noqa: BLE001
                logger.warning("familiard.conf unreadable (%s); using defaults", exc)
        for key in list(raw):
            env = os.environ.get(f"FAMILIARD_{key.upper()}")
            if env is not None:
                raw[key] = env
        # Env-only overrides for keys absent from the file.
        for env_key, value in os.environ.items():
            if env_key.startswith("FAMILIARD_"):
                raw.setdefault(env_key[len("FAMILIARD_") :].lower(), value)

        def _f(key: str, current: float) -> float:
            try:
                return float(raw[key]) if key in raw else current
            except ValueError:
                return current

        def _i(key: str, current: int) -> int:
            try:
                return int(raw[key]) if key in raw else current
            except ValueError:
                return current

        def _p(key: str, current: Path) -> Path:
            return Path(raw[key]).expanduser() if raw.get(key) else current

        cfg.interoception_path = _p("interoception_path", cfg.interoception_path)
        cfg.socket_path = _p("socket_path", cfg.socket_path)
        cfg.self_state_path = _p("self_state_path", cfg.self_state_path)
        cfg.desires_path = _p("desires_path", cfg.desires_path)
        cfg.commitments_db_path = _p("commitments_db_path", cfg.commitments_db_path)
        cfg.sample_interval_sec = _f("sample_interval_sec", cfg.sample_interval_sec)
        cfg.scheduler_interval_sec = _f("scheduler_interval_sec", cfg.scheduler_interval_sec)
        if "active_bands" in raw:
            cfg.active_bands = _parse_bands(raw["active_bands"])
        cfg.band_interval_sec = _f("band_interval_sec", cfg.band_interval_sec)
        cfg.offband_chance_day = _f("offband_chance_day", cfg.offband_chance_day)
        cfg.offband_chance_night = _f("offband_chance_night", cfg.offband_chance_night)
        cfg.night_start_hour = _i("night_start_hour", cfg.night_start_hour)
        cfg.night_end_hour = _i("night_end_hour", cfg.night_end_hour)
        cfg.quiet_start_hour = _i("quiet_start_hour", cfg.quiet_start_hour)
        cfg.quiet_end_hour = _i("quiet_end_hour", cfg.quiet_end_hour)
        cfg.reminder_wake_cooldown_sec = _f(
            "reminder_wake_cooldown_sec", cfg.reminder_wake_cooldown_sec
        )
        cfg.desire_wake_cooldown_sec = _f("desire_wake_cooldown_sec", cfg.desire_wake_cooldown_sec)
        if "offline_decay" in raw:
            cfg.offline_decay = raw["offline_decay"].strip().lower() in ("1", "true", "yes", "on")
        cfg.offline_decay_step_sec = _f("offline_decay_step_sec", cfg.offline_decay_step_sec)
        cfg.offline_grace_sec = _f("offline_grace_sec", cfg.offline_grace_sec)
        return cfg


# ---------------------------------------------------------------------------
# Interoception sampling
# ---------------------------------------------------------------------------


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _read_cpu_load_fraction() -> float:
    """1-minute load average normalized by core count; 0.0 when unavailable."""
    try:
        load1 = os.getloadavg()[0]
        cores = os.cpu_count() or 1
        return max(0.0, load1 / cores)
    except (OSError, AttributeError):  # Windows has no getloadavg
        return 0.0


def _read_mem_free_fraction() -> float:
    """MemAvailable/MemTotal from /proc/meminfo; 0.5 when unavailable."""
    try:
        total = available = None
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                total = float(line.split()[1])
            elif line.startswith("MemAvailable:"):
                available = float(line.split()[1])
            if total and available:
                return _clamp01(available / total)
    except Exception:  # noqa: BLE001
        pass
    return 0.5


def _in_hour_window(hour: int, start: int, end: int) -> bool:
    """True when ``hour`` falls in [start, end), wrapping over midnight."""
    if start <= end:
        return start <= hour < end
    return hour >= start or hour < end


def build_interoception_payload(
    *,
    cpu_load: float,
    mem_free: float,
    now: datetime,
    quiet_start: int,
    quiet_end: int,
) -> dict:
    """Map raw body metrics to the MCPInteroceptionProvider signal shape."""
    hour = now.hour
    quiet = _in_hour_window(hour, quiet_start, quiet_end)
    arousal = _clamp01(cpu_load)
    mem_pressure = 1.0 - _clamp01(mem_free)
    energy = _clamp01(0.85 - 0.35 * arousal - (0.23 if quiet else 0.0))
    cognitive_load = _clamp01(0.6 * arousal + 0.4 * mem_pressure)
    body_stress = _clamp01(0.5 * arousal + 0.35 * mem_pressure)
    social_openness = _clamp01(0.6 - (0.18 if quiet else 0.0) - 0.25 * body_stress)
    return {
        "signal": {
            "observed_at": now.astimezone(timezone.utc).isoformat(),
            "local_hour": hour,
            "quiet_hours": quiet,
            "energy": energy,
            "cognitive_load": cognitive_load,
            "body_stress": body_stress,
            "social_openness": social_openness,
            "raw_metrics": {
                "cpu_load_fraction": round(arousal, 4),
                "mem_free_fraction": round(_clamp01(mem_free), 4),
            },
        }
    }


def _write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Wake scheduling (pure decision logic — clock/rng injected for tests)
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class BandSchedulerState:
    last_band_pulse: float = 0.0
    last_offband_hour: int = -1


def decide_band_pulse(
    *,
    config: FamiliardConfig,
    state: BandSchedulerState,
    now: datetime,
    monotonic_now: float,
    rng: random.Random,
) -> bool:
    """One scheduling decision: should a band_tick pulse fire right now?

    In an active band: fire every ``band_interval_sec``. Off-band: at most one
    probabilistic attempt per hour (day/night chance), kokone-style.
    """
    minute_of_day = now.hour * 60 + now.minute
    in_band = any(start <= minute_of_day < end for start, end in config.active_bands)
    if in_band:
        if monotonic_now - state.last_band_pulse >= config.band_interval_sec:
            state.last_band_pulse = monotonic_now
            return True
        return False
    # Off-band: single roll at the top of each hour window.
    if state.last_offband_hour == now.hour:
        return False
    state.last_offband_hour = now.hour
    night = _in_hour_window(now.hour, config.night_start_hour, config.night_end_hour)
    chance = config.offband_chance_night if night else config.offband_chance_day
    if rng.random() < chance:
        state.last_band_pulse = monotonic_now
        return True
    return False


def read_desire_pressure(desires_path: Path, threshold: float = _DESIRE_WAKE_THRESHOLD) -> bool:
    """True when any persisted desire level sits at/above the wake threshold.

    Read-only. The cortex re-derives the *effective* dominant desire with its
    own affordances/cooldowns — this is only "worth waking up for a look".
    """
    try:
        raw = json.loads(desires_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return False
    levels = raw.get("desires", raw) if isinstance(raw, dict) else {}
    if not isinstance(levels, dict):
        return False
    return any(isinstance(v, (int, float)) and float(v) >= threshold for v in levels.values())


def read_due_commitments(db_path: Path, *, now: float) -> bool:
    """True when any active commitment is due (read-only; never writes).

    Opens commitments.db in SQLite read-only URI mode — the store sets WAL +
    busy_timeout on its own connection, so a reader is safe. All reminder
    semantics (backoff, caps, quiet hours) stay in the cortex; this is only
    the "there might be something" accelerator.
    """
    if not db_path.exists():
        return False
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=1.0)
        try:
            row = conn.execute(
                """
                SELECT COUNT(*) FROM runtime_commitments
                WHERE status IN ('open', 'snoozed')
                  AND due_at IS NOT NULL AND due_at <= ?
                  AND (snooze_until IS NULL OR snooze_until <= ?)
                """,
                (now, now),
            ).fetchone()
            return bool(row and row[0] > 0)
        finally:
            conn.close()
    except sqlite3.Error:
        return False


# ---------------------------------------------------------------------------
# Offline self-state decay
# ---------------------------------------------------------------------------

# Baselines mirror familiar_neighbor.mind.self_state._BASELINES; kept as data
# (not an import) so the daemon never loads cortex packages. Drift here is
# cosmetic: the cortex re-settles on its next turn anyway.
_SELF_STATE_BASELINES: dict[str, float] = {
    "arousal": 0.35,
    "fatigue": 0.2,
    "social_pull": 0.35,
    "sensor_confidence": 0.7,
    "unresolved_tension": 0.2,
    "focus_stability": 0.5,
}
_SETTLE_RATE = 0.08  # one SelfState settle step


def apply_offline_settle(path: Path, *, steps: int) -> bool:
    """Settle self_state.json toward baseline by ``steps`` decay steps.

    Returns True when the file was updated. Only called while no cortex is
    connected — the cortex is the sole writer whenever it is alive.
    """
    if steps <= 0 or not path.exists():
        return False
    try:
        values = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(values, dict):
            return False
        changed = False
        for key, baseline in _SELF_STATE_BASELINES.items():
            current = values.get(key, baseline)
            if not isinstance(current, (int, float)):
                continue
            settled = float(current)
            for _ in range(min(steps, 200)):
                settled = settled + (baseline - settled) * _SETTLE_RATE
            if abs(settled - float(current)) > 1e-9:
                values[key] = max(0.0, min(1.0, settled))
                changed = True
        if changed:
            _write_json_atomic(path, values)
        return changed
    except Exception as exc:  # noqa: BLE001
        logger.debug("offline settle skipped: %s", exc)
        return False


# ---------------------------------------------------------------------------
# The daemon
# ---------------------------------------------------------------------------


class Familiard:
    """Owns the sampler, scheduler, wake socket, and offline decay loops."""

    def __init__(self, config: FamiliardConfig | None = None) -> None:
        self.config = config or FamiliardConfig.load()
        self._clients: set[asyncio.StreamWriter] = set()
        self._server: asyncio.base_events.Server | None = None
        self._tasks: list[asyncio.Task] = []
        self._band_state = BandSchedulerState()
        self._last_wake_at: dict[str, float] = {}
        self._last_client_seen = time.monotonic()
        self._last_decay_applied = time.monotonic()
        self._rng = random.Random()
        self._stopping = asyncio.Event()

    # ── wake socket ──

    @property
    def client_count(self) -> int:
        return len(self._clients)

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self._clients.add(writer)
        self._last_client_seen = time.monotonic()
        logger.info("cortex connected (%d client(s))", len(self._clients))
        try:
            while not reader.at_eof():
                data = await reader.read(1024)
                if not data:
                    break
        except (ConnectionError, asyncio.CancelledError):
            pass
        finally:
            self._clients.discard(writer)
            self._last_client_seen = time.monotonic()
            with contextlib.suppress(Exception):
                writer.close()
            logger.info("cortex disconnected (%d client(s))", len(self._clients))

    def _emit_wake(self, reason: str) -> None:
        """Rate-limited push of a wake event to all connected cortices.

        No clients → no emit AND no cooldown burn: an event nobody heard
        doesn't count, so a cortex connecting later gets woken promptly.
        """
        if not self._clients:
            return
        cooldowns = {
            "reminder": self.config.reminder_wake_cooldown_sec,
            "desire": self.config.desire_wake_cooldown_sec,
        }
        now = time.monotonic()
        last = self._last_wake_at.get(reason, 0.0)
        if now - last < cooldowns.get(reason, 30.0):
            return
        self._last_wake_at[reason] = now
        line = json.dumps({"type": "wake", "reason": reason, "ts": time.time()}) + "\n"
        payload = line.encode("utf-8")
        for writer in list(self._clients):
            try:
                writer.write(payload)
            except Exception:  # noqa: BLE001
                self._clients.discard(writer)
        logger.info("wake emitted: %s -> %d client(s)", reason, len(self._clients))

    # ── loops ──

    async def _sampler_loop(self) -> None:
        while not self._stopping.is_set():
            try:
                payload = build_interoception_payload(
                    cpu_load=_read_cpu_load_fraction(),
                    mem_free=_read_mem_free_fraction(),
                    now=datetime.now().astimezone(),
                    quiet_start=self.config.quiet_start_hour,
                    quiet_end=self.config.quiet_end_hour,
                )
                _write_json_atomic(self.config.interoception_path, payload)
            except Exception as exc:  # noqa: BLE001
                logger.warning("interoception sample failed: %s", exc)
            await self._sleep(self.config.sample_interval_sec)

    async def _scheduler_loop(self) -> None:
        while not self._stopping.is_set():
            try:
                if read_due_commitments(self.config.commitments_db_path, now=time.time()):
                    self._emit_wake("reminder")
                if read_desire_pressure(self.config.desires_path):
                    self._emit_wake("desire")
                if decide_band_pulse(
                    config=self.config,
                    state=self._band_state,
                    now=datetime.now(),
                    monotonic_now=time.monotonic(),
                    rng=self._rng,
                ):
                    self._emit_wake("band_tick")
            except Exception as exc:  # noqa: BLE001
                logger.warning("scheduler tick failed: %s", exc)
            await self._sleep(self.config.scheduler_interval_sec)

    def _decay_tick(self, *, monotonic_now: float) -> int:
        """One offline-decay decision. Returns the number of settle steps applied.

        Feelings settle toward baseline only while NO cortex is connected
        (plus a grace period) — whenever a cortex is alive, it is the sole
        writer of self_state.json and the decay clock just tracks along.
        """
        cortex_offline = (
            not self._clients
            and monotonic_now - self._last_client_seen >= self.config.offline_grace_sec
        )
        if not cortex_offline:
            self._last_decay_applied = monotonic_now
            return 0
        steps = int(
            (monotonic_now - self._last_decay_applied) // self.config.offline_decay_step_sec
        )
        if steps <= 0:
            return 0
        applied = apply_offline_settle(self.config.self_state_path, steps=steps)
        self._last_decay_applied = monotonic_now
        if applied:
            logger.info("offline settle applied (%d step(s))", steps)
        return steps if applied else 0

    async def _decay_loop(self) -> None:
        if not self.config.offline_decay:
            return
        while not self._stopping.is_set():
            try:
                self._decay_tick(monotonic_now=time.monotonic())
            except Exception as exc:  # noqa: BLE001
                logger.warning("decay tick failed: %s", exc)
            await self._sleep(min(60.0, self.config.offline_decay_step_sec))

    async def _sleep(self, seconds: float) -> None:
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self._stopping.wait(), timeout=max(0.05, seconds))

    # ── lifecycle ──

    async def start(self) -> None:
        if sys.platform == "win32":
            logger.warning("wake socket unavailable on Windows; running sampler/decay only")
        else:
            sock = self.config.socket_path
            sock.parent.mkdir(parents=True, exist_ok=True)
            if sock.exists():
                # A live daemon would be listening; a stale socket must go.
                try:
                    reader_writer = await asyncio.wait_for(
                        asyncio.open_unix_connection(str(sock)), timeout=1.0
                    )
                    reader_writer[1].close()
                    raise RuntimeError(f"familiard already running on {sock}")
                except (ConnectionError, asyncio.TimeoutError, FileNotFoundError, OSError):
                    sock.unlink(missing_ok=True)
            self._server = await asyncio.start_unix_server(self._handle_client, path=str(sock))
            logger.info("wake socket listening at %s", sock)

        self._tasks = [
            asyncio.create_task(self._sampler_loop(), name="familiard-sampler"),
            asyncio.create_task(self._scheduler_loop(), name="familiard-scheduler"),
            asyncio.create_task(self._decay_loop(), name="familiard-decay"),
        ]

    async def stop(self) -> None:
        self._stopping.set()
        for task in self._tasks:
            task.cancel()
        for task in self._tasks:
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await task
        if self._server is not None:
            self._server.close()
            with contextlib.suppress(Exception):
                await self._server.wait_closed()
        with contextlib.suppress(Exception):
            if sys.platform != "win32":
                self.config.socket_path.unlink(missing_ok=True)
        for writer in list(self._clients):
            with contextlib.suppress(Exception):
                writer.close()
        self._clients.clear()

    async def run_forever(self) -> None:
        await self.start()
        loop = asyncio.get_running_loop()
        if sys.platform != "win32":
            for sig in (signal.SIGINT, signal.SIGTERM):
                with contextlib.suppress(NotImplementedError):
                    loop.add_signal_handler(sig, self._stopping.set)
        await self._stopping.wait()
        await self.stop()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s familiard: %(message)s",
    )
    config = FamiliardConfig.load()
    daemon = Familiard(config)
    try:
        asyncio.run(daemon.run_forever())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
