"""Add importance decay and superseded_by columns for Phase 2 memory consolidation."""

from __future__ import annotations

import sqlite3


def _has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(str(r[1]) == column for r in rows)


def upgrade(conn: sqlite3.Connection) -> None:
    # 2-2: importance — used to weight recall ranking and decay over time
    if not _has_column(conn, "observations", "importance"):
        conn.execute("ALTER TABLE observations ADD COLUMN importance REAL NOT NULL DEFAULT 1.0")

    # 2-3: superseded_by — set when an older memory is merged into a newer one
    if not _has_column(conn, "observations", "superseded_by"):
        conn.execute("ALTER TABLE observations ADD COLUMN superseded_by TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_obs_superseded ON observations(superseded_by)")
