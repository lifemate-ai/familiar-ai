"""Narrative arcs — the long threads a life is made of.

A self that only remembers one sentence per day has no plot. Arcs are the
bounded set (at most seven active) of ongoing storylines the agent holds
about its own life — a project, a relationship thread, a becoming — each
with a key, a title, a running summary and an importance used to decide
which arc goes dormant when an eighth is committed (selfhood/sociality
substrate, Phase 2).
"""

from __future__ import annotations

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS narrative_arcs (
            id TEXT PRIMARY KEY,
            arc_key TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            summary TEXT NOT NULL DEFAULT '',
            importance REAL NOT NULL DEFAULT 0.5,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_narrative_arcs_status_importance "
        "ON narrative_arcs(status, importance DESC)"
    )
