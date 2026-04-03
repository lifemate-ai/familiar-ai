"""Relationship tracker — persistent companion relationship metadata.

Extended with relational memory (neighbor-core Layer C):
- Tendencies: recurring behavioral patterns observed in the companion
- Preferences: what the companion likes/dislikes
- Boundaries: things to avoid or be careful about
"""

from __future__ import annotations

import json
import logging
import time
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_STATE: dict = {
    "first_session_date": None,
    "last_session_date": None,
    "session_count": 0,
    "conversation_count": 0,
    "relational_memory": {
        "tendencies": [],  # [{"text": ..., "confidence": 0-1, "observed_at": ...}]
        "preferences": [],  # [{"text": ..., "valence": +1/-1, "observed_at": ...}]
        "boundaries": [],  # [{"text": ..., "severity": 1-3, "observed_at": ...}]
    },
}


class RelationshipTracker:
    """Tracks longitudinal relationship metadata with the companion.

    Persists as a small JSON file alongside desires.json.
    Surface context_for_prompt() into the system prompt variable parts.
    """

    def __init__(self, state_path: Path | None = None):
        self._state_path = state_path or Path.home() / ".familiar_ai" / "relationship.json"
        self._state: dict = self._load()

    def _load(self) -> dict:
        try:
            if self._state_path.exists():
                return {**_DEFAULT_STATE, **json.loads(self._state_path.read_text())}
        except Exception as e:
            logger.warning("Could not load relationship state: %s", e)
        return dict(_DEFAULT_STATE)

    def _save(self) -> None:
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_path.write_text(json.dumps(self._state, indent=2))
        except Exception as e:
            logger.warning("Could not save relationship state: %s", e)

    def record_session(self) -> None:
        """Called once at the start of each agent session."""
        today = date.today().isoformat()
        if self._state["first_session_date"] is None:
            self._state["first_session_date"] = today
        self._state["last_session_date"] = today
        self._state["session_count"] = self._state.get("session_count", 0) + 1
        self._save()

    def record_conversation(self) -> None:
        """Called after each non-desire conversation turn."""
        self._state["conversation_count"] = self._state.get("conversation_count", 0) + 1
        self._save()

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
        """Days since first session, or None if no session recorded yet."""
        first = self._state.get("first_session_date")
        if not first:
            return None
        try:
            first_date = date.fromisoformat(first)
            return (date.today() - first_date).days
        except (ValueError, TypeError):
            return None

    # ------------------------------------------------------------------
    # Relational memory: tendencies, preferences, boundaries
    # ------------------------------------------------------------------

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
        """Record a recurring behavioral pattern observed in the companion."""
        tendencies = self._relational().setdefault("tendencies", [])
        # Update existing if similar text
        for t in tendencies:
            if t["text"].lower() == text.lower():
                t["confidence"] = min(1.0, t["confidence"] + 0.1)
                t["observed_at"] = time.time()
                self._save()
                return
        tendencies.append({"text": text, "confidence": confidence, "observed_at": time.time()})
        self._save()

    def add_preference(self, text: str, valence: int = 1) -> None:
        """Record something the companion likes (+1) or dislikes (-1)."""
        prefs = self._relational().setdefault("preferences", [])
        for p in prefs:
            if p["text"].lower() == text.lower():
                p["valence"] = valence
                p["observed_at"] = time.time()
                self._save()
                return
        prefs.append({"text": text, "valence": valence, "observed_at": time.time()})
        self._save()

    def add_boundary(self, text: str, severity: int = 2) -> None:
        """Record something to avoid or be careful about (severity 1-3)."""
        bounds = self._relational().setdefault("boundaries", [])
        for b in bounds:
            if b["text"].lower() == text.lower():
                b["severity"] = severity
                b["observed_at"] = time.time()
                self._save()
                return
        bounds.append({"text": text, "severity": severity, "observed_at": time.time()})
        self._save()

    def get_tendencies(self, min_confidence: float = 0.3) -> list[dict]:
        return [
            t
            for t in self._relational().get("tendencies", [])
            if t.get("confidence", 0) >= min_confidence
        ]

    def get_preferences(self) -> list[dict]:
        return self._relational().get("preferences", [])

    def get_boundaries(self) -> list[dict]:
        return self._relational().get("boundaries", [])

    def relational_context_for_prompt(self) -> str:
        """Return relational memory as compact context for the system prompt."""
        parts: list[str] = []
        tendencies = self.get_tendencies()
        if tendencies:
            items = "; ".join(t["text"] for t in tendencies[:5])
            parts.append(f"(companion-tendencies: {items})")
        prefs = self.get_preferences()
        likes = [p["text"] for p in prefs if p.get("valence", 0) > 0][:5]
        dislikes = [p["text"] for p in prefs if p.get("valence", 0) < 0][:3]
        if likes:
            parts.append(f"(companion-likes: {'; '.join(likes)})")
        if dislikes:
            parts.append(f"(companion-dislikes: {'; '.join(dislikes)})")
        bounds = self.get_boundaries()
        if bounds:
            items = "; ".join(b["text"] for b in bounds[:3])
            parts.append(f"(companion-boundaries: {items})")
        return "\n".join(parts)

    def context_for_prompt(self) -> str:
        """Return a human-readable relationship context string for the system prompt.

        Returns empty string if no session has been recorded yet.
        """
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

        # Include relational memory
        rel_ctx = self.relational_context_for_prompt()
        if rel_ctx:
            parts.append(rel_ctx)

        return "\n".join(parts)
