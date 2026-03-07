"""Tests for proactive memory sharing desire.

Phase 3 of companion-likeness improvements.
New 'share_memory' desire grows over time, triggering contextual "remember when..." prompts.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from familiar_agent.desires import (
    DEFAULT_DESIRES,
    GROWTH_RATES,
    DesireSystem,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _desires(tmp_path: Path) -> DesireSystem:
    return DesireSystem(state_path=tmp_path / "desires.json")


# ---------------------------------------------------------------------------
# Tests: share_memory desire exists and grows
# ---------------------------------------------------------------------------


def test_share_memory_in_default_desires() -> None:
    assert "share_memory" in DEFAULT_DESIRES


def test_share_memory_in_growth_rates() -> None:
    assert "share_memory" in GROWTH_RATES


def test_share_memory_growth_rate_positive() -> None:
    assert GROWTH_RATES["share_memory"] > 0.0


def test_share_memory_grows_with_tick(tmp_path) -> None:
    desires = _desires(tmp_path)
    initial = desires.level("share_memory")
    # Simulate time passing by manipulating _last_tick
    desires._last_tick -= 300  # 5 minutes
    desires.tick()
    assert desires.level("share_memory") > initial


def test_share_memory_satisfies_and_decays(tmp_path) -> None:
    desires = _desires(tmp_path)
    desires.boost("share_memory", 0.8)
    before = desires.level("share_memory")
    desires.satisfy("share_memory")
    assert desires.level("share_memory") < before


def test_share_memory_has_prompt_in_dominant(tmp_path) -> None:
    """When share_memory is dominant, dominant_as_prompt returns a string."""
    desires = _desires(tmp_path)
    desires.boost("share_memory", 1.0)
    # Suppress other desires so share_memory is clearly dominant
    for name in ("look_around", "explore", "greet_companion", "rest", "worry_companion"):
        desires._desires[name] = 0.0
    prompt = desires.dominant_as_prompt()
    assert prompt is not None
    assert len(prompt) > 0


# ---------------------------------------------------------------------------
# Tests: circadian modulation of share_memory
# ---------------------------------------------------------------------------


def test_share_memory_boosted_in_evening() -> None:
    """Evening hours (18-22) should grow share_memory faster."""
    modulation = DesireSystem._time_modulation(20)  # 8pm
    rate = modulation.get("share_memory", 1.0)
    assert rate > 1.0


def test_share_memory_suppressed_at_night() -> None:
    """Night hours (22-6) should suppress share_memory (old memories feel heavy)."""
    modulation = DesireSystem._time_modulation(2)  # 2am
    rate = modulation.get("share_memory", 1.0)
    assert rate < 1.0


def test_share_memory_default_modulation_daytime() -> None:
    """Daytime modulation (10-18) should not penalize share_memory excessively."""
    modulation = DesireSystem._time_modulation(14)  # 2pm
    rate = modulation.get("share_memory", 1.0)
    assert rate >= 0.5  # Not heavily suppressed during day


# ---------------------------------------------------------------------------
# Tests: _proactive_memory_context helper in agent
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_proactive_memory_context_returns_string_when_memories_exist() -> None:
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    # Mock memory with some old memories (>24h old)
    old_time = (datetime.now() - timedelta(hours=48)).isoformat()
    agent._memory = MagicMock()
    agent._memory.recall_async = AsyncMock(
        return_value=[
            {"content": "コウタとカメラを設置した", "created_at": old_time, "score": 0.85},
            {"content": "夜景を一緒に見た", "created_at": old_time, "score": 0.70},
        ]
    )

    result = await agent._proactive_memory_context()

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_proactive_memory_context_returns_none_when_empty() -> None:
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._memory = MagicMock()
    agent._memory.recall_async = AsyncMock(return_value=[])

    result = await agent._proactive_memory_context()

    assert result is None


@pytest.mark.asyncio
async def test_proactive_memory_context_filters_recent_memories() -> None:
    """Memories from the last 24h should be filtered out (avoid repeating recent events)."""
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    very_recent = datetime.now().isoformat()  # just now
    agent._memory = MagicMock()
    agent._memory.recall_async = AsyncMock(
        return_value=[
            {"content": "さっきやったこと", "created_at": very_recent, "score": 0.95},
        ]
    )

    result = await agent._proactive_memory_context()

    # All memories are too recent → should return None
    assert result is None


@pytest.mark.asyncio
async def test_proactive_memory_context_no_crash_on_malformed_memories() -> None:
    """Memories with missing/invalid created_at should not crash."""
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._memory = MagicMock()
    agent._memory.recall_async = AsyncMock(
        return_value=[
            {"content": "古い記憶", "score": 0.8},  # no created_at
            {"content": "壊れた記憶", "created_at": "not-a-date", "score": 0.7},
        ]
    )

    # Must not raise
    result = await agent._proactive_memory_context()
    # May return None or a string — both are valid
    assert result is None or isinstance(result, str)
