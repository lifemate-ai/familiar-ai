"""Tests for temporal / anniversary awareness.

Phase 4 of companion-likeness Round 2.
The agent knows "on this day" events and milestones, surfacing them in morning reconstruction.
"""

from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from familiar_agent.tools.memory import ObservationMemory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _memory_with_rows(rows: list[dict]) -> ObservationMemory:
    """ObservationMemory backed by an in-memory DB seeded with rows."""
    import threading

    mem = ObservationMemory.__new__(ObservationMemory)
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE observations (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            direction TEXT NOT NULL DEFAULT 'unknown',
            kind TEXT NOT NULL DEFAULT 'observation',
            emotion TEXT NOT NULL DEFAULT 'neutral',
            image_path TEXT,
            image_data TEXT,
            importance REAL NOT NULL DEFAULT 1.0,
            superseded_by TEXT
        )"""
    )
    for i, row in enumerate(rows):
        conn.execute(
            "INSERT INTO observations (id, content, timestamp, date, time, kind, emotion) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                str(i),
                row["content"],
                row.get("timestamp", f"{row['date']}T12:00:00"),
                row["date"],
                row.get("time", "12:00"),
                row.get("kind", "conversation"),
                row.get("emotion", "neutral"),
            ),
        )
    conn.commit()
    mem._db = conn
    mem._db_lock = threading.Lock()
    return mem


def _today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def _last_year_same_day() -> str:
    today = date.today()
    try:
        return today.replace(year=today.year - 1).strftime("%Y-%m-%d")
    except ValueError:
        # Feb 29 edge case
        return (today - timedelta(days=365)).strftime("%Y-%m-%d")


def _weeks_ago(n: int) -> str:
    return (date.today() - timedelta(weeks=n)).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Tests: recall_on_this_day / recall_on_this_day_async
# ---------------------------------------------------------------------------


def test_recall_on_this_day_returns_matching_month_day() -> None:
    anniversary_date = _last_year_same_day()
    mem = _memory_with_rows(
        [
            {"content": "カメラを設置した日", "date": anniversary_date},
            {"content": "全然関係ない日", "date": _weeks_ago(4)},
        ]
    )
    today = date.today()
    results = mem.recall_on_this_day(today.month, today.day)
    assert len(results) == 1
    assert "カメラを設置した日" in results[0]["content"]


def test_recall_on_this_day_excludes_today() -> None:
    """Today's memories should NOT appear — only past years."""
    mem = _memory_with_rows(
        [
            {"content": "今日の記憶", "date": _today_str()},
        ]
    )
    today = date.today()
    results = mem.recall_on_this_day(today.month, today.day)
    assert len(results) == 0


def test_recall_on_this_day_empty_db_returns_empty() -> None:
    mem = _memory_with_rows([])
    today = date.today()
    results = mem.recall_on_this_day(today.month, today.day)
    assert results == []


def test_recall_on_this_day_respects_n_limit() -> None:
    anniversary_date = _last_year_same_day()
    mem = _memory_with_rows([{"content": f"記憶{i}", "date": anniversary_date} for i in range(5)])
    today = date.today()
    results = mem.recall_on_this_day(today.month, today.day, n=2)
    assert len(results) <= 2


@pytest.mark.asyncio
async def test_recall_on_this_day_async_works() -> None:
    anniversary_date = _last_year_same_day()
    mem = _memory_with_rows(
        [
            {"content": "去年の今日", "date": anniversary_date},
        ]
    )
    today = date.today()
    results = await mem.recall_on_this_day_async(today.month, today.day)
    assert len(results) == 1


# ---------------------------------------------------------------------------
# Tests: get_earliest_date / get_earliest_date_async
# ---------------------------------------------------------------------------


def test_get_earliest_date_returns_min_date() -> None:
    mem = _memory_with_rows(
        [
            {"content": "新しい記憶", "date": _weeks_ago(1)},
            {"content": "古い記憶", "date": _weeks_ago(10)},
        ]
    )
    result = mem.get_earliest_date()
    assert result == _weeks_ago(10)


def test_get_earliest_date_empty_db_returns_none() -> None:
    mem = _memory_with_rows([])
    result = mem.get_earliest_date()
    assert result is None


@pytest.mark.asyncio
async def test_get_earliest_date_async_works() -> None:
    mem = _memory_with_rows(
        [
            {"content": "古い記憶", "date": _weeks_ago(5)},
        ]
    )
    result = await mem.get_earliest_date_async()
    assert result == _weeks_ago(5)


# ---------------------------------------------------------------------------
# Tests: _anniversary_context in EmbodiedAgent
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_anniversary_context_returns_string_when_anniversary_exists() -> None:
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._memory = MagicMock()
    anniversary_date = _last_year_same_day()
    agent._memory.recall_on_this_day_async = AsyncMock(
        return_value=[{"content": "去年の今日はカメラを設置した", "date": anniversary_date}]
    )
    agent._memory.get_earliest_date_async = AsyncMock(return_value=_weeks_ago(30))

    result = await agent._anniversary_context()
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_anniversary_context_includes_milestone_at_7_days() -> None:
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._memory = MagicMock()
    agent._memory.recall_on_this_day_async = AsyncMock(return_value=[])
    agent._memory.get_earliest_date_async = AsyncMock(return_value=_weeks_ago(1))  # 7 days

    result = await agent._anniversary_context()
    # 7 days milestone should produce output
    assert result is not None


@pytest.mark.asyncio
async def test_anniversary_context_returns_none_when_nothing_notable() -> None:
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._memory = MagicMock()
    agent._memory.recall_on_this_day_async = AsyncMock(return_value=[])
    agent._memory.get_earliest_date_async = AsyncMock(
        return_value=_weeks_ago(3)
    )  # 21 days, no milestone

    result = await agent._anniversary_context()
    # No anniversary, 21 days is divisible by 7 → milestone!
    # Actually 21 = 3*7, so it IS a milestone. Let's use a non-milestone day.
    # Use 3 days (not divisible by 7, not a round number milestone)
    agent._memory.get_earliest_date_async = AsyncMock(
        return_value=(date.today() - timedelta(days=3)).strftime("%Y-%m-%d")
    )
    result = await agent._anniversary_context()
    assert result is None


@pytest.mark.asyncio
async def test_anniversary_context_no_crash_on_none_earliest_date() -> None:
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._memory = MagicMock()
    agent._memory.recall_on_this_day_async = AsyncMock(return_value=[])
    agent._memory.get_earliest_date_async = AsyncMock(return_value=None)

    result = await agent._anniversary_context()
    assert result is None


@pytest.mark.asyncio
async def test_online_temporal_context_surfaces_resurfaced_memory_and_thread() -> None:
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._turn_count = 3
    agent._self_state = MagicMock()
    agent._self_state.snapshot.return_value = {"unresolved_tension": 0.72}
    agent._proactive_memory_context = AsyncMock(return_value="あの夜に空を探した")
    agent._anniversary_context = AsyncMock(return_value=None)

    desires = MagicMock()
    desires.level = MagicMock(return_value=0.0)
    desires.curiosity_target = "窓の向こうにある空の気配"

    result = await agent._online_temporal_context(desires=desires)

    assert result is not None
    assert "[Resurfaced memory]" in result
    assert "[Unresolved thread]" in result
    assert "空" in result


@pytest.mark.asyncio
async def test_online_temporal_context_skips_first_turn() -> None:
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._turn_count = 1
    agent._self_state = MagicMock()
    agent._self_state.snapshot.return_value = {"unresolved_tension": 0.9}
    agent._proactive_memory_context = AsyncMock(return_value="昔の記憶")
    agent._anniversary_context = AsyncMock(return_value="[Milestone]: 14 days since first memory.")

    desires = MagicMock()
    desires.level = MagicMock(return_value=0.9)
    desires.curiosity_target = "未解決の糸口"

    result = await agent._online_temporal_context(desires=desires)

    assert result is None
    agent._proactive_memory_context.assert_not_awaited()
    agent._anniversary_context.assert_not_awaited()
