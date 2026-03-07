"""Tests for EmbodiedAgent._morning_reconstruction()."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from familiar_agent.exploration import ExplorationTracker


# ---------------------------------------------------------------------------
# Shared helper — minimal agent without __init__
# ---------------------------------------------------------------------------


def _make_agent():
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent.config = MagicMock()
    agent.config.max_tokens = 1000
    agent.config.agent_name = "Kokone"
    agent.config.companion_name = "Kouta"

    agent._turn_count = 0
    agent._session_input_tokens = 0
    agent._session_output_tokens = 0
    agent._last_context_tokens = 0
    agent._post_compact = False
    agent._started_at = 0.0
    agent.messages = []
    agent._me_md = ""
    agent._exploration = ExplorationTracker()

    backend = MagicMock()
    backend.complete = AsyncMock(return_value="")
    agent.backend = backend
    agent._utility_backend = backend

    mem = MagicMock()
    mem.recall_self_model_async = AsyncMock(return_value=[])
    mem.recall_curiosities_async = AsyncMock(return_value=[])
    mem.recent_feelings_async = AsyncMock(return_value=[])
    mem.recall_day_summaries_async = AsyncMock(return_value=[])
    mem.recall_semantic_facts_async = AsyncMock(return_value=[])
    mem.recall_behavior_policies_async = AsyncMock(return_value=[])
    mem.format_for_context = MagicMock(return_value="")
    mem.format_feelings_for_context = MagicMock(return_value="[feelings]")
    mem.format_day_summaries_for_context = MagicMock(return_value="[day_summaries]")
    mem.format_semantic_facts_for_context = MagicMock(return_value="[semantic_facts]")
    mem.format_behavior_policies_for_context = MagicMock(return_value="[behavior_policies]")
    mem.format_self_model_for_context = MagicMock(return_value="[self_model]")
    mem.format_curiosities_for_context = MagicMock(return_value="[curiosities]")
    mem.save_async = AsyncMock()
    mem.get_dates_with_observations = MagicMock(return_value=[])
    mem.get_dates_with_summaries = MagicMock(return_value=[])
    agent._memory = mem

    return agent


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_morning_calls_all_six_memory_methods():
    """_morning_reconstruction() must call all 6 memory async methods."""
    agent = _make_agent()

    with (
        patch("familiar_agent.agent.EmbodiedAgent._backfill_day_summaries", new=AsyncMock()),
        patch("asyncio.ensure_future"),
    ):
        await agent._morning_reconstruction()

    agent._memory.recall_self_model_async.assert_awaited_once()
    agent._memory.recall_curiosities_async.assert_awaited_once()
    agent._memory.recent_feelings_async.assert_awaited_once()
    agent._memory.recall_day_summaries_async.assert_awaited()
    agent._memory.recall_semantic_facts_async.assert_awaited_once()
    agent._memory.recall_behavior_policies_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_morning_returns_no_history_when_all_empty():
    """With no memories at all, the function returns the no-history placeholder string."""
    agent = _make_agent()

    with (
        patch("familiar_agent.agent.EmbodiedAgent._backfill_day_summaries", new=AsyncMock()),
        patch("asyncio.ensure_future"),
    ):
        result = await agent._morning_reconstruction()

    # Result should be non-empty (no-history placeholder)
    assert result
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_morning_includes_memory_content_in_output():
    """When memories exist, the formatted content appears in the result."""
    agent = _make_agent()
    agent._memory.recall_day_summaries_async = AsyncMock(
        return_value=[{"summary": "yesterday was great"}]
    )

    with (
        patch("familiar_agent.agent.EmbodiedAgent._backfill_day_summaries", new=AsyncMock()),
        patch("asyncio.ensure_future"),
    ):
        result = await agent._morning_reconstruction()

    # format_day_summaries_for_context was called and its output is in the result
    agent._memory.format_day_summaries_for_context.assert_called_once()
    assert "[day_summaries]" in result


@pytest.mark.asyncio
async def test_morning_sets_curiosity_target_on_desires():
    """Surface first curiosity into desires.curiosity_target when it's None."""
    agent = _make_agent()
    agent._memory.recall_curiosities_async = AsyncMock(
        return_value=[{"summary": "black holes"}, {"summary": "language models"}]
    )

    desires = MagicMock()
    desires.curiosity_target = None

    with (
        patch("familiar_agent.agent.EmbodiedAgent._backfill_day_summaries", new=AsyncMock()),
        patch("asyncio.ensure_future"),
    ):
        await agent._morning_reconstruction(desires=desires)

    assert desires.curiosity_target == "black holes"


@pytest.mark.asyncio
async def test_morning_does_not_overwrite_existing_curiosity_target():
    """If desires.curiosity_target is already set, it must NOT be overwritten."""
    agent = _make_agent()
    agent._memory.recall_curiosities_async = AsyncMock(return_value=[{"summary": "new topic"}])

    desires = MagicMock()
    desires.curiosity_target = "existing topic"

    with (
        patch("familiar_agent.agent.EmbodiedAgent._backfill_day_summaries", new=AsyncMock()),
        patch("asyncio.ensure_future"),
    ):
        await agent._morning_reconstruction(desires=desires)

    assert desires.curiosity_target == "existing topic"


@pytest.mark.asyncio
async def test_morning_schedules_backfill_via_ensure_future():
    """_morning_reconstruction() must schedule _backfill_day_summaries via asyncio.ensure_future."""
    agent = _make_agent()

    with (
        patch("familiar_agent.agent.EmbodiedAgent._backfill_day_summaries", new=AsyncMock()),
        patch("familiar_agent.agent.asyncio.ensure_future") as mock_ensure,
    ):
        await agent._morning_reconstruction()

    mock_ensure.assert_called_once()


@pytest.mark.asyncio
async def test_morning_no_desires_arg_is_safe():
    """Passing no desires argument (None) must not raise."""
    agent = _make_agent()

    with (
        patch("familiar_agent.agent.EmbodiedAgent._backfill_day_summaries", new=AsyncMock()),
        patch("asyncio.ensure_future"),
    ):
        result = await agent._morning_reconstruction(desires=None)

    assert isinstance(result, str)
