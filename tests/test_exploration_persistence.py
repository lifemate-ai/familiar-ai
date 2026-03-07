"""Tests for ExplorationTracker persistence (Phase 1-3).

TDD: written before persistence is implemented in exploration.py.
Uses in-memory SQLite to avoid touching the real DB.
"""

from __future__ import annotations

import sqlite3

import pytest

from familiar_agent.exploration import ExplorationTracker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _in_memory_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    ExplorationTracker.init_schema(conn)
    return conn


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_init_schema_creates_table():
    """ExplorationTracker.init_schema() creates exploration_state table."""
    conn = sqlite3.connect(":memory:")
    ExplorationTracker.init_schema(conn)

    tables = {
        r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    assert "exploration_state" in tables


def test_save_and_load_pan_tilt():
    """save_to_db() persists pan/tilt accumulators; load_from_db() restores them."""
    conn = _in_memory_conn()
    tracker = ExplorationTracker()

    tracker.record_move("left", 45)
    tracker.record_move("up", 30)
    tracker.save_to_db(conn)

    restored = ExplorationTracker()
    restored.load_from_db(conn)

    assert abs(restored._pan_accum - tracker._pan_accum) < 1e-6
    assert abs(restored._tilt_accum - tracker._tilt_accum) < 1e-6


def test_load_from_empty_db_is_zero():
    """load_from_db() on empty DB leaves accumulators at 0."""
    conn = _in_memory_conn()
    tracker = ExplorationTracker()
    tracker.load_from_db(conn)

    assert tracker._pan_accum == 0.0
    assert tracker._tilt_accum == 0.0


def test_save_and_load_records():
    """Records list is serialized and restored correctly."""
    conn = _in_memory_conn()
    tracker = ExplorationTracker()

    tracker.record_move("right", 60)
    tracker.record_move("down", 20)
    tracker.save_to_db(conn)

    restored = ExplorationTracker()
    restored.load_from_db(conn)

    assert len(restored._records) == len(tracker._records)
    assert restored._records[0].direction_label == "right"
    assert restored._records[1].direction_label == "down"


def test_save_overwrites_previous_state():
    """Second save_to_db() replaces the first (upsert semantics)."""
    conn = _in_memory_conn()
    tracker = ExplorationTracker()

    tracker.record_move("left", 30)
    tracker.save_to_db(conn)

    tracker.record_move("right", 30)
    tracker.save_to_db(conn)

    restored = ExplorationTracker()
    restored.load_from_db(conn)

    row_count = conn.execute("SELECT COUNT(*) FROM exploration_state").fetchone()[0]
    assert row_count == 1
    assert len(restored._records) == 2


def test_novelty_values_survive_round_trip():
    """Novelty scores attached to records are preserved after save/load."""
    conn = _in_memory_conn()
    tracker = ExplorationTracker()

    tracker.record_move("up", 30)
    tracker.record_novelty(0.75)
    tracker.save_to_db(conn)

    restored = ExplorationTracker()
    restored.load_from_db(conn)

    assert restored._records[0].novelty == pytest.approx(0.75)
