"""Inner-loop scaffolding (Phase 2 PR1): driver + cheap-cycle seam.

PR1 only lands the dark scaffolding: the InnerLoop driver (cadence/lifecycle),
the TrainOfThought/InnerThought dataclasses, and the _compete_once extraction
that makes _gather_workspace_context a thin wrapper. Nothing runs yet — the
tick is a no-op stub and the loop is never started.
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


@pytest.mark.asyncio
async def test_stub_tick_is_noop():
    agent = _make_agent()
    assert await agent._inner_loop_tick() is None
