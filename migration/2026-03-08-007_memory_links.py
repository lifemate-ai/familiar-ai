"""Add memory_links table for typed associative links between observations."""

from __future__ import annotations

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memory_links (
            id          TEXT PRIMARY KEY,
            source_id   TEXT NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
            target_id   TEXT NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
            link_type   TEXT NOT NULL DEFAULT 'related',
            note        TEXT,
            created_at  TEXT NOT NULL,
            UNIQUE(source_id, target_id, link_type)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_links_source ON memory_links(source_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_links_target ON memory_links(target_id)")
