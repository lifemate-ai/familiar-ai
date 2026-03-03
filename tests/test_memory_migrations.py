"""Tests for automatic SQLite schema migrations on startup."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import patch

from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {str(r["name"]) for r in rows}


def test_auto_applies_migrations_on_first_connect(tmp_path) -> None:
    db_path = str(tmp_path / "auto_migrate.db")
    expected_ids = {p.stem for p in (Path.cwd() / "migration").glob("*.py")}

    with patch.object(_EmbeddingModel, "pre_warm"):
        mem = ObservationMemory(db_path=db_path)
        mem.append_memory_event("memory.save", {"content": "x"}, queue_job=False)
        mem.close()

    with _connect(db_path) as conn:
        applied = {
            str(r["id"]) for r in conn.execute("SELECT id FROM schema_migrations").fetchall()
        }
        tables = {
            str(r["name"])
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }

    assert expected_ids.issubset(applied)
    assert {"observations", "obs_embeddings", "memory_events", "memory_jobs"}.issubset(tables)


def test_migrates_legacy_observations_schema(tmp_path) -> None:
    db_path = str(tmp_path / "legacy_schema.db")
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE observations (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                direction TEXT NOT NULL DEFAULT 'unknown'
            )
            """
        )
        conn.commit()

    with patch.object(_EmbeddingModel, "pre_warm"):
        mem = ObservationMemory(db_path=db_path)
        mem.append_memory_event("memory.save", {"content": "x"}, queue_job=False)
        mem.close()

    with _connect(db_path) as conn:
        cols = _columns(conn, "observations")
        applied = {
            str(r["id"]) for r in conn.execute("SELECT id FROM schema_migrations").fetchall()
        }

    for name in ("kind", "emotion", "image_path", "image_data"):
        assert name in cols
    assert "2026-03-03-001_observations_baseline" in applied


def test_migrations_are_idempotent_across_restarts(tmp_path) -> None:
    db_path = str(tmp_path / "idempotent.db")
    with patch.object(_EmbeddingModel, "pre_warm"):
        mem = ObservationMemory(db_path=db_path)
        mem.append_memory_event("memory.save", {"content": "first"}, queue_job=False)
        mem.close()

        with _connect(db_path) as conn:
            count_first = conn.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]

        mem2 = ObservationMemory(db_path=db_path)
        mem2.append_memory_event("memory.save", {"content": "second"}, queue_job=False)
        mem2.close()

    with _connect(db_path) as conn:
        count_second = conn.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]

    assert count_second == count_first
