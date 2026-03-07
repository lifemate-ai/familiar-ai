"""Create scene_entities and scene_events tables for the world model (Phase 1)."""

from __future__ import annotations

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scene_entities (
            entity_id   TEXT PRIMARY KEY,
            label       TEXT NOT NULL,
            category    TEXT NOT NULL DEFAULT 'object',
            first_seen  TEXT NOT NULL,
            last_seen   TEXT NOT NULL,
            confidence  REAL NOT NULL DEFAULT 0.8,
            bbox_hint   TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scene_entities_label ON scene_entities(label)")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scene_events (
            event_id     TEXT PRIMARY KEY,
            event_type   TEXT NOT NULL,
            entity_id    TEXT REFERENCES scene_entities(entity_id) ON DELETE SET NULL,
            entity_label TEXT NOT NULL,
            timestamp    TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scene_events_ts ON scene_events(timestamp)")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS exploration_state (
            id          INTEGER PRIMARY KEY CHECK (id = 1),
            pan_accum   REAL    NOT NULL DEFAULT 0.0,
            tilt_accum  REAL    NOT NULL DEFAULT 0.0,
            records_json TEXT   NOT NULL DEFAULT '[]',
            saved_at    TEXT    NOT NULL
        )
        """
    )
