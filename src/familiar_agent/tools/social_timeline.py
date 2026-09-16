"""Social timeline tool — read the append-only relational event ledger.

``social_timeline`` lists the most recent social events (trust/intimacy
shifts, boundaries, permissions, commitments, identity violations, person
inferences) newest-first, optionally filtered by kind or person. Read-only:
the ledger is written by the emitters, never by the model.
"""

from __future__ import annotations

import logging
from typing import Any

from familiar_neighbor.mind.social_events import SOCIAL_EVENT_KINDS, SocialEvent

logger = logging.getLogger(__name__)

_DEFAULT_LIMIT = 10
_MAX_LIMIT = 50
_PAYLOAD_KEYS_SHOWN = 3
_VALUE_WIDTH = 60

_SOCIAL_TIMELINE_DEF: dict[str, Any] = {
    "name": "social_timeline",
    "description": (
        "List what recently happened between you and the people around you: "
        "trust or intimacy shifts, boundaries, permissions, commitments made or "
        "kept, moments you strained something you hold, and what you inferred "
        "about someone. Newest first. Filter by kind or person when you need "
        "one thread of the story."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": f"How many events to list (1-{_MAX_LIMIT})",
                "default": _DEFAULT_LIMIT,
            },
            "kind": {
                "type": "string",
                "description": "Only events of this kind",
                "enum": sorted(SOCIAL_EVENT_KINDS),
            },
            "person": {
                "type": "string",
                "description": "Only events about this person (case-insensitive)",
            },
        },
        "required": [],
    },
}


def _short(value: Any) -> str:
    if isinstance(value, float):
        text = f"{value:.2f}".rstrip("0").rstrip(".")
    elif isinstance(value, bool):
        text = "yes" if value else "no"
    elif isinstance(value, (list, dict)):
        text = str(value)
    else:
        text = str(value)
    text = " ".join(text.split())
    return text if len(text) <= _VALUE_WIDTH else text[: _VALUE_WIDTH - 1] + "…"


def _format_event(event: SocialEvent) -> str:
    when = event.ts[:16].replace("T", " ")
    parts = [f"{when} {event.kind}"]
    if event.person_key:
        parts.append(f"[{event.person_key}]")
    payload_bits = [
        f"{key}={_short(value)}"
        for key, value in list(event.payload.items())[:_PAYLOAD_KEYS_SHOWN]
        if value not in (None, "", [], {})
    ]
    if payload_bits:
        parts.append(" ".join(payload_bits))
    if event.confidence is not None:
        parts.append(f"(conf {event.confidence:.2f})")
    return "- " + " ".join(parts)


class SocialTimelineTool:
    """Read-only view over a :class:`SocialEventLog` (duck-typed)."""

    def __init__(self, log: Any) -> None:
        self._log = log

    def get_tool_definitions(self) -> list[dict]:
        return [_SOCIAL_TIMELINE_DEF]

    async def call(self, name: str, tool_input: dict) -> tuple[str, None]:
        if name != "social_timeline":
            return f"Error: unknown social-timeline tool '{name}'", None
        return self._timeline(tool_input), None

    def _timeline(self, tool_input: dict) -> str:
        log = self._log
        if log is None:
            return "Error: social event log is unavailable."
        try:
            limit = int(tool_input.get("limit", _DEFAULT_LIMIT))
        except (TypeError, ValueError):
            limit = _DEFAULT_LIMIT
        limit = max(1, min(limit, _MAX_LIMIT))
        kind = str(tool_input.get("kind", "") or "").strip() or None
        if kind is not None and kind not in SOCIAL_EVENT_KINDS:
            return f"Error: unknown kind '{kind}'. Known: {', '.join(sorted(SOCIAL_EVENT_KINDS))}"
        person = str(tool_input.get("person", "") or "").strip() or None
        try:
            total = int(log.count(kind=kind, person_key=person))
            events = list(log.recent(limit, kind=kind, person_key=person))
        except Exception as exc:  # noqa: BLE001
            logger.warning("social_timeline read failed: %s", exc)
            return "Error: social event log is unavailable."
        if not events:
            scope = []
            if kind:
                scope.append(f"kind={kind}")
            if person:
                scope.append(f"person={person}")
            return (
                f"No social events recorded for {' '.join(scope)}."
                if scope
                else "No social events recorded yet."
            )
        header = f"Social timeline (newest first, {len(events)} of {total}):"
        return "\n".join([header, *(_format_event(e) for e in events)])
