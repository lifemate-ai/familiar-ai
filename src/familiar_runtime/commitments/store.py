"""SQLite-backed durable commitment store (secretary core).

Follows the standalone-runtime-DB pattern established by
:mod:`familiar_runtime.tasks.store`: the store self-initialises its own schema
in a dedicated database file, so it stays persona-neutral and decoupled from the
neighbour's observation/memory DB.
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

from .model import Commitment, CommitmentKind, CommitmentStatus


def _sort_key(c: Commitment) -> tuple[int, float, int, float]:
    """Order: dated commitments first (earliest due), then undated by priority.

    Returns a tuple sorted ascending: (has_no_due, effective_due, -priority,
    created_at). ``has_no_due`` pushes undated commitments after dated ones.
    """
    due = c.effective_due()
    if due is not None:
        return (0, due, -c.priority, c.created_at)
    return (1, 0.0, -c.priority, c.created_at)


class SQLiteCommitmentStore:
    """Persist commitments in a dedicated SQLite database."""

    def __init__(self, db_path: str | Path) -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS runtime_commitments (
                id TEXT PRIMARY KEY,
                summary TEXT NOT NULL,
                kind TEXT NOT NULL,
                status TEXT NOT NULL,
                due_at REAL,
                priority INTEGER NOT NULL,
                created_by TEXT NOT NULL,
                person TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                completed_at REAL,
                snooze_until REAL,
                metadata_json TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_commitments_status
                ON runtime_commitments(status);
            """
        )
        self._ensure_columns()
        self._conn.commit()

    def _ensure_columns(self) -> None:
        """Idempotently add columns introduced after the initial schema.

        Lets an existing commitments.db created by an earlier version pick up the
        proactive-reminder columns without a separate migration runner.
        """
        existing = {
            row["name"] for row in self._conn.execute("PRAGMA table_info(runtime_commitments)")
        }
        if "last_reminded_at" not in existing:
            self._conn.execute("ALTER TABLE runtime_commitments ADD COLUMN last_reminded_at REAL")
        if "reminder_count" not in existing:
            self._conn.execute(
                "ALTER TABLE runtime_commitments ADD COLUMN reminder_count INTEGER NOT NULL DEFAULT 0"
            )

    # ── writes ──

    def create(
        self,
        *,
        summary: str,
        kind: CommitmentKind = CommitmentKind.REMINDER,
        due_at: float | None = None,
        priority: int = 0,
        created_by: str = "agent",
        person: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Commitment:
        now = time.time()
        commitment = Commitment(
            id=f"commit_{uuid.uuid4().hex}",
            summary=summary,
            kind=kind,
            status=CommitmentStatus.OPEN,
            due_at=due_at,
            priority=priority,
            created_by=created_by,
            person=person,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )
        self.save(commitment)
        return commitment

    def save(self, commitment: Commitment) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO runtime_commitments (
                id, summary, kind, status, due_at, priority, created_by, person,
                created_at, updated_at, completed_at, snooze_until,
                last_reminded_at, reminder_count, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                commitment.id,
                commitment.summary,
                commitment.kind.value,
                commitment.status.value,
                commitment.due_at,
                commitment.priority,
                commitment.created_by,
                commitment.person,
                commitment.created_at,
                commitment.updated_at,
                commitment.completed_at,
                commitment.snooze_until,
                commitment.last_reminded_at,
                commitment.reminder_count,
                json.dumps(commitment.metadata, ensure_ascii=False),
            ),
        )
        self._conn.commit()

    def _require(self, commitment_id: str) -> Commitment:
        commitment = self.get(commitment_id)
        if commitment is None:
            raise KeyError(f"commitment not found: {commitment_id}")
        return commitment

    def complete(self, commitment_id: str) -> Commitment:
        commitment = self._require(commitment_id)
        now = time.time()
        commitment.status = CommitmentStatus.DONE
        commitment.completed_at = now
        commitment.updated_at = now
        self.save(commitment)
        return commitment

    def cancel(self, commitment_id: str) -> Commitment:
        commitment = self._require(commitment_id)
        commitment.status = CommitmentStatus.CANCELLED
        commitment.updated_at = time.time()
        self.save(commitment)
        return commitment

    def snooze(self, commitment_id: str, *, until: float) -> Commitment:
        commitment = self._require(commitment_id)
        commitment.status = CommitmentStatus.SNOOZED
        commitment.snooze_until = until
        # Explicit deferral restarts the proactive-reminder cadence.
        commitment.reminder_count = 0
        commitment.last_reminded_at = None
        commitment.updated_at = time.time()
        self.save(commitment)
        return commitment

    def mark_reminded(self, commitment_ids: list[str], *, at: float) -> None:
        """Record that a proactive reminder fired for these commitments."""
        for commitment_id in commitment_ids:
            self._conn.execute(
                """
                UPDATE runtime_commitments
                SET last_reminded_at = ?, reminder_count = reminder_count + 1, updated_at = ?
                WHERE id = ?
                """,
                (at, at, commitment_id),
            )
        self._conn.commit()

    # ── reads ──

    def get(self, commitment_id: str) -> Commitment | None:
        row = self._conn.execute(
            "SELECT * FROM runtime_commitments WHERE id = ?",
            (commitment_id,),
        ).fetchone()
        return self._from_row(row) if row else None

    def _active(self) -> list[Commitment]:
        rows = self._conn.execute(
            "SELECT * FROM runtime_commitments WHERE status IN (?, ?)",
            (CommitmentStatus.OPEN.value, CommitmentStatus.SNOOZED.value),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    def list_open(self) -> list[Commitment]:
        return sorted(self._active(), key=_sort_key)

    def list_due(self, *, now: float) -> list[Commitment]:
        due = [c for c in self._active() if c.is_due(now=now)]
        return sorted(due, key=_sort_key)

    def list_upcoming(self, *, now: float, horizon: float) -> list[Commitment]:
        upcoming = [c for c in self._active() if c.is_upcoming(now=now, horizon=horizon)]
        return sorted(upcoming, key=_sort_key)

    def list_due_for_reminder(self, *, now: float, base_cooldown: float) -> list[Commitment]:
        """Due commitments that warrant a *proactive* reminder right now.

        Applies the per-commitment escalating backoff + cap, distinct from
        ``list_due`` (which is used for passive context surfacing).
        """
        ready = [
            c for c in self._active() if c.due_for_reminder(now=now, base_cooldown=base_cooldown)
        ]
        return sorted(ready, key=_sort_key)

    def _from_row(self, row: sqlite3.Row) -> Commitment:
        return Commitment(
            id=row["id"],
            summary=row["summary"],
            kind=CommitmentKind(row["kind"]),
            status=CommitmentStatus(row["status"]),
            due_at=row["due_at"],
            priority=row["priority"],
            created_by=row["created_by"],
            person=row["person"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            completed_at=row["completed_at"],
            snooze_until=row["snooze_until"],
            last_reminded_at=row["last_reminded_at"],
            reminder_count=row["reminder_count"],
            metadata=json.loads(row["metadata_json"]),
        )

    def close(self) -> None:
        self._conn.close()
