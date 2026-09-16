"""Micro-thoughts (Phase 2 PR4) — inner backend role, verbalization,
monologue re-competition, body-modulated cadence.

Cost contract under test throughout: idle cycles never burn main-model calls.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from familiar_agent.inner_loop import InnerThought
from familiar_neighbor.mind.workspace import Coalition

from tests.test_agent_react_loop import _make_agent


def _coalition(source="curiosity", activation=0.8, urgency=0.5, summary="thinking about rain"):
    return Coalition(
        source=source,
        summary=summary,
        activation=activation,
        urgency=urgency,
        novelty=0.3,
        context_block=f"[{source}] {summary}",
    )


def _tick_result(winner):
    from familiar_agent.inner_loop import CompeteResult

    return CompeteResult(winner=winner, others=[], coalitions=[winner] if winner else [])


# ---------------------------------------------------------------------------
# create_inner_backend
# ---------------------------------------------------------------------------


def _config(**env_fields):
    cfg = MagicMock()
    cfg.inner_platform = env_fields.get("inner_platform", "")
    cfg.inner_api_key = env_fields.get("inner_api_key", "")
    cfg.inner_model = env_fields.get("inner_model", "")
    cfg.inner_base_url = env_fields.get("inner_base_url", "")
    return cfg


def test_inner_backend_none_without_platform():
    from familiar_agent.backend import create_inner_backend

    assert create_inner_backend(_config()) is None


def test_inner_backend_openai_local_defaults():
    from familiar_agent.backend import create_inner_backend
    from familiar_runtime.models import OpenAICompatibleBackend

    backend = create_inner_backend(_config(inner_platform="openai", inner_model="gemma3:4b"))
    assert isinstance(backend, OpenAICompatibleBackend)
    assert backend.model == "gemma3:4b"
    assert "localhost:11434" in str(backend.client.base_url)  # local by default
    assert backend.tools_mode == "prompt"


def test_inner_backend_openai_requires_model():
    from familiar_agent.backend import create_inner_backend

    assert create_inner_backend(_config(inner_platform="openai")) is None


def test_inner_backend_cloud_platforms_require_key():
    from familiar_agent.backend import create_inner_backend

    assert create_inner_backend(_config(inner_platform="anthropic")) is None
    assert create_inner_backend(_config(inner_platform="nonsense", inner_api_key="k")) is None


def test_config_reads_inner_env(monkeypatch):
    monkeypatch.setenv("INNER_PLATFORM", "openai")
    monkeypatch.setenv("INNER_MODEL", "qwen3:4b")
    monkeypatch.setenv("INNER_BASE_URL", "http://box:11434/v1")
    from familiar_agent.config import AgentConfig

    cfg = AgentConfig()
    assert cfg.inner_platform == "openai"
    assert cfg.inner_model == "qwen3:4b"
    assert cfg.inner_base_url == "http://box:11434/v1"


# ---------------------------------------------------------------------------
# Micro-thought verbalization in the tick
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_crystallization_uses_verbalized_thought():
    agent = _make_agent()
    agent._inner_backend = MagicMock()
    agent._inner_backend.complete = AsyncMock(return_value="the rain sounds like static today")
    winner = _coalition(source="narrative")
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    await agent._inner_loop_tick()
    await agent._inner_loop_tick()  # streak 2 → crystallize + verbalize

    assert len(agent._inner_monologue) == 1
    assert agent._inner_monologue[0].summary == "the rain sounds like static today"
    agent._inner_backend.complete.assert_awaited_once()
    # Reasoning-model-aware budget floor.
    assert agent._inner_backend.complete.call_args.kwargs["max_tokens"] >= 256


@pytest.mark.asyncio
async def test_micro_thought_rate_limited_and_degrades_to_summary():
    agent = _make_agent()
    agent._inner_backend = MagicMock()
    agent._inner_backend.complete = AsyncMock(return_value="a verbal thought")
    winner = _coalition(source="narrative", summary="raw focus summary")
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    for _ in range(4):  # crystallizes on ticks 2,3,4 — but only one LLM call
        await agent._inner_loop_tick()

    assert agent._inner_backend.complete.await_count == 1
    summaries = [t.summary for t in agent._inner_monologue]
    assert summaries[0] == "a verbal thought"
    assert all(s == "raw focus summary" for s in summaries[1:])  # rate-limited → raw


@pytest.mark.asyncio
async def test_no_backend_keeps_subverbal_monologue():
    agent = _make_agent()
    assert agent._inner_backend is None
    winner = _coalition(source="narrative", summary="quiet focus")
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    await agent._inner_loop_tick()
    await agent._inner_loop_tick()
    assert agent._inner_monologue[0].summary == "quiet focus"


@pytest.mark.asyncio
async def test_backend_failure_or_empty_degrades():
    agent = _make_agent()
    agent._inner_backend = MagicMock()
    agent._inner_backend.complete = AsyncMock(side_effect=RuntimeError("model gone"))
    winner = _coalition(source="narrative", summary="fallback me")
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    await agent._inner_loop_tick()
    await agent._inner_loop_tick()
    assert agent._inner_monologue[0].summary == "fallback me"


@pytest.mark.asyncio
async def test_recurrence_sources_never_crystallize():
    """The monologue echoing itself back into itself is a feedback loop."""
    agent = _make_agent()
    winner = _coalition(source="monologue", summary="echo")
    agent._compete_once = AsyncMock(return_value=_tick_result(winner))

    for _ in range(4):
        await agent._inner_loop_tick()
    assert len(agent._inner_monologue) == 0


def test_inner_backend_defaults_to_none_when_utility_is_main():
    """Cost contract: without INNER_* and without a separate utility backend,
    micro-thoughts stay off — idle cycles never touch the main model."""
    agent = _make_agent()
    # _make_agent sets _utility_backend = backend (same object) → tape None.
    assert agent._tape_backend() is None


# ---------------------------------------------------------------------------
# Monologue re-competition
# ---------------------------------------------------------------------------


def test_monologue_coalition_renders_fresh_thoughts():
    agent = _make_agent()
    now = time.time()
    agent._inner_monologue.append(
        InnerThought(summary="rain again", source="scene", ts=now - 60, score=0.6)
    )
    agent._inner_monologue.append(
        InnerThought(summary="he seemed tired", source="tom", ts=now - 10, score=0.7)
    )
    coalition = agent._inner_monologue_coalition()
    assert coalition is not None
    assert coalition.source == "monologue"
    assert "rain again" in coalition.context_block
    assert "he seemed tired" in coalition.context_block


def test_monologue_coalition_fades_out_when_stale():
    agent = _make_agent()
    agent._inner_monologue.append(
        InnerThought(summary="old musing", source="scene", ts=time.time() - 7200, score=0.6)
    )
    assert agent._inner_monologue_coalition() is None
    agent._inner_monologue.clear()
    assert agent._inner_monologue_coalition() is None


@pytest.mark.asyncio
async def test_monologue_competes_in_workspace():
    agent = _make_agent()
    agent._inner_monologue.append(
        InnerThought(summary="fresh idle thought", source="scene", ts=time.time(), score=0.9)
    )
    result = await agent._compete_once(cheap=True)
    assert any(c.source == "monologue" for c in result.coalitions)


# ---------------------------------------------------------------------------
# Body-modulated cadence
# ---------------------------------------------------------------------------


def _signal(energy: float):
    signal = MagicMock()
    signal.energy = energy
    return signal


def test_cadence_quickens_with_energy_and_clamps():
    agent = _make_agent()
    agent.config.inner_loop_interval = 20.0

    agent._collect_interoception = MagicMock(return_value=(_signal(1.0), None))
    agent._modulate_inner_cadence()
    lively = agent._inner_loop_config.interval_sec

    agent._collect_interoception = MagicMock(return_value=(_signal(0.0), None))
    agent._modulate_inner_cadence()
    tired = agent._inner_loop_config.interval_sec

    assert lively < 20.0 < tired
    assert 5.0 <= lively and tired <= 120.0

    # Clamping at the extremes.
    agent.config.inner_loop_interval = 2.0
    agent._collect_interoception = MagicMock(return_value=(_signal(1.0), None))
    agent._modulate_inner_cadence()
    assert agent._inner_loop_config.interval_sec == 5.0


def test_cadence_failure_leaves_interval_untouched():
    agent = _make_agent()
    agent._inner_loop_config.interval_sec = 20.0
    agent._collect_interoception = MagicMock(side_effect=RuntimeError("no body"))
    agent._modulate_inner_cadence()
    assert agent._inner_loop_config.interval_sec == 20.0
