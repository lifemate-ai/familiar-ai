"""Identity assertions — load-bearing values, boundaries, and self-commitments."""

from __future__ import annotations

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS identity_assertions (
            id TEXT PRIMARY KEY,
            assertion_key TEXT NOT NULL UNIQUE,
            kind TEXT NOT NULL,
            statement TEXT NOT NULL,
            non_negotiable INTEGER NOT NULL DEFAULT 0,
            confidence REAL NOT NULL DEFAULT 0.6,
            checker_id TEXT NOT NULL DEFAULT '',
            checker_params_json TEXT NOT NULL DEFAULT '{}',
            source TEXT NOT NULL DEFAULT 'seed',
            evidence_json TEXT NOT NULL DEFAULT '[]',
            violation_count INTEGER NOT NULL DEFAULT 0,
            last_violated_at TEXT,
            last_seen_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_identity_assertions_kind "
        "ON identity_assertions(kind, confidence DESC)"
    )
