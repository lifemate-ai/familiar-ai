"""Tests for RelationshipTracker (Phase 6 — relationship modeling).

Tracks first session, session count, conversation count, and surfaces
context for the system prompt.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from familiar_agent.relationship import RelationshipTracker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _tracker(tmp_path: Path) -> RelationshipTracker:
    return RelationshipTracker(state_path=tmp_path / "relationship.json")


# ---------------------------------------------------------------------------
# Tests: initial state
# ---------------------------------------------------------------------------


def test_fresh_tracker_has_zero_sessions(tmp_path) -> None:
    t = _tracker(tmp_path)
    assert t.session_count == 0


def test_fresh_tracker_has_zero_conversations(tmp_path) -> None:
    t = _tracker(tmp_path)
    assert t.conversation_count == 0


def test_fresh_tracker_has_no_first_session_date(tmp_path) -> None:
    t = _tracker(tmp_path)
    assert t.first_session_date is None


# ---------------------------------------------------------------------------
# Tests: record_session
# ---------------------------------------------------------------------------


def test_record_session_increments_count(tmp_path) -> None:
    t = _tracker(tmp_path)
    t.record_session()
    assert t.session_count == 1


def test_record_session_twice_increments_to_two(tmp_path) -> None:
    t = _tracker(tmp_path)
    t.record_session()
    t.record_session()
    assert t.session_count == 2


def test_record_session_sets_first_session_date_on_first_call(tmp_path) -> None:
    t = _tracker(tmp_path)
    t.record_session()
    assert t.first_session_date is not None


def test_record_session_does_not_overwrite_first_session_date(tmp_path) -> None:
    t = _tracker(tmp_path)
    t.record_session()
    first = t.first_session_date
    t.record_session()
    assert t.first_session_date == first


def test_record_session_updates_last_session_date(tmp_path) -> None:
    t = _tracker(tmp_path)
    t.record_session()
    assert t.last_session_date is not None


# ---------------------------------------------------------------------------
# Tests: record_conversation
# ---------------------------------------------------------------------------


def test_record_conversation_increments_count(tmp_path) -> None:
    t = _tracker(tmp_path)
    t.record_conversation()
    assert t.conversation_count == 1


def test_record_conversation_multiple_times(tmp_path) -> None:
    t = _tracker(tmp_path)
    for _ in range(5):
        t.record_conversation()
    assert t.conversation_count == 5


# ---------------------------------------------------------------------------
# Tests: days_together
# ---------------------------------------------------------------------------


def test_days_together_none_when_no_first_session(tmp_path) -> None:
    t = _tracker(tmp_path)
    assert t.days_together is None


def test_days_together_zero_on_first_day(tmp_path) -> None:
    t = _tracker(tmp_path)
    t.record_session()
    assert t.days_together == 0


def test_days_together_correct_after_backdating(tmp_path) -> None:
    t = _tracker(tmp_path)
    t.record_session()
    # Backdate first_session_date by 7 days
    t._state["first_session_date"] = (date.today() - timedelta(days=7)).isoformat()
    t._save()
    assert t.days_together == 7


# ---------------------------------------------------------------------------
# Tests: persistence across instances
# ---------------------------------------------------------------------------


def test_state_persists_across_instances(tmp_path) -> None:
    t1 = _tracker(tmp_path)
    t1.record_session()
    t1.record_conversation()
    t1.record_conversation()

    t2 = _tracker(tmp_path)
    assert t2.session_count == 1
    assert t2.conversation_count == 2


# ---------------------------------------------------------------------------
# Tests: context_for_prompt
# ---------------------------------------------------------------------------


def test_context_for_prompt_returns_string(tmp_path) -> None:
    t = _tracker(tmp_path)
    t.record_session()
    t.record_conversation()
    result = t.context_for_prompt()
    assert isinstance(result, str)
    assert len(result) > 0


def test_context_for_prompt_empty_before_first_session(tmp_path) -> None:
    t = _tracker(tmp_path)
    result = t.context_for_prompt()
    # No session yet — should return empty string or None
    assert result == "" or result is None


def test_context_for_prompt_includes_session_info(tmp_path) -> None:
    t = _tracker(tmp_path)
    t.record_session()
    for _ in range(3):
        t.record_conversation()
    result = t.context_for_prompt()
    # Should mention sessions or conversations somewhere
    assert (
        "session" in result.lower() or "conversation" in result.lower() or "talk" in result.lower()
    )
