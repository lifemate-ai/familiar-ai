"""Dense recurrence: idle broadcasts re-enter modules, with batched disk I/O.

FAMILIAR_INNER_DENSE (default off, requires the inner loop) closes the
density gap: idle winners update the attention schema and re-enter broadcast
listeners between turns, drive nudges accumulate and flush once per full
cycle, and the cadence floor becomes configurable down to ~1 Hz. Off by
default = idle cognition stays read-only, byte-identical to before.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

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


# ── Review-round regressions: durability ordering + turn-yield ──


@pytest.mark.asyncio
async def test_tick_yields_when_turn_starts_mid_compete(tmp_path):
    """A turn starting during the competition await must abort the dense
    re-entry — idle broadcasts must not inject into a live turn."""
    from unittest.mock import AsyncMock

    from familiar_agent.inner_loop import CompeteResult

    agent = _dense_agent(tmp_path, dense=True)
    winner = _coalition(source="narrative")

    async def compete_then_turn_starts(**kwargs):
        agent._turn_active = True  # user message landed mid-await
        return CompeteResult(winner=winner, others=[])

    agent._compete_once = AsyncMock(side_effect=compete_then_turn_starts)
    fired = []

    async def probe(w):
        fired.append(w)

    agent._workspace.register_broadcast_listener(probe)
    await agent._inner_loop_tick()
    assert not fired
    assert len(agent._attention_schema.focus_history()) == 0


@pytest.mark.asyncio
async def test_post_response_pipeline_flushes_deferred_self_state(tmp_path):
    """The turn's own affect deltas must be durable once the post-response
    pipeline ends — the defer_saves 'never a real turn's state' promise."""
    path = tmp_path / "self.json"
    agent = _make_agent()
    state = SelfState(path=path)
    state.defer_saves(min_interval=3600.0)
    state._last_save_at = __import__("time").monotonic()
    state.apply_broadcast(_coalition(source="prediction"))  # deferred, dirty
    agent._self_state = state
    assert not path.exists()

    # Pipeline internals blow up immediately — the finally-flush must still run.
    agent._infer_emotion = MagicMock(side_effect=RuntimeError("boom"))
    await agent._run_post_response_pipeline(
        user_input="x",
        final_text="y",
        camera_used=False,
        observation_action_name=None,
        observation_action_input=None,
        is_desire_turn=False,
        desires=None,
        companion_mood="engaged",
    )
    assert path.exists()


@pytest.mark.asyncio
async def test_close_flushes_after_producers_stop(tmp_path):
    """close() must stop producers (drain, inner loop) BEFORE the flush, or a
    late background nudge re-dirties the store past the flush and is lost."""
    agent = _make_agent()
    order = []

    state = SelfState(path=tmp_path / "self.json")
    orig_flush = state.flush
    state.flush = lambda: (order.append("flush"), orig_flush())[1]  # type: ignore[method-assign]
    agent._self_state = state
    agent._attention_schema = AttentionSchema(state_path=tmp_path / "att.json")

    agent._camera = None
    agent._drain_background_tasks = AsyncMock(side_effect=lambda: order.append("drain"))
    agent._write_today_narrative = AsyncMock()
    agent._utility_backend = agent.backend  # skip day summary
    inner_loop = MagicMock()
    inner_loop.stop = AsyncMock(side_effect=lambda: order.append("inner_stop"))
    agent._inner_loop = inner_loop
    agent._memory_worker = None
    agent._mcp = None
    agent._memory = MagicMock()
    agent._stt = None
    agent._tts = None

    await agent.close()
    assert "flush" in order and "drain" in order and "inner_stop" in order
    assert order.index("flush") > order.index("drain")
    assert order.index("flush") > order.index("inner_stop")


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
