"""Secretary tool: create, list, complete, and snooze commitments.

Bridges the model to the generic :class:`SQLiteCommitmentStore`. Exposes the
legacy ``get_tool_definitions()`` / async ``call()`` surface so it can be wrapped
by :class:`familiar_capabilities.commitments.CommitmentCapability`.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import datetime

from familiar_runtime.commitments import (
    Commitment,
    CommitmentKind,
    CommitmentStatus,
    SQLiteCommitmentStore,
)

# Surface this many days of commitments as "upcoming" by default.
DEFAULT_UPCOMING_HORIZON_SECONDS = 24 * 3600


def _format_due(commitment: Commitment, *, now: float) -> str:
    due = commitment.effective_due()
    if due is None:
        return "no due time"
    delta = due - now
    if delta <= 0:
        return f"overdue by {_humanize(-delta)}"
    return f"in {_humanize(delta)}"


def _humanize(seconds: float) -> str:
    seconds = abs(seconds)
    if seconds < 90:
        return f"{int(seconds)}s"
    minutes = seconds / 60
    if minutes < 90:
        return f"{int(minutes)}m"
    hours = minutes / 60
    if hours < 36:
        return f"{int(hours)}h"
    return f"{int(hours / 24)}d"


def _line(commitment: Commitment, *, now: float) -> str:
    flag = "❗" if commitment.priority >= 2 else "•"
    who = f" (for {commitment.person})" if commitment.person else ""
    return f"{flag} [{commitment.id}] {commitment.summary[:120]}{who} — {_format_due(commitment, now=now)}"


def format_commitment_line(commitment: Commitment, *, now: float) -> str:
    """Public single-line renderer (priority flag + summary + human due time)."""
    return _line(commitment, now=now)


def format_commitments_for_context(
    *,
    due: list[Commitment],
    upcoming: list[Commitment],
    now: float | None = None,
) -> str:
    """Render due + upcoming commitments for prompt injection.

    Returns an empty string when there is nothing to surface, so callers can
    cheaply skip the block.
    """
    now = time.time() if now is None else now
    blocks: list[str] = []
    if due:
        lines = "\n".join(_line(c, now=now) for c in due)
        blocks.append(f"[Reminders due now]\n{lines}")
    if upcoming:
        lines = "\n".join(_line(c, now=now) for c in upcoming)
        blocks.append(f"[Upcoming commitments]\n{lines}")
    return "\n\n".join(blocks)


class CommitmentTool:
    """Tool object exposing commitment CRUD to the ReAct loop."""

    def __init__(
        self,
        store: SQLiteCommitmentStore,
        *,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.store = store
        self._clock = clock

    def get_tool_definitions(self) -> list[dict]:
        kinds = [k.value for k in CommitmentKind]
        return [
            {
                "name": "add_commitment",
                "description": (
                    "Remember something you or the user committed to: a reminder, "
                    "appointment, promise, or follow-up. Give a due time when one is "
                    "known (due_in_minutes for relative, due_at_iso for absolute). "
                    "Use this whenever the user asks you to remind them, or when you "
                    "promise to do/check something later."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Short description of the commitment.",
                        },
                        "kind": {"type": "string", "enum": kinds},
                        "due_in_minutes": {
                            "type": "number",
                            "description": "Minutes from now until due (may be negative for past).",
                        },
                        "due_at_iso": {
                            "type": "string",
                            "description": "Absolute due time, ISO 8601 (e.g. 2026-06-11T09:00).",
                        },
                        "priority": {
                            "type": "integer",
                            "description": "0 (low) to 3 (urgent). >=2 is flagged.",
                        },
                        "person": {
                            "type": "string",
                            "description": "Who this concerns, if not the user.",
                        },
                    },
                    "required": ["summary"],
                },
            },
            {
                "name": "list_commitments",
                "description": "List remembered commitments (filter: open, due, upcoming, all).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "enum": ["open", "due", "upcoming", "all"],
                        },
                        "horizon_minutes": {
                            "type": "number",
                            "description": "Window for the 'upcoming' filter (default 24h).",
                        },
                    },
                },
            },
            {
                "name": "complete_commitment",
                "description": "Mark a commitment done by id.",
                "input_schema": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}},
                    "required": ["id"],
                },
            },
            {
                "name": "snooze_commitment",
                "description": "Hide a commitment for N minutes, then it becomes due again.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "minutes": {"type": "number"},
                    },
                    "required": ["id", "minutes"],
                },
            },
        ]

    async def call(self, name: str, tool_input: dict) -> tuple[str, None]:
        try:
            if name == "add_commitment":
                return self._add(tool_input), None
            if name == "list_commitments":
                return self._list(tool_input), None
            if name == "complete_commitment":
                return self._complete(tool_input), None
            if name == "snooze_commitment":
                return self._snooze(tool_input), None
        except KeyError as exc:
            return f"Error: {exc}", None
        except ValueError as exc:
            return f"Error: invalid input — {exc}", None
        return f"Error: unknown commitment tool '{name}'", None

    # ── handlers ──

    def _add(self, tool_input: dict) -> str:
        summary = str(tool_input.get("summary", "")).strip()
        if not summary:
            raise ValueError("summary is required")
        kind = CommitmentKind(tool_input.get("kind", CommitmentKind.REMINDER.value))
        due_at = self._resolve_due(tool_input)
        priority = int(tool_input.get("priority", 0))
        person = tool_input.get("person")
        commitment = self.store.create(
            summary=summary,
            kind=kind,
            due_at=due_at,
            priority=max(0, min(3, priority)),
            created_by="user",
            person=person,
        )
        when = _format_due(commitment, now=self._clock())
        return f"Saved: {commitment.summary} ({when}) [{commitment.id}]"

    def _resolve_due(self, tool_input: dict) -> float | None:
        if tool_input.get("due_in_minutes") is not None:
            return self._clock() + float(tool_input["due_in_minutes"]) * 60
        iso = tool_input.get("due_at_iso")
        if iso:
            return datetime.fromisoformat(str(iso)).timestamp()
        return None

    def _list(self, tool_input: dict) -> str:
        now = self._clock()
        which = str(tool_input.get("filter", "open"))
        if which == "due":
            items = self.store.list_due(now=now)
        elif which == "upcoming":
            horizon = float(tool_input.get("horizon_minutes", 0)) * 60
            horizon = horizon or DEFAULT_UPCOMING_HORIZON_SECONDS
            items = self.store.list_upcoming(now=now, horizon=horizon)
        else:  # open / all both map to active set
            items = self.store.list_open()
        if not items:
            return "No commitments."
        return "\n".join(_line(c, now=now) for c in items)

    def _complete(self, tool_input: dict) -> str:
        commitment = self.store.complete(str(tool_input["id"]))
        return f"✓ Completed: {commitment.summary}"

    def _snooze(self, tool_input: dict) -> str:
        minutes = float(tool_input["minutes"])
        until = self._clock() + minutes * 60
        commitment = self.store.snooze(str(tool_input["id"]), until=until)
        assert commitment.status is CommitmentStatus.SNOOZED
        return f"Snoozed {commitment.summary} for {_humanize(minutes * 60)}"
