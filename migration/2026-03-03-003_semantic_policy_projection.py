"""Add semantic facts and behavior policies projection tables."""

from __future__ import annotations

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS semantic_facts (
            id TEXT PRIMARY KEY,
            fact_key TEXT NOT NULL UNIQUE,
            fact_text TEXT NOT NULL,
            source_memory_id TEXT REFERENCES observations(id) ON DELETE SET NULL,
            confidence REAL NOT NULL DEFAULT 0.5,
            tags TEXT NOT NULL DEFAULT '',
            last_seen_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_semantic_facts_last_seen ON semantic_facts(last_seen_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_semantic_facts_source ON semantic_facts(source_memory_id)"
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS behavior_policies (
            id TEXT PRIMARY KEY,
            policy_key TEXT NOT NULL UNIQUE,
            policy_text TEXT NOT NULL,
            trigger_context TEXT NOT NULL DEFAULT '',
            action_hint TEXT NOT NULL DEFAULT '',
            source_memory_id TEXT REFERENCES observations(id) ON DELETE SET NULL,
            confidence REAL NOT NULL DEFAULT 0.5,
            last_seen_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_behavior_policies_last_seen ON behavior_policies(last_seen_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_behavior_policies_source ON behavior_policies(source_memory_id)"
    )
