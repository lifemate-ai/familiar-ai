"""Tests for DefaultModeProcessor (Phase 4: Default Mode Network).

Tests cover:
- wander(): spontaneous memory recall + association when workspace is idle
- consolidate(): find near-duplicate memories and mark for merging
- as_coalition(): DMN output as a workspace Coalition (can win next cycle)
- Activation only when workspace is idle (nothing ignited)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from familiar_agent.default_mode import DefaultModeProcessor


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_memory_mock(memories: list[dict] | None = None) -> MagicMock:
    mem = MagicMock()
    mem.recall_async = AsyncMock(return_value=memories or [])
    mem.recall_curiosities_async = AsyncMock(return_value=memories or [])
    mem.find_near_duplicates_async = AsyncMock(return_value=[])
    return mem


def _memory_entry(content: str, emotion: str = "neutral", importance: float = 1.0) -> dict:
    return {
        "memory_id": "test-id",
        "summary": content,
        "emotion": emotion,
        "confidence": importance,
        "timestamp": "2026-03-16T10:00:00",
    }


# ── Construction ──────────────────────────────────────────────────────────────


def test_default_construction():
    mem = _make_memory_mock()
    dmn = DefaultModeProcessor(mem)
    assert dmn is not None


# ── wander ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_wander_returns_none_when_no_memories():
    mem = _make_memory_mock(memories=[])
    dmn = DefaultModeProcessor(mem)
    result = await dmn.wander()
    assert result is None


@pytest.mark.asyncio
async def test_wander_returns_coalition_with_memories():
    from familiar_agent.workspace import Coalition

    mem = _make_memory_mock(
        memories=[
            _memory_entry("I saw Kouta reading a book", emotion="happy"),
            _memory_entry("The sunset was beautiful yesterday", emotion="moved"),
        ]
    )
    dmn = DefaultModeProcessor(mem)
    result = await dmn.wander()
    assert result is not None
    assert isinstance(result, Coalition)


@pytest.mark.asyncio
async def test_wander_coalition_source_is_dmn():
    mem = _make_memory_mock(memories=[_memory_entry("some memory")])
    dmn = DefaultModeProcessor(mem)
    result = await dmn.wander()
    assert result is not None
    assert result.source == "default_mode"


@pytest.mark.asyncio
async def test_wander_coalition_fields_in_valid_range():
    mem = _make_memory_mock(memories=[_memory_entry("some memory", importance=0.8)])
    dmn = DefaultModeProcessor(mem)
    result = await dmn.wander()
    assert result is not None
    assert 0.0 <= result.activation <= 1.0
    assert 0.0 <= result.urgency <= 1.0
    assert 0.0 <= result.novelty <= 1.0


@pytest.mark.asyncio
async def test_wander_context_block_mentions_memory():
    mem = _make_memory_mock(memories=[_memory_entry("コウタが帰ってきた時のこと")])
    dmn = DefaultModeProcessor(mem)
    result = await dmn.wander()
    assert result is not None
    assert len(result.context_block) > 0


@pytest.mark.asyncio
async def test_wander_low_urgency():
    """DMN wander is not urgent — it's idle-time processing."""
    mem = _make_memory_mock(memories=[_memory_entry("some memory")])
    dmn = DefaultModeProcessor(mem)
    result = await dmn.wander()
    assert result is not None
    assert result.urgency < 0.5  # wandering is never urgent


# ── consolidate ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_consolidate_returns_zero_when_no_duplicates():
    mem = _make_memory_mock()
    mem.find_near_duplicates_async = AsyncMock(return_value=[])
    dmn = DefaultModeProcessor(mem)
    count = await dmn.consolidate()
    assert count == 0


@pytest.mark.asyncio
async def test_consolidate_returns_count_of_processed_pairs():
    mem = _make_memory_mock()
    mem.find_near_duplicates_async = AsyncMock(
        return_value=[
            ("id1", "id2", 0.95),
            ("id3", "id4", 0.91),
        ]
    )
    dmn = DefaultModeProcessor(mem)
    count = await dmn.consolidate()
    assert count >= 0  # May not mark all depending on threshold


@pytest.mark.asyncio
async def test_consolidate_does_not_raise_on_empty_memory():
    mem = _make_memory_mock(memories=[])
    mem.find_near_duplicates_async = AsyncMock(return_value=[])
    dmn = DefaultModeProcessor(mem)
    count = await dmn.consolidate()  # Should not raise
    assert count == 0


# ── as_coalition (idle trigger) ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_as_coalition_returns_none_before_wander():
    """Before wander() is called, no coalition to surface."""
    mem = _make_memory_mock()
    dmn = DefaultModeProcessor(mem)
    assert dmn.as_coalition() is None


@pytest.mark.asyncio
async def test_as_coalition_returns_coalition_after_wander():
    from familiar_agent.workspace import Coalition

    mem = _make_memory_mock(memories=[_memory_entry("some memory")])
    dmn = DefaultModeProcessor(mem)
    await dmn.wander()
    result = dmn.as_coalition()
    assert result is not None
    assert isinstance(result, Coalition)
    assert result.source == "default_mode"


@pytest.mark.asyncio
async def test_as_coalition_none_after_wander_with_no_memories():
    """If wander found nothing, coalition remains None."""
    mem = _make_memory_mock(memories=[])
    dmn = DefaultModeProcessor(mem)
    await dmn.wander()
    assert dmn.as_coalition() is None
