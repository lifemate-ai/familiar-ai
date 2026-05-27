"""Memory graph runtime tables: episodes, activation, unfinished business."""

from __future__ import annotations

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS episodes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT NOT NULL DEFAULT '',
            participants TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'open',
            opened_from_memory_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS episode_memories (
            id TEXT PRIMARY KEY,
            episode_id TEXT NOT NULL,
            memory_id TEXT NOT NULL,
            position INTEGER NOT NULL DEFAULT 0,
            added_at TEXT NOT NULL,
            UNIQUE(episode_id, memory_id),
            FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE,
            FOREIGN KEY (memory_id) REFERENCES observations(id) ON DELETE CASCADE
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memory_activation (
            id TEXT PRIMARY KEY,
            memory_id TEXT NOT NULL,
            activation REAL NOT NULL DEFAULT 0.0,
            source TEXT NOT NULL DEFAULT 'recall',
            context TEXT NOT NULL DEFAULT '',
            episode_id TEXT,
            activated_at TEXT NOT NULL,
            FOREIGN KEY (memory_id) REFERENCES observations(id) ON DELETE CASCADE,
            FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE SET NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS unfinished_business (
            id TEXT PRIMARY KEY,
            summary TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            source TEXT NOT NULL DEFAULT 'agent',
            related_memory_id TEXT,
            metadata_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL,
            resolved_at TEXT,
            FOREIGN KEY (related_memory_id) REFERENCES observations(id) ON DELETE SET NULL
        )
        """
    )

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_episode_memories_episode "
        "ON episode_memories(episode_id, position)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_memory_activation_recent "
        "ON memory_activation(activated_at DESC)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_unfinished_business_status "
        "ON unfinished_business(status, created_at DESC)"
    )
