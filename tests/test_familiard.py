"""familiard body daemon — config, sampler, scheduler, decay, wake socket.

The daemon's contract: read-only toward cortex-owned state (desires.json,
commitments.db), writes only its own payload + the offline self-state settle,
and wake events are nudges — every behavioral gate stays in the cortex.
"""

from __future__ import annotations

import json
import random
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import pytest

from familiar_agent.familiard import (
    BandSchedulerState,
    Familiard,
    FamiliardConfig,
    _parse_bands,
    apply_offline_settle,
    build_interoception_payload,
    decide_band_pulse,
    read_desire_pressure,
    read_due_commitments,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def test_parse_bands_valid_and_garbage():
    assert _parse_bands("07:00-09:00,18:30-24:00") == [(420, 540), (1110, 1440)]
    assert _parse_bands("") == []
    assert _parse_bands("garbage,25:00-26:00,09:00-08:00") == []


def test_config_load_from_file_with_env_override(tmp_path: Path, monkeypatch):
    conf = tmp_path / "familiard.conf"
    conf.write_text(
        "\n".join(
            [
                "# comment",
                "band_interval_sec = 600",
                "active_bands = 08:00-10:00",
                "offband_chance_day = 0.25",
                "offline_decay = off",
            ]
        )
    )
    monkeypatch.setenv("FAMILIARD_BAND_INTERVAL_SEC", "300")
    cfg = FamiliardConfig.load(conf)
    assert cfg.band_interval_sec == 300.0  # env beats file
    assert cfg.active_bands == [(480, 600)]
    assert cfg.offband_chance_day == 0.25
    assert cfg.offline_decay is False


def test_config_defaults_without_file(tmp_path: Path):
    cfg = FamiliardConfig.load(tmp_path / "missing.conf")
    assert cfg.sample_interval_sec == 10.0
    assert cfg.active_bands  # non-empty defaults


# ---------------------------------------------------------------------------
# Interoception payload
# ---------------------------------------------------------------------------


def test_payload_roundtrips_through_mcp_provider(tmp_path: Path):
    """The daemon's payload must be consumable by the cortex's existing
    MCPInteroceptionProvider with zero cortex changes."""
    from familiar_neighbor.mind.interoception import MCPInteroceptionProvider

    payload = build_interoception_payload(
        cpu_load=0.5,
        mem_free=0.6,
        now=datetime.now().astimezone(),
        quiet_start=23,
        quiet_end=7,
    )
    path = tmp_path / "interoception.json"
    path.write_text(json.dumps(payload))

    signal = MCPInteroceptionProvider(path).collect()
    assert signal.provider == "mcp"
    assert 0.0 <= signal.energy <= 1.0
    assert 0.0 <= signal.cognitive_load <= 1.0
    assert signal.raw_metrics["cpu_load_fraction"] == pytest.approx(0.5)


def test_payload_quiet_hours_wrap_midnight():
    payload_night = build_interoception_payload(
        cpu_load=0.1,
        mem_free=0.8,
        now=datetime.now().astimezone().replace(hour=2),
        quiet_start=23,
        quiet_end=7,
    )
    payload_day = build_interoception_payload(
        cpu_load=0.1,
        mem_free=0.8,
        now=datetime.now().astimezone().replace(hour=14),
        quiet_start=23,
        quiet_end=7,
    )
    assert payload_night["signal"]["quiet_hours"] is True
    assert payload_day["signal"]["quiet_hours"] is False
    assert payload_night["signal"]["energy"] < payload_day["signal"]["energy"]


def test_stale_payload_rejected_fresh_accepted(tmp_path: Path):
    """Staleness gating still works end-to-end (45s default in the provider)."""
    from familiar_neighbor.mind.interoception import MCPInteroceptionProvider

    payload = build_interoception_payload(
        cpu_load=0.2,
        mem_free=0.5,
        now=datetime.now().astimezone(),
        quiet_start=23,
        quiet_end=7,
    )
    payload["signal"]["observed_at"] = "2020-01-01T00:00:00+00:00"
    path = tmp_path / "interoception.json"
    path.write_text(json.dumps(payload))
    assert MCPInteroceptionProvider(path).collect().provider == "noop"


# ---------------------------------------------------------------------------
# Band scheduler
# ---------------------------------------------------------------------------


def _cfg(**kw) -> FamiliardConfig:
    cfg = FamiliardConfig()
    for key, value in kw.items():
        setattr(cfg, key, value)
    return cfg


def _at(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 7, 2, hour, minute, 0)


def test_band_pulse_fires_on_interval_inside_band():
    cfg = _cfg(active_bands=[(8 * 60, 10 * 60)], band_interval_sec=100.0)
    state = BandSchedulerState()
    rng = random.Random(0)

    assert decide_band_pulse(config=cfg, state=state, now=_at(8), monotonic_now=1000.0, rng=rng)
    # 50s later: not yet.
    assert not decide_band_pulse(
        config=cfg, state=state, now=_at(8, 1), monotonic_now=1050.0, rng=rng
    )
    # 100s after the first: fires again.
    assert decide_band_pulse(config=cfg, state=state, now=_at(8, 2), monotonic_now=1100.0, rng=rng)


def test_offband_rolls_once_per_hour_with_day_night_chance():
    cfg = _cfg(
        active_bands=[(8 * 60, 9 * 60)],
        offband_chance_day=1.0,
        offband_chance_night=0.0,
        night_start_hour=0,
        night_end_hour=7,
    )
    state = BandSchedulerState()
    rng = random.Random(0)

    # Daytime off-band with chance 1.0: first check of the hour fires...
    assert decide_band_pulse(config=cfg, state=state, now=_at(14), monotonic_now=0.0, rng=rng)
    # ...but not twice within the same hour.
    assert not decide_band_pulse(
        config=cfg, state=state, now=_at(14, 30), monotonic_now=10.0, rng=rng
    )
    # Night hour with chance 0.0: never fires.
    assert not decide_band_pulse(config=cfg, state=state, now=_at(3), monotonic_now=20.0, rng=rng)


# ---------------------------------------------------------------------------
# Read-only cortex-state probes
# ---------------------------------------------------------------------------


def test_desire_pressure_threshold(tmp_path: Path):
    path = tmp_path / "desires.json"
    path.write_text(json.dumps({"desires": {"curiosity": 0.3, "reflect": 0.2}}))
    assert read_desire_pressure(path) is False
    path.write_text(json.dumps({"desires": {"curiosity": 0.7}}))
    assert read_desire_pressure(path) is True
    assert read_desire_pressure(tmp_path / "missing.json") is False
    (tmp_path / "garbage.json").write_text("not json")
    assert read_desire_pressure(tmp_path / "garbage.json") is False


def test_due_commitments_read_only_probe(tmp_path: Path):
    """The daemon reads the real store's DB (created by the store itself)
    without ever opening a write connection."""
    from familiar_runtime.commitments.store import SQLiteCommitmentStore

    db = tmp_path / "commitments.db"
    store = SQLiteCommitmentStore(db)
    now = time.time()
    assert read_due_commitments(db, now=now) is False

    store.create(summary="water the plants", due_at=now - 60)
    assert read_due_commitments(db, now=now) is True

    # Missing DB → quietly False, never an error.
    assert read_due_commitments(tmp_path / "nope.db", now=now) is False
    store.close()


# ---------------------------------------------------------------------------
# Offline self-state decay
# ---------------------------------------------------------------------------


def test_offline_settle_moves_toward_baseline(tmp_path: Path):
    path = tmp_path / "self_state.json"
    path.write_text(json.dumps({"arousal": 0.9, "unresolved_tension": 0.8, "fatigue": 0.2}))

    assert apply_offline_settle(path, steps=3) is True
    values = json.loads(path.read_text())
    # arousal decays toward baseline 0.35, tension toward 0.2.
    assert 0.35 < values["arousal"] < 0.9
    assert 0.2 < values["unresolved_tension"] < 0.8
    # fatigue already at baseline: unchanged.
    assert values["fatigue"] == pytest.approx(0.2)


def test_offline_settle_noops_safely(tmp_path: Path):
    assert apply_offline_settle(tmp_path / "missing.json", steps=5) is False
    path = tmp_path / "self_state.json"
    path.write_text(json.dumps({"arousal": 0.35}))
    assert apply_offline_settle(path, steps=0) is False
    path.write_text("not json")
    assert apply_offline_settle(path, steps=2) is False


# ---------------------------------------------------------------------------
# Wake socket (POSIX only)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(sys.platform == "win32", reason="Unix sockets unavailable on Windows")
@pytest.mark.asyncio
async def test_wake_roundtrip_daemon_to_listener():
    """Daemon emits → WakeListener receives; rate limit collapses repeats."""
    from familiar_agent.wake import WakeListener

    # AF_UNIX paths are length-limited (~104 bytes); pytest tmp_path can
    # exceed that, so use a short mkdtemp under /tmp.
    short_dir = Path(tempfile.mkdtemp(prefix="fam-", dir="/tmp"))
    cfg = FamiliardConfig()
    cfg.socket_path = short_dir / "familiard.sock"
    cfg.interoception_path = short_dir / "interoception.json"
    cfg.self_state_path = short_dir / "self_state.json"
    cfg.desires_path = short_dir / "desires.json"
    cfg.commitments_db_path = short_dir / "commitments.db"
    cfg.reminder_wake_cooldown_sec = 0.05

    daemon = Familiard(cfg)
    await daemon.start()
    try:
        listener = WakeListener(cfg.socket_path, enabled=True)
        # Establish the connection (no event yet → returns None on timeout).
        assert await listener.wait(0.3) is None
        assert daemon.client_count == 1

        daemon._emit_wake("reminder")
        event = await listener.wait(2.0)
        assert event is not None and event.reason == "reminder"

        # Within the cooldown the second emit is swallowed.
        daemon._emit_wake("reminder")
        daemon._emit_wake("reminder")
        first = await listener.wait(0.5)
        second = await listener.wait(0.3)
        assert (first is None) or (second is None)

        listener.close()
    finally:
        await daemon.stop()
    assert not cfg.socket_path.exists()  # socket cleaned up


def test_decay_tick_gated_on_connected_cortex(tmp_path: Path):
    """No settle while a cortex is connected (or within grace); steps apply
    only after real offline wall-clock has accumulated."""
    cfg = _cfg(
        self_state_path=tmp_path / "self_state.json",
        offline_grace_sec=60.0,
        offline_decay_step_sec=600.0,
    )
    cfg.self_state_path.write_text(json.dumps({"arousal": 0.9}))
    daemon = Familiard(cfg)

    # A connected cortex pins the decay clock: no steps, clock tracks along.
    daemon._clients.add(object())  # type: ignore[arg-type]
    daemon._last_client_seen = 0.0
    daemon._last_decay_applied = 0.0
    assert daemon._decay_tick(monotonic_now=10_000.0) == 0
    assert daemon._last_decay_applied == 10_000.0

    # Disconnected but within grace: still nothing.
    daemon._clients.clear()
    daemon._last_client_seen = 10_000.0
    assert daemon._decay_tick(monotonic_now=10_030.0) == 0

    # Past grace with 2 step-intervals of offline time: 2 settle steps apply.
    steps = daemon._decay_tick(monotonic_now=11_260.0)
    assert steps == 2
    assert json.loads(cfg.self_state_path.read_text())["arousal"] < 0.9
