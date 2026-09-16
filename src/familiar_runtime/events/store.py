"""SQLite persistence for runtime events."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .model import AgentEvent


class SQLiteEventStore:
    """Append and replay runtime events from SQLite."""

    def __init__(self, db_path: str | Path) -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runtime_events (
                id TEXT PRIMARY KEY,
                run_id TEXT,
                task_id TEXT,
                turn_id TEXT,
                source TEXT NOT NULL,
                type TEXT NOT NULL,
                payload TEXT NOT NULL,
                timestamp REAL NOT NULL,
                salience REAL NOT NULL,
                confidence REAL NOT NULL,
                parent_id TEXT
            )
            """
        )
        self._conn.commit()

    def append(self, event: AgentEvent) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO runtime_events (
                id, run_id, task_id, turn_id, source, type, payload,
                timestamp, salience, confidence, parent_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.id,
                event.run_id,
                event.task_id,
                event.turn_id,
                event.source,
                event.type,
                json.dumps(event.payload, ensure_ascii=False),
                event.timestamp,
                event.salience,
                event.confidence,
                event.parent_id,
            ),
        )
        self._conn.commit()

    def replay(self) -> list[AgentEvent]:
        rows = self._conn.execute(
            "SELECT * FROM runtime_events ORDER BY timestamp, rowid"
        ).fetchall()
        return [
            AgentEvent(
                id=row["id"],
                run_id=row["run_id"],
                task_id=row["task_id"],
                turn_id=row["turn_id"],
                source=row["source"],
                type=row["type"],
                payload=json.loads(row["payload"]),
                timestamp=row["timestamp"],
                salience=row["salience"],
                confidence=row["confidence"],
                parent_id=row["parent_id"],
            )
            for row in rows
        ]

    def close(self) -> None:
        self._conn.close()
