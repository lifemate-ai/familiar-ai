"""Routine tools — the agent authors its own recurring schedule.

Self-authored time is identity structure: what a mind chooses to do every
day at ten is part of who it is. Guardrails (interval floor, count cap, the
seed-vs-agent trust split) are enforced in the RoutineStore, not here — a
tool wrapper must not be the security boundary.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_ROUTINE_COMMIT_DEF = {
    "name": "routine_commit",
    "description": (
        "Create or update one of YOUR OWN recurring routines (a daily reading "
        "hour, an evening reflection, a periodic look outside). Schedule formats: "
        "'daily@HH:MM' or 'interval:<seconds>'. When it comes due, the routine "
        "surfaces as a reminder through the normal idle flow. Pass routine_id to "
        "update an existing one."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Short name for the routine"},
            "schedule": {"type": "string", "description": "daily@HH:MM or interval:<seconds>"},
            "prompt": {
                "type": "string",
                "description": "What to do when it fires — written to your future self",
            },
            "priority": {
                "type": "integer",
                "description": "0-3; >=2 may surface even in quiet hours",
            },
            "routine_id": {"type": "string", "description": "Existing routine to update"},
        },
        "required": ["name", "schedule", "prompt"],
    },
}

_ROUTINE_REVIEW_DEF = {
    "name": "routine_review",
    "description": "List your routines — schedule, prompt, source, and enabled state.",
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

_ROUTINE_DROP_DEF = {
    "name": "routine_drop",
    "description": (
        "Disable one of your own routines by routine_id. Seed routines are "
        "operator-owned and cannot be dropped from here."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"routine_id": {"type": "string"}},
        "required": ["routine_id"],
    },
}


class RoutineTool:
    def __init__(self, store: Any) -> None:
        self._store = store

    def get_tool_definitions(self) -> list[dict]:
        return [_ROUTINE_COMMIT_DEF, _ROUTINE_REVIEW_DEF, _ROUTINE_DROP_DEF]

    async def call(self, name: str, tool_input: dict) -> tuple[str, None]:
        if name == "routine_commit":
            return self._commit(tool_input), None
        if name == "routine_review":
            return self._review(), None
        if name == "routine_drop":
            return self._drop(tool_input), None
        return f"Error: unknown routine tool '{name}'", None

    def _commit(self, tool_input: dict) -> str:
        routine, message = self._store.commit(
            name=str(tool_input.get("name", "")),
            schedule=str(tool_input.get("schedule", "")),
            prompt=str(tool_input.get("prompt", "")),
            priority=int(tool_input.get("priority", 1) or 1),
            routine_id=(str(tool_input["routine_id"]) if tool_input.get("routine_id") else None),
            source="agent",
        )
        if routine is None:
            return f"Error: {message}"
        return f"Routine {message}: [{routine.routine_id}] {routine.name} ({routine.schedule})"

    def _review(self) -> str:
        routines = self._store.list_routines()
        if not routines:
            return "No routines yet — routine_commit creates one."
        lines = ["Your routines:"]
        for r in routines:
            state = "" if r.enabled else " (disabled)"
            owner = " [seed]" if r.source == "seed" else ""
            lines.append(
                f"- [{r.routine_id}] {r.name} — {r.schedule}{owner}{state}: {r.prompt[:80]}"
            )
        return "\n".join(lines)

    def _drop(self, tool_input: dict) -> str:
        ok, message = self._store.drop(str(tool_input.get("routine_id", "")), source="agent")
        return message if ok else f"Error: {message}"
