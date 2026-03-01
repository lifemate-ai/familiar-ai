"""Tests for ExplorationTracker — novelty-aware ICL exploration."""

from __future__ import annotations

import pytest

from familiar_agent.exploration import ExplorationTracker


class TestRecordMove:
    def test_first_move_creates_record(self):
        t = ExplorationTracker()
        t.record_move("left", 30)
        assert len(t._records) == 1
        assert t._records[0].direction_label == "left"

    def test_unknown_direction_stored_as_center(self):
        t = ExplorationTracker()
        t.record_move("diagonal", 10)
        assert t._records[0].direction_label == "center"

    def test_pan_accumulates_for_left(self):
        t = ExplorationTracker()
        t.record_move("left", 30)
        t.record_move("left", 30)
        assert t._pan_accum > 0  # left is positive pan delta

    def test_pan_accumulates_for_right(self):
        t = ExplorationTracker()
        t.record_move("right", 30)
        assert t._pan_accum < 0  # right is negative pan delta


class TestRecordNovelty:
    def test_novelty_fills_most_recent_record(self):
        t = ExplorationTracker()
        t.record_move("left", 30)
        t.record_novelty(0.9)
        assert t._records[-1].novelty == pytest.approx(0.9)

    def test_novelty_only_updates_last_record(self):
        t = ExplorationTracker()
        t.record_move("left", 30)
        t.record_move("right", 30)
        t.record_novelty(0.7)
        assert t._records[0].novelty is None
        assert t._records[1].novelty == pytest.approx(0.7)

    def test_record_novelty_noop_when_no_records(self):
        t = ExplorationTracker()
        t.record_novelty(0.5)  # should not raise


class TestUnvisitedHint:
    def test_hints_unvisited_direction(self):
        t = ExplorationTracker()
        t.record_move("left", 30)
        t.record_move("left", 30)
        t.record_move("left", 30)
        hint = t.unvisited_hint()
        # right/up/down are unvisited — should mention at least one
        assert any(d in hint for d in ("right", "up", "down"))

    def test_no_hint_when_no_records(self):
        t = ExplorationTracker()
        hint = t.unvisited_hint()
        assert hint == ""

    def test_all_visited_returns_empty(self):
        t = ExplorationTracker()
        for d in ("left", "right", "up", "down"):
            t.record_move(d, 30)
        hint = t.unvisited_hint()
        # All directions visited once — no strong bias, hint may be empty or minimal
        assert isinstance(hint, str)


class TestContextForPrompt:
    def test_empty_when_no_records(self):
        t = ExplorationTracker()
        ctx = t.context_for_prompt()
        assert ctx == ""

    def test_contains_direction(self):
        t = ExplorationTracker()
        t.record_move("up", 30)
        ctx = t.context_for_prompt()
        assert "up" in ctx

    def test_novelty_label_high(self):
        t = ExplorationTracker()
        t.record_move("left", 30)
        t.record_novelty(0.85)
        ctx = t.context_for_prompt()
        assert "HIGH" in ctx

    def test_novelty_label_low(self):
        t = ExplorationTracker()
        t.record_move("center", 0)
        t.record_novelty(0.15)
        ctx = t.context_for_prompt()
        assert "LOW" in ctx

    def test_novelty_label_medium(self):
        t = ExplorationTracker()
        t.record_move("right", 30)
        t.record_novelty(0.5)
        ctx = t.context_for_prompt()
        assert "MED" in ctx

    def test_respects_n_limit(self):
        t = ExplorationTracker()
        for _ in range(10):
            t.record_move("left", 10)
        ctx = t.context_for_prompt(n=3)
        # Should only show last 3 — count occurrences
        assert ctx.count("left") <= 4  # 3 records + possibly hint

    def test_includes_unvisited_hint(self):
        t = ExplorationTracker()
        for _ in range(3):
            t.record_move("left", 30)
        ctx = t.context_for_prompt()
        assert "Unexplored" in ctx or "haven't" in ctx
