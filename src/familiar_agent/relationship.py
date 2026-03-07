"""Relationship tracker — persistent companion relationship metadata."""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_STATE: dict = {
    "first_session_date": None,
    "last_session_date": None,
    "session_count": 0,
    "conversation_count": 0,
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

        return "\n".join(parts)
