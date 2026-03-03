"""Add durable event log + async memory job queue tables."""

from __future__ import annotations

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memory_events (
            event_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            event_type TEXT NOT NULL,
            dedupe_key TEXT,
            payload_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_memory_events_dedupe
        ON memory_events(dedupe_key)
        WHERE dedupe_key IS NOT NULL
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_memory_events_created_at ON memory_events(created_at)"
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memory_jobs (
            job_id TEXT PRIMARY KEY,
            event_id TEXT NOT NULL REFERENCES memory_events(event_id) ON DELETE CASCADE,
            job_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            attempts INTEGER NOT NULL DEFAULT 0,
            available_at TEXT NOT NULL,
            last_error TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_memory_jobs_event_type
        ON memory_jobs(event_id, job_type)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_memory_jobs_status_available
        ON memory_jobs(status, available_at)
        """
    )
