"""Tests for Phase 2 memory consolidation features.

TDD: written before implementation.
All tests use an isolated ObservationMemory instance with a temp DB.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


from familiar_agent.tools.memory import ObservationMemory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_memory(tmp_path: Path) -> ObservationMemory:
    """Create an ObservationMemory backed by a real temp SQLite DB.

    Forces DB initialization (migrations) immediately so columns are ready.
    """
    db_path = str(tmp_path / "obs_test.db")
    mem = ObservationMemory(db_path=db_path)
    # Trigger lazy initialization and migration immediately
    with mem._db_lock:
        mem._ensure_connected()
    return mem


def _direct_conn(mem: ObservationMemory) -> sqlite3.Connection:
    """Open a direct SQLite connection to the same DB for inspection."""
    return sqlite3.connect(mem._db_path)


def _insert_observation(
    mem: ObservationMemory,
    content: str,
    kind: str = "observation",
    emotion: str = "neutral",
    importance: float = 1.0,
) -> str:
    """Synchronously insert a bare observation row for testing."""
    import uuid
    from datetime import datetime

    obs_id = str(uuid.uuid4())
    now = datetime.now()
    with mem._db_lock:
        db = mem._ensure_connected()
        db.execute(
            """
            INSERT INTO observations
                (id, content, timestamp, date, time, direction, kind, emotion, importance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                obs_id,
                content,
                now.isoformat(),
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M"),
                "test",
                kind,
                emotion,
                importance,
            ),
        )
        db.commit()
    return obs_id


# ---------------------------------------------------------------------------
# Tests: Phase 2-2 — importance column
# ---------------------------------------------------------------------------


def test_observations_has_importance_column(tmp_path):
    """observations table must have an importance column with default 1.0."""
    mem = _make_memory(tmp_path)
    conn = _direct_conn(mem)
    pragma = conn.execute("PRAGMA table_info(observations)").fetchall()
    col_names = {r[1] for r in pragma}
    assert "importance" in col_names


def test_importance_defaults_to_one(tmp_path):
    """Inserted observation without explicit importance gets 1.0."""
    mem = _make_memory(tmp_path)
    obs_id = _insert_observation(mem, "default importance check")
    conn = _direct_conn(mem)
    row = conn.execute("SELECT importance FROM observations WHERE id=?", (obs_id,)).fetchone()
    assert row is not None
    assert abs(row[0] - 1.0) < 1e-6


def test_decay_importance_reduces_old_records(tmp_path):
    """decay_importance() multiplies importance by factor for records before cutoff date."""
    mem = _make_memory(tmp_path)
    obs_id = _insert_observation(mem, "old memory", importance=1.0)
    # Force its date to the past
    conn = _direct_conn(mem)
    conn.execute("UPDATE observations SET date='2025-01-01' WHERE id=?", (obs_id,))
    conn.commit()

    mem.decay_importance(before_date="2026-01-01", factor=0.95)

    row = conn.execute("SELECT importance FROM observations WHERE id=?", (obs_id,)).fetchone()
    assert abs(row[0] - 0.95) < 1e-4


def test_decay_importance_skips_recent_records(tmp_path):
    """decay_importance() leaves records on or after cutoff date unchanged."""
    from datetime import date

    mem = _make_memory(tmp_path)
    today = date.today().isoformat()
    obs_id = _insert_observation(mem, "fresh memory", importance=1.0)
    conn = _direct_conn(mem)
    conn.execute("UPDATE observations SET date=? WHERE id=?", (today, obs_id))
    conn.commit()

    mem.decay_importance(before_date=today, factor=0.95)

    row = conn.execute("SELECT importance FROM observations WHERE id=?", (obs_id,)).fetchone()
    assert abs(row[0] - 1.0) < 1e-6


def test_decay_importance_is_cumulative(tmp_path):
    """Calling decay_importance() twice compounds the factor."""
    mem = _make_memory(tmp_path)
    obs_id = _insert_observation(mem, "old memory", importance=1.0)
    conn = _direct_conn(mem)
    conn.execute("UPDATE observations SET date='2020-01-01' WHERE id=?", (obs_id,))
    conn.commit()

    mem.decay_importance(before_date="2026-01-01", factor=0.9)
    mem.decay_importance(before_date="2026-01-01", factor=0.9)

    row = conn.execute("SELECT importance FROM observations WHERE id=?", (obs_id,)).fetchone()
    assert abs(row[0] - 0.81) < 1e-4  # 0.9 * 0.9 = 0.81


# ---------------------------------------------------------------------------
# Tests: Phase 2-3 — superseded_by column
# ---------------------------------------------------------------------------


def test_observations_has_superseded_by_column(tmp_path):
    """observations table must have a superseded_by column (nullable TEXT)."""
    mem = _make_memory(tmp_path)
    conn = _direct_conn(mem)
    pragma = conn.execute("PRAGMA table_info(observations)").fetchall()
    col_names = {r[1] for r in pragma}
    assert "superseded_by" in col_names


def test_mark_superseded_sets_superseded_by(tmp_path):
    """mark_superseded(old_id, new_id) sets superseded_by on the old record."""
    mem = _make_memory(tmp_path)
    old_id = _insert_observation(mem, "old version of memory")
    new_id = _insert_observation(mem, "updated version of memory")

    mem.mark_superseded(old_id=old_id, new_id=new_id)

    conn = _direct_conn(mem)
    row = conn.execute("SELECT superseded_by FROM observations WHERE id=?", (old_id,)).fetchone()
    assert row[0] == new_id


def test_recall_excludes_superseded_records(tmp_path):
    """recall() must not return observations that have been superseded."""
    mem = _make_memory(tmp_path)
    old_id = _insert_observation(mem, "stale memory about cats")
    new_id = _insert_observation(mem, "updated memory about cats")

    mem.mark_superseded(old_id=old_id, new_id=new_id)

    # Bypass embedding (not loaded in test) — use keyword fallback
    results = mem.recall("cats", n=10, kind=None)
    returned_ids = {r["memory_id"] for r in results}
    assert old_id not in returned_ids


def test_recall_includes_non_superseded_records(tmp_path):
    """recall() still returns normal (non-superseded) observations."""
    mem = _make_memory(tmp_path)
    obs_id = _insert_observation(mem, "active memory about dogs")

    results = mem.recall("dogs", n=10, kind=None)
    returned_ids = {r["memory_id"] for r in results}
    assert obs_id in returned_ids


# ---------------------------------------------------------------------------
# Tests: Phase 2-3 — near-duplicate detection
# ---------------------------------------------------------------------------


def test_find_near_duplicates_returns_pairs(tmp_path):
    """find_near_duplicates() returns (id_a, id_b) pairs from the DB."""
    mem = _make_memory(tmp_path)
    # Insert two observations with manually-forced high cosine similarity
    import numpy as np
    from familiar_agent.tools.memory import _encode_vector

    vec = np.ones(384, dtype=np.float32)
    vec /= np.linalg.norm(vec)

    id_a = _insert_observation(mem, "memory A about the living room")
    id_b = _insert_observation(mem, "memory B about the living room")

    # Inject identical embeddings so cosine similarity = 1.0
    conn = _direct_conn(mem)
    blob = _encode_vector(vec.tolist())
    for obs_id in (id_a, id_b):
        conn.execute(
            "INSERT OR REPLACE INTO obs_embeddings (obs_id, vector) VALUES (?, ?)",
            (obs_id, blob),
        )
    conn.commit()

    pairs = mem.find_near_duplicates(threshold=0.95)
    pair_ids = {frozenset([p[0], p[1]]) for p in pairs}
    assert frozenset([id_a, id_b]) in pair_ids


def test_find_near_duplicates_skips_already_superseded(tmp_path):
    """find_near_duplicates() ignores records that are already superseded."""
    import numpy as np
    from familiar_agent.tools.memory import _encode_vector

    mem = _make_memory(tmp_path)
    vec = np.ones(384, dtype=np.float32)
    vec /= np.linalg.norm(vec)
    blob = _encode_vector(vec.tolist())

    id_a = _insert_observation(mem, "old memory X")
    id_b = _insert_observation(mem, "new memory X")
    mem.mark_superseded(old_id=id_a, new_id=id_b)

    conn = _direct_conn(mem)
    for obs_id in (id_a, id_b):
        conn.execute(
            "INSERT OR REPLACE INTO obs_embeddings (obs_id, vector) VALUES (?, ?)",
            (obs_id, blob),
        )
    conn.commit()

    pairs = mem.find_near_duplicates(threshold=0.95)
    pair_ids = {frozenset([p[0], p[1]]) for p in pairs}
    # id_a is already superseded — should not appear in pairs
    assert frozenset([id_a, id_b]) not in pair_ids
