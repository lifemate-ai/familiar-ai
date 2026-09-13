"""Relationship tracker — persistent companion relationship metadata.

Relationship state now lives primarily in SQLite so it participates in the same
migration and backup story as the rest of the agent memory. Legacy JSON state is
still imported on first load for backward compatibility.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

from familiar_agent.sqlite_migrations import apply_migrations, default_migration_dir

from .social_events import emit_social_event

logger = logging.getLogger(__name__)

DEFAULT_RELATIONSHIP_DB_PATH = Path.home() / ".familiar_ai" / "observations.db"

_DEFAULT_STATE: dict = {
    "first_session_date": None,
    "last_session_date": None,
    "session_count": 0,
    "conversation_count": 0,
    "trust_trajectory": [],
    "intimacy_trajectory": [],
    "repair_history": [],
    "support_preferences": [],
    "failed_support_patterns": [],
    "shared_rituals": [],
    "sensitive_topics": [],
    "permission_model": {},
    "relational_memory": {
        "tendencies": [],
        "preferences": [],
        "boundaries": [],
    },
}


def _fresh_state() -> dict:
    return json.loads(json.dumps(_DEFAULT_STATE))


class RelationshipTracker:
    """Tracks longitudinal relationship metadata with the companion."""

    def __init__(self, state_path: Path | None = None, db_path: str | Path | None = None):
        self._state_path = state_path or Path.home() / ".familiar_ai" / "relationship.json"
        if db_path is None:
            self._db_path = (
                self._state_path.with_suffix(".db")
                if state_path is not None
                else DEFAULT_RELATIONSHIP_DB_PATH
            )
        else:
            self._db_path = Path(db_path)
        self._db: sqlite3.Connection | None = None
        # Optional social event ledger (duck-typed: ``append(kind, **kw)``).
        # None keeps every write path byte-stable; emission never raises.
        self.event_log: Any = None
        self._state: dict = self._load()

    def close(self) -> None:
        if self._db is not None:
            try:
                self._db.close()
            except Exception:
                pass
            finally:
                self._db = None

    def _ensure_db(self) -> sqlite3.Connection:
        if self._db is None:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._db = sqlite3.connect(self._db_path, check_same_thread=False)
            self._db.row_factory = sqlite3.Row
            self._db.execute("PRAGMA journal_mode = WAL")
            self._db.execute("PRAGMA synchronous = NORMAL")
            self._db.execute("PRAGMA foreign_keys = ON")
            apply_migrations(self._db, default_migration_dir())
            self._db.commit()
        return self._db

    def _load_from_db(self) -> dict | None:
        try:
            db = self._ensure_db()
            row = db.execute(
                "SELECT value_json FROM relationship_state WHERE state_key = 'default'"
            ).fetchone()
        except Exception as e:
            logger.warning("Could not load relationship state from SQLite: %s", e)
            return None
        if row is None:
            return None
        try:
            payload = json.loads(str(row["value_json"]))
        except Exception as e:
            logger.warning("Could not decode relationship state payload: %s", e)
            return None
        state = _fresh_state()
        if isinstance(payload, dict):
            state.update(payload)
        return state

    def _load_legacy_json(self) -> dict | None:
        try:
            if self._state_path.exists():
                payload = json.loads(self._state_path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    state = _fresh_state()
                    state.update(payload)
                    return state
        except Exception as e:
            logger.warning("Could not load legacy relationship state: %s", e)
        return None

    def _load(self) -> dict:
        state = self._load_from_db()
        if state is not None:
            return state
        state = self._load_legacy_json()
        if state is not None:
            self._state = state
            self._save()
            return state
        return _fresh_state()

    def _save(self) -> None:
        try:
            db = self._ensure_db()
            now = datetime.utcnow().isoformat()
            db.execute(
                """
                INSERT INTO relationship_state (state_key, value_json, updated_at)
                VALUES ('default', ?, ?)
                ON CONFLICT(state_key) DO UPDATE SET
                    value_json = excluded.value_json,
                    updated_at = excluded.updated_at
                """,
                (json.dumps(self._state, ensure_ascii=False), now),
            )
            db.commit()
        except Exception as e:
            logger.warning("Could not save relationship state: %s", e)

    def _append_evidence(
        self,
        key: str,
        *,
        evidence: str,
        confidence: float = 0.6,
        value: float | None = None,
        extra: dict | None = None,
    ) -> None:
        entries = self._state.setdefault(key, [])
        record = {
            "evidence": evidence,
            "confidence": max(0.0, min(1.0, float(confidence))),
            "observed_at": time.time(),
            "recency": time.time(),
        }
        if value is not None:
            record["value"] = max(0.0, min(1.0, float(value)))
        if extra:
            record.update(extra)
        entries.append(record)
        del entries[:-30]
        self._save()

    def _current_metric(self, key: str, default: float) -> float:
        entries = self._state.get(key, [])
        if not entries:
            return default
        latest = entries[-1]
        return max(0.0, min(1.0, float(latest.get("value", default))))

    def record_session(self) -> None:
        today = date.today().isoformat()
        if self._state["first_session_date"] is None:
            self._state["first_session_date"] = today
        self._state["last_session_date"] = today
        self._state["session_count"] = self._state.get("session_count", 0) + 1
        self._save()

    def record_conversation(self) -> None:
        self._state["conversation_count"] = self._state.get("conversation_count", 0) + 1
        self._save()

    @property
    def trust(self) -> float:
        return self._current_metric("trust_trajectory", 0.5)

    @property
    def intimacy(self) -> float:
        return self._current_metric("intimacy_trajectory", 0.4)

    def _emit(self, kind: str, **kwargs: Any) -> None:
        emit_social_event(self.event_log, kind, source="relationship", **kwargs)

    def note_trust_shift(self, value: float, evidence: str, confidence: float = 0.6) -> None:
        self._append_evidence(
            "trust_trajectory",
            value=value,
            evidence=evidence,
            confidence=confidence,
        )
        self._emit(
            "trust_shift",
            confidence=confidence,
            payload={"value": float(value), "evidence": evidence},
        )

    def note_intimacy_shift(self, value: float, evidence: str, confidence: float = 0.6) -> None:
        self._append_evidence(
            "intimacy_trajectory",
            value=value,
            evidence=evidence,
            confidence=confidence,
        )
        self._emit(
            "intimacy_shift",
            confidence=confidence,
            payload={"value": float(value), "evidence": evidence},
        )

    @property
    def first_session_date(self) -> str | None:
        return self._state.get("first_session_date")

    @property
    def last_session_date(self) -> str | None:
        return self._state.get("last_session_date")

    @property
    def session_count(self) -> int:
        return self._state.get("session_count", 0)

    @property
    def conversation_count(self) -> int:
        return self._state.get("conversation_count", 0)

    @property
    def days_together(self) -> int | None:
        first = self._state.get("first_session_date")
        if not first:
            return None
        try:
            first_date = date.fromisoformat(first)
            return (date.today() - first_date).days
        except (ValueError, TypeError):
            return None

    def _relational(self) -> dict:
        return self._state.setdefault(
            "relational_memory",
            {
                "tendencies": [],
                "preferences": [],
                "boundaries": [],
            },
        )

    def add_tendency(self, text: str, confidence: float = 0.6) -> None:
        tendencies = self._relational().setdefault("tendencies", [])
        for tendency in tendencies:
            if tendency["text"].lower() == text.lower():
                tendency["confidence"] = min(1.0, tendency["confidence"] + 0.1)
                tendency["observed_at"] = time.time()
                self._save()
                return
        tendencies.append({"text": text, "confidence": confidence, "observed_at": time.time()})
        self._save()

    def add_preference(self, text: str, valence: int = 1) -> None:
        prefs = self._relational().setdefault("preferences", [])
        for pref in prefs:
            if pref["text"].lower() == text.lower():
                pref["valence"] = valence
                pref["observed_at"] = time.time()
                self._save()
                return
        prefs.append({"text": text, "valence": valence, "observed_at": time.time()})
        self._save()

    def add_boundary(self, text: str, severity: int = 2) -> None:
        bounds = self._relational().setdefault("boundaries", [])
        for boundary in bounds:
            if boundary["text"].lower() == text.lower():
                boundary["severity"] = severity
                boundary["observed_at"] = time.time()
                self._save()
                self._emit(
                    "boundary_added",
                    payload={"text": text, "severity": int(severity), "updated": True},
                )
                return
        bounds.append({"text": text, "severity": severity, "observed_at": time.time()})
        self._save()
        self._emit("boundary_added", payload={"text": text, "severity": int(severity)})

    def record_support_preference(
        self,
        text: str,
        *,
        confidence: float = 0.7,
        style: str = "validate_first",
    ) -> None:
        self._append_evidence(
            "support_preferences",
            evidence=text,
            confidence=confidence,
            extra={"style": style, "text": text},
        )

    def record_failed_support_pattern(
        self,
        text: str,
        *,
        confidence: float = 0.8,
        consequence: str = "mismatch",
    ) -> None:
        self._append_evidence(
            "failed_support_patterns",
            evidence=text,
            confidence=confidence,
            extra={"pattern": text, "consequence": consequence},
        )

    def record_shared_ritual(
        self,
        text: str,
        *,
        confidence: float = 0.65,
    ) -> None:
        self._append_evidence(
            "shared_rituals",
            evidence=text,
            confidence=confidence,
            extra={"text": text},
        )

    def record_sensitive_topic(
        self,
        text: str,
        *,
        confidence: float = 0.65,
        caution: str = "handle-gently",
    ) -> None:
        self._append_evidence(
            "sensitive_topics",
            evidence=text,
            confidence=confidence,
            extra={"text": text, "caution": caution},
        )
        self._emit(
            "sensitive_topic", confidence=confidence, payload={"text": text, "caution": caution}
        )

    def record_repair(
        self,
        text: str,
        *,
        resolved: bool,
        confidence: float = 0.75,
    ) -> None:
        self._append_evidence(
            "repair_history",
            evidence=text,
            confidence=confidence,
            extra={"text": text, "resolved": bool(resolved)},
        )
        self._emit(
            "repair", confidence=confidence, payload={"text": text, "resolved": bool(resolved)}
        )

    def set_permission(
        self,
        permission: str,
        allowed: bool,
        *,
        evidence: str,
        confidence: float = 0.7,
    ) -> None:
        permissions = self._state.setdefault("permission_model", {})
        permissions[permission] = {
            "allowed": bool(allowed),
            "evidence": evidence,
            "confidence": max(0.0, min(1.0, float(confidence))),
            "observed_at": time.time(),
            "recency": time.time(),
        }
        self._save()
        self._emit(
            "permission_set",
            confidence=confidence,
            payload={"permission": permission, "allowed": bool(allowed), "evidence": evidence},
        )

    def permission(self, permission: str) -> dict | None:
        return self._state.get("permission_model", {}).get(permission)

    def record_consent(
        self,
        person: str,
        consent_type: str,
        value: bool,
        source: str = "explicit",
    ) -> None:
        """Record one person's consent (or its withdrawal) for one thing.

        Finer than the coarse ``permission_model``: keyed by (person,
        consent_type), case-insensitive on both, latest record replaces the
        previous one. Persists through the same state save as everything
        else on the tracker and mirrors onto the ledger as ``consent_recorded``.
        """
        person_clean = (person or "").strip()
        type_clean = (consent_type or "").strip()
        if not person_clean or not type_clean:
            raise ValueError("person and consent_type are required")
        source_clean = (source or "").strip() or "explicit"
        consents = self._state.setdefault("consents", [])
        person_key = person_clean.lower()
        type_key = type_clean.lower()
        kept = [
            item
            for item in consents
            if not (
                str(item.get("person", "")).lower() == person_key
                and str(item.get("consent_type", "")).lower() == type_key
            )
        ]
        kept.append(
            {
                "person": person_clean,
                "consent_type": type_clean,
                "value": bool(value),
                "source": source_clean,
                "recorded_at": time.time(),
            }
        )
        self._state["consents"] = kept
        self._save()
        self._emit(
            "consent_recorded",
            person_key=person_clean,
            payload={
                "person": person_clean,
                "consent_type": type_clean,
                "value": bool(value),
                "source": source_clean,
            },
        )

    def consents(self, person: str | None = None) -> list[dict]:
        rows = list(self._state.get("consents", []))
        if person is None:
            return rows
        key = person.strip().lower()
        return [r for r in rows if str(r.get("person", "")).lower() == key]

    def get_tendencies(self, min_confidence: float = 0.3) -> list[dict]:
        return [
            tendency
            for tendency in self._relational().get("tendencies", [])
            if tendency.get("confidence", 0) >= min_confidence
        ]

    def get_preferences(self) -> list[dict]:
        return self._relational().get("preferences", [])

    def get_boundaries(self) -> list[dict]:
        return self._relational().get("boundaries", [])

    def support_preferences(self) -> list[dict]:
        return self._state.get("support_preferences", [])

    def failed_support_patterns(self) -> list[dict]:
        return self._state.get("failed_support_patterns", [])

    def shared_rituals(self) -> list[dict]:
        return self._state.get("shared_rituals", [])

    def sensitive_topics(self) -> list[dict]:
        return self._state.get("sensitive_topics", [])

    def repair_history(self) -> list[dict]:
        return self._state.get("repair_history", [])

    def relational_context_for_prompt(self) -> str:
        parts: list[str] = []
        tendencies = self.get_tendencies()
        if tendencies:
            items = "; ".join(item["text"] for item in tendencies[:5])
            parts.append(f"(companion-tendencies: {items})")
        prefs = self.get_preferences()
        likes = [item["text"] for item in prefs if item.get("valence", 0) > 0][:5]
        dislikes = [item["text"] for item in prefs if item.get("valence", 0) < 0][:3]
        if likes:
            parts.append(f"(companion-likes: {'; '.join(likes)})")
        if dislikes:
            parts.append(f"(companion-dislikes: {'; '.join(dislikes)})")
        bounds = self.get_boundaries()
        if bounds:
            items = "; ".join(item["text"] for item in bounds[:3])
            parts.append(f"(companion-boundaries: {items})")
        if self.support_preferences():
            items = "; ".join(
                str(item.get("text") or item.get("evidence"))
                for item in self.support_preferences()[:3]
            )
            parts.append(f"(support-preferences: {items})")
        if self.failed_support_patterns():
            items = "; ".join(
                str(item.get("pattern") or item.get("evidence"))
                for item in self.failed_support_patterns()[:2]
            )
            parts.append(f"(failed-support-patterns: {items})")
        if self.shared_rituals():
            items = "; ".join(
                str(item.get("text") or item.get("evidence")) for item in self.shared_rituals()[:3]
            )
            parts.append(f"(shared-rituals: {items})")
        if self.sensitive_topics():
            items = "; ".join(
                str(item.get("text") or item.get("evidence"))
                for item in self.sensitive_topics()[:3]
            )
            parts.append(f"(sensitive-topics: {items})")
        if self._state.get("permission_model"):
            allowed = [
                name
                for name, item in self._state["permission_model"].items()
                if item.get("allowed") is True
            ][:4]
            blocked = [
                name
                for name, item in self._state["permission_model"].items()
                if item.get("allowed") is False
            ][:3]
            if allowed:
                parts.append(f"(permissions-allowed: {'; '.join(allowed)})")
            if blocked:
                parts.append(f"(permissions-blocked: {'; '.join(blocked)})")
        consents = self.consents()
        if consents:
            items = "; ".join(
                f"{c.get('person')}/{c.get('consent_type')}={'yes' if c.get('value') else 'no'}"
                for c in consents[:6]
            )
            parts.append(f"(consents: {items})")
        return "\n".join(parts)

    def context_for_prompt(self) -> str:
        if self._state.get("first_session_date") is None:
            return ""

        parts: list[str] = []
        days = self.days_together
        if days is not None:
            if days == 0:
                parts.append('(relationship :note "First session today.")')
            else:
                parts.append(f"(relationship :days-together {days})")

        sessions = self.session_count
        convos = self.conversation_count
        if sessions > 0:
            parts.append(f"(relationship :sessions {sessions} :conversations {convos})")
        parts.append(f"(relationship :trust {self.trust:.2f} :intimacy {self.intimacy:.2f})")

        rel_ctx = self.relational_context_for_prompt()
        if rel_ctx:
            parts.append(rel_ctx)

        return "\n".join(parts)
