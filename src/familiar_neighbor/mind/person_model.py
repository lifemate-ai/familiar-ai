"""Persistent per-person mental model fed by ToM inferences.

The ToM tool produces structured inferences ({state, confidence}, evidence,
response policy) but historically discarded them after one turn. This tracker
persists them per person so the agent accumulates a model of what each person
tends to feel and want — and what response approach was chosen — instead of
re-inferring from scratch every conversation.

Follows the lazy-connection + migration pattern of
:class:`familiar_neighbor.mind.relationship.RelationshipTracker`; rows live in
the shared observations DB (``person_inferences`` table, migration 010).
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from familiar_agent.sqlite_migrations import apply_migrations, default_migration_dir

logger = logging.getLogger(__name__)

DEFAULT_PERSON_MODEL_DB_PATH = Path.home() / ".familiar_ai" / "observations.db"


def _parse_created_at(created_at_iso: str) -> datetime:
    """Parse a stored timestamp, treating unparseable values as very old."""
    try:
        then = datetime.fromisoformat(created_at_iso)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    return then


def _age_label(created_at_iso: str, *, now: datetime | None = None) -> str:
    """Compact "how long ago" label for prompt rendering."""
    try:
        then = datetime.fromisoformat(created_at_iso)
    except ValueError:
        return ""
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    now = now or datetime.now(timezone.utc)
    seconds = max(0.0, (now - then).total_seconds())
    if seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    if seconds < 48 * 3600:
        return f"{int(seconds // 3600)}h ago"
    return f"{int(seconds // 86400)}d ago"


class PersonModelTracker:
    """Append-only store of per-person mental-state inferences."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self._db_path = Path(db_path) if db_path is not None else DEFAULT_PERSON_MODEL_DB_PATH
        self._db: sqlite3.Connection | None = None

    def _ensure_db(self) -> sqlite3.Connection:
        if self._db is None:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._db = sqlite3.connect(self._db_path, check_same_thread=False)
            self._db.row_factory = sqlite3.Row
            self._db.execute("PRAGMA journal_mode = WAL")
            self._db.execute("PRAGMA synchronous = NORMAL")
            apply_migrations(self._db, default_migration_dir())
            self._db.commit()
        return self._db

    def close(self) -> None:
        if self._db is not None:
            try:
                self._db.close()
            finally:
                self._db = None

    # ── writes ──

    def record_inference(
        self,
        *,
        person: str,
        states: list[tuple[str, float]],
        evidence: list[str],
        policy: str,
        source: str = "tom",
    ) -> None:
        """Persist one ToM inference (one row per inferred state)."""
        person = person.strip()
        if not person:
            return
        db = self._ensure_db()
        created_at = datetime.now(timezone.utc).isoformat()
        evidence_json = json.dumps(evidence, ensure_ascii=False)
        for state, confidence in states:
            state = str(state).strip()
            if not state:
                continue
            db.execute(
                """
                INSERT INTO person_inferences (
                    id, person, state, confidence, evidence_json, policy, source, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"pinf_{uuid.uuid4().hex}",
                    person,
                    state,
                    float(confidence),
                    evidence_json,
                    policy,
                    source,
                    created_at,
                ),
            )
        db.commit()

    # ── reads ──

    def recent(self, person: str, n: int = 5) -> list[dict]:
        db = self._ensure_db()
        rows = db.execute(
            """
            SELECT person, state, confidence, evidence_json, policy, source, created_at
            FROM person_inferences
            WHERE person = ? COLLATE NOCASE
            ORDER BY created_at DESC, rowid DESC
            LIMIT ?
            """,
            (person, n),
        ).fetchall()
        return [
            {
                "person": row["person"],
                "state": row["state"],
                "confidence": row["confidence"],
                "evidence": json.loads(row["evidence_json"]),
                "policy": row["policy"],
                "source": row["source"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def context_for_prompt(self, person: str, n: int = 4, max_age_days: float = 7.0) -> str:
        """Compact accumulated-model block for the system prompt.

        Inferences older than ``max_age_days`` are excluded — a stale guess
        ("exhausted", ten days ago) misleads more than it helps.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        rows = [
            row
            for row in self.recent(person, n=n)
            if _parse_created_at(row["created_at"]) >= cutoff
        ]
        if not rows:
            return ""
        lines = [f"[Person model: {person} — accumulated impressions, may be stale]"]
        for row in rows:
            age = _age_label(row["created_at"])
            suffix = f" ({row['confidence']:.1f}{', ' + age if age else ''})"
            lines.append(f"- {row['state']}{suffix}")
        latest_policy = next((row["policy"] for row in rows if row["policy"]), "")
        if latest_policy:
            lines.append(f"- last chosen approach: {latest_policy}")
        return "\n".join(lines)
