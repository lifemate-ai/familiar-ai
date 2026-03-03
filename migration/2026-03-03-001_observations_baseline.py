"""Create and backfill the baseline observations schema."""

from __future__ import annotations

import sqlite3


def _has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(str(r[1]) == column for r in rows)


def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS observations (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            direction TEXT NOT NULL DEFAULT 'unknown',
            kind TEXT NOT NULL DEFAULT 'observation',
            emotion TEXT NOT NULL DEFAULT 'neutral',
            image_path TEXT,
            image_data TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS obs_embeddings (
            obs_id TEXT PRIMARY KEY REFERENCES observations(id) ON DELETE CASCADE,
            vector BLOB NOT NULL
        )
        """
    )

    # Existing users may already have observations without newer columns.
    for col, definition in [
        ("kind", "TEXT NOT NULL DEFAULT 'observation'"),
        ("emotion", "TEXT NOT NULL DEFAULT 'neutral'"),
        ("image_path", "TEXT"),
        ("image_data", "TEXT"),
    ]:
        if not _has_column(conn, "observations", col):
            conn.execute(f"ALTER TABLE observations ADD COLUMN {col} {definition}")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_obs_timestamp ON observations(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_obs_date ON observations(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_obs_kind ON observations(kind)")
