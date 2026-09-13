"""Social event ledger — one append-only relational timeline.

Every socially meaningful state change (a trust shift, a boundary, a
permission, a commitment, an identity violation, a person-model write) lands
here as a typed event, so the agent can answer "what happened between us
lately?" from one queryable place instead of reconstructing it from scattered
evidence lists and snapshots.

Design constraints:

- **Emission is best-effort.** :meth:`SocialEventLog.append` never raises to
  its caller — a broken ledger must not break the relationship tracker, the
  commitment store or the identity core that emits into it.
- **Closed vocabulary.** ``kind`` must be one of :data:`SOCIAL_EVENT_KINDS`;
  an unknown kind is logged and dropped rather than silently widening the
  schema of the timeline.
- **No persona strings.** Person keys and payloads come from the emitters.

Rows live in the shared observations DB (``social_events`` table, migration
013) via the same lazy-connection + migration pattern as
:class:`familiar_neighbor.mind.person_model.PersonModelTracker`.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from familiar_agent.sqlite_migrations import apply_migrations, default_migration_dir

logger = logging.getLogger(__name__)

DEFAULT_SOCIAL_EVENTS_DB_PATH = Path.home() / ".familiar_ai" / "observations.db"

SOCIAL_EVENT_KINDS: frozenset[str] = frozenset(
    {
        "trust_shift",
        "intimacy_shift",
        "boundary_added",
        "permission_set",
        "commitment_added",
        "commitment_completed",
        "commitment_snoozed",
        "identity_violation",
        "identity_reflection",
        "person_inference",
        "repair",
        "sensitive_topic",
        "arc_updated",
        "action_evaluated",
        "consent_recorded",
    }
)

_MAX_RECENT = 200


@dataclass(frozen=True)
class SocialEvent:
    """One immutable entry on the relational timeline."""

    id: str
    ts: str
    source: str
    kind: str
    person_key: str | None = None
    session_id: str | None = None
    correlation_id: str | None = None
    confidence: float | None = None
    payload: dict[str, Any] = field(default_factory=dict)


def _clamp_confidence(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return None


class SocialEventLog:
    """Append-only, best-effort social event store.

    ``session_id`` is generated once per instance (one process lifetime);
    ``default_person`` fills ``person_key`` for emitters that only ever talk
    about the single companion (e.g. the relationship tracker).
    """

    def __init__(
        self,
        db_path: str | Path | None = None,
        *,
        default_person: str | None = None,
        session_id: str | None = None,
    ) -> None:
        self._db_path = Path(db_path) if db_path is not None else DEFAULT_SOCIAL_EVENTS_DB_PATH
        self._db: sqlite3.Connection | None = None
        self._default_person = (default_person or "").strip() or None
        self.session_id = session_id or f"sess_{uuid.uuid4().hex[:12]}"

    # ── connection ──

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

    def append(
        self,
        kind: str,
        *,
        source: str,
        person_key: str | None = None,
        correlation_id: str | None = None,
        confidence: float | None = None,
        payload: dict[str, Any] | None = None,
    ) -> SocialEvent | None:
        """Record one event. Returns the stored event, or None on any failure.

        Never raises: emitters call this from inside their own state updates
        and a ledger fault must not roll those back.
        """
        try:
            if kind not in SOCIAL_EVENT_KINDS:
                logger.warning("social_events: dropping unknown kind %r", kind)
                return None
            person = (person_key or "").strip() or self._default_person
            event = SocialEvent(
                id=f"sev_{uuid.uuid4().hex}",
                ts=datetime.now(timezone.utc).isoformat(),
                source=str(source),
                kind=kind,
                person_key=person,
                session_id=self.session_id,
                correlation_id=correlation_id,
                confidence=_clamp_confidence(confidence),
                payload=dict(payload or {}),
            )
            db = self._ensure_db()
            db.execute(
                """
                INSERT INTO social_events (
                    id, ts, source, kind, person_key, session_id,
                    correlation_id, confidence, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.ts,
                    event.source,
                    event.kind,
                    event.person_key,
                    event.session_id,
                    event.correlation_id,
                    event.confidence,
                    json.dumps(event.payload, ensure_ascii=False, default=str),
                ),
            )
            db.commit()
            return event
        except Exception as exc:  # noqa: BLE001
            logger.warning("social_events: append failed (%s): %s", kind, exc)
            return None

    # ── reads ──

    @staticmethod
    def _where(kind: str | None, person_key: str | None) -> tuple[str, list[Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if kind:
            clauses.append("kind = ?")
            params.append(kind)
        if person_key:
            clauses.append("LOWER(person_key) = LOWER(?)")
            params.append(person_key.strip())
        return (" WHERE " + " AND ".join(clauses)) if clauses else "", params

    def recent(
        self,
        limit: int = 10,
        *,
        kind: str | None = None,
        person_key: str | None = None,
    ) -> list[SocialEvent]:
        """Newest-first slice of the timeline, optionally filtered."""
        limit = max(1, min(int(limit), _MAX_RECENT))
        where, params = self._where(kind, person_key)
        try:
            db = self._ensure_db()
            rows = db.execute(
                "SELECT id, ts, source, kind, person_key, session_id, correlation_id, "
                f"confidence, payload_json FROM social_events{where} "
                "ORDER BY ts DESC, rowid DESC LIMIT ?",
                [*params, limit],
            ).fetchall()
        except Exception as exc:  # noqa: BLE001
            logger.warning("social_events: recent() failed: %s", exc)
            return []
        return [self._from_row(r) for r in rows]

    def by_person(self, person_key: str, limit: int = 10) -> list[SocialEvent]:
        return self.recent(limit, person_key=person_key)

    def by_kind(self, kind: str, limit: int = 10) -> list[SocialEvent]:
        return self.recent(limit, kind=kind)

    def count(self, *, kind: str | None = None, person_key: str | None = None) -> int:
        where, params = self._where(kind, person_key)
        try:
            db = self._ensure_db()
            row = db.execute(f"SELECT COUNT(*) FROM social_events{where}", params).fetchone()
        except Exception as exc:  # noqa: BLE001
            logger.warning("social_events: count() failed: %s", exc)
            return 0
        return int(row[0]) if row else 0

    @staticmethod
    def _from_row(row: sqlite3.Row) -> SocialEvent:
        try:
            payload = json.loads(row["payload_json"] or "{}")
        except (TypeError, ValueError):
            payload = {}
        if not isinstance(payload, dict):
            payload = {"value": payload}
        return SocialEvent(
            id=str(row["id"]),
            ts=str(row["ts"]),
            source=str(row["source"]),
            kind=str(row["kind"]),
            person_key=row["person_key"],
            session_id=row["session_id"],
            correlation_id=row["correlation_id"],
            confidence=row["confidence"],
            payload=payload,
        )


def emit_social_event(event_log: Any, kind: str, **kwargs: Any) -> None:
    """Best-effort emission helper shared by the emitters.

    ``event_log`` is duck-typed (anything with ``append(kind, **kwargs)``) so
    persona-free packages can hold one without importing this module. A None
    log is a no-op; a raising log is logged and swallowed.
    """
    if event_log is None:
        return
    try:
        event_log.append(kind, **kwargs)
    except Exception as exc:  # noqa: BLE001
        logger.warning("social_events: emitter for %s failed: %s", kind, exc)
