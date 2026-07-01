"""Inner loop (Phase 2): driver, cheap-cycle seam, and the live tick.

PR1 landed the dark scaffolding (InnerLoop driver, TrainOfThought/InnerThought,
the _compete_once extraction); PR2 lights it: _inner_loop_tick runs a real
idle workspace cycle, feeds the train of thought / inner monologue, and
escalates a sustained focus by boosting a drive — never by starting a turn
itself (single-flight stays with the UI idle loops).
"""

from __future__ import annotations

import asyncio

import pytest

from familiar_agent.inner_loop import (
    InnerLoop,
    InnerLoopConfig,
    TrainOfThought,
)
from familiar_neighbor.mind.workspace import Coalition

from tests.test_agent_react_loop import _make_agent


def _coalition(source="desire", activation=0.8, urgency=0.5, novelty=0.3, summary="thinking"):
    return Coalition(
        source=source,
        summary=summary,
        activation=activation,
        urgency=urgency,
        novelty=novelty,
        context_block=f"[{source}] {summary}",
    )


# ── InnerLoop driver (modeled on MemoryJobWorker) ──


@pytest.mark.asyncio
async def test_start_is_idempotent_and_stop_is_clean():
    calls = 0

    async def tick():
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.01)

    loop = InnerLoop(tick, InnerLoopConfig(interval_sec=1.0))
    assert not loop.is_running
    await loop.start()
    await loop.start()  # idempotent — does not start a second task
    assert loop.is_running
    await asyncio.sleep(0.03)
    await loop.stop()
    assert not loop.is_running
    assert calls >= 1


@pytest.mark.asyncio
async def test_run_once_calls_tick_once():
    calls = 0

    async def tick():
        nonlocal calls
        calls += 1

    loop = InnerLoop(tick)
    await loop.run_once()
    assert calls == 1


@pytest.mark.asyncio
async def test_run_once_swallows_tick_errors():
    async def tick():
        raise RuntimeError("boom")

    loop = InnerLoop(tick)
    await loop.run_once()  # must not raise


@pytest.mark.asyncio
async def test_stop_without_start_is_safe():
    loop = InnerLoop(lambda: asyncio.sleep(0))
    await loop.stop()  # no task yet — no error
    assert not loop.is_running


# ── TrainOfThought (recurrence holder) ──


def test_train_of_thought_decays_and_reinjects():
    tot = TrainOfThought(decay=0.7, floor=0.1)
    assert tot.as_coalition() is None  # nothing observed yet
    tot.observe(_coalition(activation=0.8))
    inj = tot.as_coalition()
    assert inj is not None
    assert inj.source == "train_of_thought"
    assert inj.activation == pytest.approx(0.8 * 0.7)


def test_train_of_thought_streak_increments_on_same_source():
    tot = TrainOfThought()
    tot.observe(_coalition(source="curiosity"))
    assert tot.streak == 1
    tot.observe(_coalition(source="curiosity"))
    assert tot.streak == 2
    tot.observe(_coalition(source="concern"))
    assert tot.streak == 1  # reset on a different source


def test_train_of_thought_resets_below_floor():
    tot = TrainOfThought(decay=0.5, floor=0.3)
    tot.observe(_coalition(activation=0.5))
    # 0.5 * 0.5 = 0.25 < floor 0.3 → reset, return None
    assert tot.as_coalition() is None
    assert tot.last is None


# ── _compete_once / _gather byte-stability ──


@pytest.mark.asyncio
async def test_cheap_cycle_skips_memory_and_dmn():
    from unittest.mock import AsyncMock

    agent = _make_agent()
    agent._memory.as_coalition_async = AsyncMock(return_value=_coalition(source="memory"))
    agent._dmn = type("D", (), {"wander": AsyncMock(return_value=_coalition(source="dmn"))})()

    result = await agent._compete_once(cheap=True)
    agent._memory.as_coalition_async.assert_not_called()
    agent._dmn.wander.assert_not_called()
    assert all(c.source != "memory" for c in result.coalitions)


@pytest.mark.asyncio
async def test_full_cycle_uses_memory_recall():
    from unittest.mock import AsyncMock

    agent = _make_agent()
    agent._memory.as_coalition_async = AsyncMock(return_value=None)
    await agent._compete_once(cheap=False)
    agent._memory.as_coalition_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_dmn_fallback_promotes_winner_when_nothing_ignites():
    from unittest.mock import AsyncMock

    agent = _make_agent()
    agent._memory.as_coalition_async = AsyncMock(return_value=None)
    # Force the competition to find no winner so the DMN fallback runs. An
    # extra coalition keeps the list non-empty (else _compete_once early-returns).
    agent._workspace.compete = lambda coalitions: None
    agent._dmn = type("D", (), {"wander": AsyncMock(return_value=_coalition(source="dmn"))})()

    result = await agent._compete_once(cheap=False, extra_coalitions=[_coalition(source="desire")])
    agent._dmn.wander.assert_awaited_once()
    assert result.winner is not None and result.winner.source == "dmn"
    assert result.winner in result.coalitions
    assert result.winner not in result.others


@pytest.mark.asyncio
async def test_cheap_cycle_never_calls_dmn_even_with_no_winner():
    from unittest.mock import AsyncMock

    agent = _make_agent()
    agent._workspace.compete = lambda coalitions: None
    agent._dmn = type("D", (), {"wander": AsyncMock(return_value=_coalition(source="dmn"))})()

    result = await agent._compete_once(cheap=True)
    agent._dmn.wander.assert_not_called()
    assert result.winner is None


@pytest.mark.asyncio
async def test_gather_workspace_context_still_returns_string():
    """The turn path wrapper must keep returning a broadcast string (or '')."""
    agent = _make_agent()
    out = await agent._gather_workspace_context()
    assert isinstance(out, str)


# ── config / construction ──


def test_inner_loop_off_by_default(monkeypatch):
    monkeypatch.delenv("FAMILIAR_INNER_LOOP", raising=False)
    from familiar_agent.config import AgentConfig

    assert AgentConfig().inner_loop is False


def test_inner_loop_env_enables(monkeypatch):
    monkeypatch.setenv("FAMILIAR_INNER_LOOP", "1")
    from familiar_agent.config import AgentConfig

    assert AgentConfig().inner_loop is True


# ── the live tick (Phase 2 PR2) ──


def _tick_result(winner):
    from familiar_agent.inner_loop import CompeteResult

    return CompeteResult(winner=winner, others=[], coalitions=[winner] if winner else [])


@pytest.mark.asyncio
async def test_tick_skips_while_turn_active():
    from unittest.mock import AsyncMock

    agent = _make_agent()
    agent._compete_once = AsyncMock()
    agent._turn_active = True
    await agent._inner_loop_tick()
    agent._compete_once.assert_not_called()


@pytest.mark.asyncio
async def test_tick_feeds_train_of_thought_and_crystallizes_monologue():
    from unittest.mock import AsyncMock

    agent = _make_agent()
    winner = _coalition(source="narrative", activation=0.7, urgency=0.3)
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    await agent._inner_loop_tick()
    assert agent._train_of_thought.streak == 1
    assert len(agent._inner_monologue) == 0  # one win does not crystallize

    await agent._inner_loop_tick()
    assert agent._train_of_thought.streak == 2
    assert len(agent._inner_monologue) == 1  # second consecutive win does
    thought = agent._inner_monologue[0]
    assert thought.source == "narrative"
    assert thought.summary == winner.summary


@pytest.mark.asyncio
async def test_tick_alternates_cheap_and_full_cycles():
    from unittest.mock import AsyncMock

    agent = _make_agent()
    agent._inner_loop_config.full_cycle_every = 3
    agent._compete_once = AsyncMock(return_value=_tick_result(None))

    for _ in range(6):
        await agent._inner_loop_tick()

    cheap_flags = [call.kwargs["cheap"] for call in agent._compete_once.call_args_list]
    # Ticks 1,2 cheap; tick 3 full; ticks 4,5 cheap; tick 6 full.
    assert cheap_flags == [True, True, False, True, True, False]


@pytest.mark.asyncio
async def test_tick_reinjects_train_of_thought_recurrence():
    from unittest.mock import AsyncMock

    agent = _make_agent()
    winner = _coalition(source="curiosity", activation=0.9)
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    await agent._inner_loop_tick()  # first win seeds the train
    await agent._inner_loop_tick()  # second tick must re-inject it

    second_call = agent._compete_once.call_args_list[1]
    extra = second_call.kwargs["extra_coalitions"]
    assert len(extra) == 1
    assert extra[0].source == "train_of_thought"


@pytest.mark.asyncio
async def test_sustained_salient_focus_escalates_to_drive_boost():
    from unittest.mock import AsyncMock, MagicMock

    agent = _make_agent()
    desires = MagicMock()
    agent.bind_desires(desires)
    # identity focus: activation 0.8 + urgency 0.8 = 1.6 >= salience bar
    winner = _coalition(source="identity", activation=0.8, urgency=0.8)
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    await agent._inner_loop_tick()
    await agent._inner_loop_tick()
    desires.boost.assert_not_called()  # streak 2 < min streak 3

    await agent._inner_loop_tick()
    desires.boost.assert_called_once()
    args, _ = desires.boost.call_args
    assert args[0] == "identity_coherence"
    # Escalation resets the train so the focus is not re-pumped.
    assert agent._train_of_thought.last is None


@pytest.mark.asyncio
async def test_weak_focus_never_escalates():
    from unittest.mock import AsyncMock, MagicMock

    agent = _make_agent()
    desires = MagicMock()
    agent.bind_desires(desires)
    # Sustained but low-salience: 0.5 + 0.3 = 0.8 < 1.0 bar.
    winner = _coalition(source="narrative", activation=0.5, urgency=0.3)
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    for _ in range(5):
        await agent._inner_loop_tick()
    desires.boost.assert_not_called()


@pytest.mark.asyncio
async def test_desire_source_never_escalates():
    """Dominant desires fire natively through the UI idle chain — no boost."""
    from unittest.mock import AsyncMock, MagicMock

    agent = _make_agent()
    desires = MagicMock()
    agent.bind_desires(desires)
    winner = _coalition(source="desire", activation=0.9, urgency=0.9)
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    for _ in range(5):
        await agent._inner_loop_tick()
    desires.boost.assert_not_called()


@pytest.mark.asyncio
async def test_escalation_respects_per_source_cooldown():
    from unittest.mock import AsyncMock, MagicMock

    agent = _make_agent()
    desires = MagicMock()
    agent.bind_desires(desires)
    winner = _coalition(source="identity", activation=0.8, urgency=0.8)
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    for _ in range(3):
        await agent._inner_loop_tick()
    assert desires.boost.call_count == 1

    # The train was reset; even after rebuilding the streak, the per-source
    # cooldown blocks a second boost.
    for _ in range(4):
        await agent._inner_loop_tick()
    assert desires.boost.call_count == 1


@pytest.mark.asyncio
async def test_tick_never_calls_run():
    """The tick escalates via drives only — it must never start a turn."""
    from unittest.mock import AsyncMock, MagicMock

    agent = _make_agent()
    agent.run = AsyncMock()
    agent.bind_desires(MagicMock())
    winner = _coalition(source="identity", activation=0.9, urgency=0.9)
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    for _ in range(6):
        await agent._inner_loop_tick()
    agent.run.assert_not_called()


@pytest.mark.asyncio
async def test_tick_without_desires_still_thinks():
    """Before bind_desires (or in bare embeddings), the tick still cycles."""
    from unittest.mock import AsyncMock

    agent = _make_agent()
    assert agent._desires is None
    winner = _coalition(source="identity", activation=0.9, urgency=0.9)
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    for _ in range(4):
        await agent._inner_loop_tick()  # must not raise
    assert agent._train_of_thought.streak >= 1


# ── lazy start via prepare_turn ──


@pytest.mark.asyncio
async def test_prepare_turn_starts_inner_loop_when_enabled():
    from unittest.mock import AsyncMock, MagicMock

    agent = _make_agent()
    agent.config.inner_loop = True
    inner_loop = MagicMock()
    inner_loop.is_running = False
    inner_loop.start = AsyncMock()
    agent._inner_loop = inner_loop

    from tests.test_agent_react_loop import _patch_heavy, _turn

    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="hi"), "hi"))
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("hi")
    finally:
        for p in ps:
            p.stop()
    inner_loop.start.assert_awaited_once()


@pytest.mark.asyncio
async def test_prepare_turn_leaves_inner_loop_dark_when_disabled():
    from unittest.mock import AsyncMock, MagicMock

    agent = _make_agent()
    agent.config.inner_loop = False
    inner_loop = MagicMock()
    inner_loop.is_running = False
    inner_loop.start = AsyncMock()
    agent._inner_loop = inner_loop

    from tests.test_agent_react_loop import _patch_heavy, _turn

    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="hi"), "hi"))
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("hi")
    finally:
        for p in ps:
            p.stop()
    inner_loop.start.assert_not_called()


# ── turn-active flag lifecycle ──


@pytest.mark.asyncio
async def test_turn_active_set_during_run_and_cleared_after():
    from unittest.mock import AsyncMock

    from tests.test_agent_react_loop import _patch_heavy, _turn

    agent = _make_agent()
    seen: list[bool] = []

    async def _spy_stream_turn(**kwargs):
        seen.append(agent._turn_active)
        return (_turn("end_turn", text="ok"), "ok")

    agent.backend.stream_turn = AsyncMock(side_effect=_spy_stream_turn)
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("hello")
    finally:
        for p in ps:
            p.stop()
    assert seen == [True]
    assert agent._turn_active is False


@pytest.mark.asyncio
async def test_turn_active_cleared_when_prepare_turn_raises():
    from unittest.mock import AsyncMock

    agent = _make_agent()
    agent._hook.prepare_turn = AsyncMock(side_effect=RuntimeError("boom"))
    with pytest.raises(RuntimeError):
        await agent.run("hello")
    assert agent._turn_active is False
