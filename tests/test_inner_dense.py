"""Dense recurrence: idle broadcasts re-enter modules, with batched disk I/O.

FAMILIAR_INNER_DENSE (default off, requires the inner loop) closes the
density gap: idle winners update the attention schema and re-enter broadcast
listeners between turns, drive nudges accumulate and flush once per full
cycle, and the cadence floor becomes configurable down to ~1 Hz. Off by
default = idle cognition stays read-only, byte-identical to before.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from familiar_neighbor.mind.attention_schema import AttentionSchema
from familiar_neighbor.mind.self_state import SelfState
from familiar_neighbor.mind.workspace import Coalition

from tests.test_agent_react_loop import _make_agent


def _coalition(source="scene", activation=0.8):
    return Coalition(
        source=source,
        summary="s",
        activation=activation,
        urgency=0.5,
        novelty=0.5,
        context_block="b",
    )


# ── AttentionSchema.note_focus: batched persistence ──


def test_note_focus_batches_saves(tmp_path):
    schema = AttentionSchema(state_path=tmp_path / "att.json")
    saves = []
    schema._save_state = lambda: saves.append(1)  # type: ignore[method-assign]
    for _ in range(9):
        schema.note_focus(_coalition(), save_every=10, save_interval_sec=9999)
    assert not saves  # under both thresholds — nothing written
    schema.note_focus(_coalition(), save_every=10, save_interval_sec=9999)
    assert len(saves) == 1  # 10th note flushes
    assert len(schema.focus_history()) == 10


def test_note_focus_flush_on_interval(tmp_path):
    schema = AttentionSchema(state_path=tmp_path / "att.json")
    saves = []
    schema._save_state = lambda: saves.append(1)  # type: ignore[method-assign]
    schema._last_save_at -= 120.0  # pretend a minute+ has passed
    schema.note_focus(_coalition(), save_every=10, save_interval_sec=60.0)
    assert len(saves) == 1


def test_update_focus_persists_idle_backlog(tmp_path):
    path = tmp_path / "att.json"
    schema = AttentionSchema(state_path=path)
    schema.note_focus(_coalition(source="monologue"), save_every=100, save_interval_sec=9999)
    assert not path.exists()  # idle note deferred
    schema.update_focus(_coalition(source="desire"))  # a real turn
    restored = AttentionSchema(state_path=path)
    assert [e.source for e in restored.focus_history()] == ["monologue", "desire"]


def test_flush_persists_immediately(tmp_path):
    path = tmp_path / "att.json"
    schema = AttentionSchema(state_path=path)
    schema.note_focus(_coalition(), save_every=100, save_interval_sec=9999)
    schema.flush()
    assert path.exists()


# ── SelfState deferred saves ──


def test_self_state_default_saves_every_broadcast(tmp_path):
    state = SelfState(path=tmp_path / "self.json")
    writes = []
    state._write = lambda: writes.append(1)  # type: ignore[method-assign]
    state.apply_broadcast(_coalition())
    state.apply_broadcast(_coalition())
    assert len(writes) == 2  # historical behaviour untouched


def test_self_state_defer_batches_and_flushes(tmp_path):
    path = tmp_path / "self.json"
    state = SelfState(path=path)
    state.defer_saves(min_interval=3600.0)
    state._last_save_at = __import__("time").monotonic()  # window just started
    before = state.snapshot()["arousal"]
    state.apply_broadcast(_coalition(source="prediction"))
    state.apply_broadcast(_coalition(source="prediction"))
    assert not path.exists()  # deferred
    state.flush()
    assert path.exists()
    restored = SelfState(path=path)
    assert restored.snapshot()["arousal"] != before  # nudges survived the batch


def test_self_state_flush_noop_when_clean(tmp_path):
    path = tmp_path / "self.json"
    state = SelfState(path=path)
    state.flush()
    assert not path.exists()  # nothing dirty, nothing written


# ── Agent tick wiring ──


def _dense_agent(tmp_path, *, dense: bool):
    agent = _make_agent()
    agent.config.inner_dense = dense
    agent._attention_schema = AttentionSchema(state_path=tmp_path / "att.json")
    agent._self_state = SelfState(path=tmp_path / "self.json")
    agent._pending_drive_nudges = {}
    return agent


@pytest.mark.asyncio
async def test_tick_off_leaves_attention_and_listeners_untouched(tmp_path):
    agent = _dense_agent(tmp_path, dense=False)
    fired = []
    agent._workspace.register_broadcast_listener(lambda w: fired.append(w))
    before = len(agent._attention_schema.focus_history())
    for _ in range(5):
        await agent._inner_loop_tick()
    assert len(agent._attention_schema.focus_history()) == before
    assert not fired


@pytest.mark.asyncio
async def test_tick_dense_updates_attention_and_notifies(tmp_path):
    from unittest.mock import AsyncMock

    from familiar_agent.inner_loop import CompeteResult

    agent = _dense_agent(tmp_path, dense=True)
    winner = _coalition(source="narrative")
    agent._compete_once = AsyncMock(return_value=CompeteResult(winner=winner, others=[]))
    fired = []

    async def probe(w):
        fired.append(w.source)

    agent._workspace.register_broadcast_listener(probe)
    for _ in range(3):
        await agent._inner_loop_tick()
    assert len(agent._attention_schema.focus_history()) == 3
    assert fired == ["narrative"] * 3  # broadcast re-entered listeners on idle ticks


@pytest.mark.asyncio
async def test_drive_nudges_accumulate_and_flush_on_full_cycle(tmp_path):
    agent = _dense_agent(tmp_path, dense=True)
    desires = MagicMock()
    agent._desires = desires
    agent._pending_drive_nudges = {"reflect": 0.06}
    agent._inner_tick_count = 0
    agent._inner_loop_config.full_cycle_every = 1  # every tick is a full cycle
    await agent._inner_loop_tick()
    desires.boost.assert_any_call("reflect", 0.06)
    assert agent._pending_drive_nudges == {} or "reflect" not in agent._pending_drive_nudges


@pytest.mark.asyncio
async def test_nudge_listener_caps_accumulation():
    agent = _make_agent()
    agent._pending_drive_nudges = {}
    for _ in range(20):
        await agent._on_broadcast_drive_nudge(_coalition(source="scene", activation=1.0))
    assert agent._pending_drive_nudges["look_around"] == pytest.approx(0.15)


@pytest.mark.asyncio
async def test_nudge_listener_ignores_unmapped_sources():
    agent = _make_agent()
    agent._pending_drive_nudges = {}
    await agent._on_broadcast_drive_nudge(_coalition(source="train_of_thought"))
    assert agent._pending_drive_nudges == {}


# ── Cadence floor ──


def test_cadence_floor_default_matches_historical_constant():
    from familiar_agent.agent import _INNER_CADENCE_MIN_SEC
    from familiar_agent.config import AgentConfig

    import os

    os.environ.pop("FAMILIAR_INNER_MIN_INTERVAL", None)
    assert AgentConfig().inner_min_interval == _INNER_CADENCE_MIN_SEC


def test_cadence_floor_configurable(monkeypatch):
    monkeypatch.setenv("FAMILIAR_INNER_MIN_INTERVAL", "1")
    monkeypatch.setenv("FAMILIAR_INNER_LOOP_INTERVAL", "1")
    from familiar_agent.config import AgentConfig

    cfg = AgentConfig()
    agent = _make_agent()
    agent.config = cfg
    agent._collect_interoception = lambda: (MagicMock(energy=1.0), None)
    agent._modulate_inner_cadence()
    assert agent._inner_loop_config.interval_sec == pytest.approx(1.0)


def test_config_inner_dense_off_by_default(monkeypatch):
    monkeypatch.delenv("FAMILIAR_INNER_DENSE", raising=False)
    from familiar_agent.config import AgentConfig

    assert AgentConfig().inner_dense is False
