"""Persistent per-person mental-model inferences (ToM accumulation)."""

from __future__ import annotations

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS person_inferences (
            id TEXT PRIMARY KEY,
            person TEXT NOT NULL,
            state TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 0.0,
            evidence_json TEXT NOT NULL DEFAULT '[]',
            policy TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT 'tom',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_person_inferences_person "
        "ON person_inferences(person, created_at DESC)"
    )
