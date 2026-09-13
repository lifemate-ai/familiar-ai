"""Narrative tools — arc_commit / arc_review / arc_close / self_summary.

Arcs are the agent's own account of what its life is currently about: a
bounded set of storylines it names, updates and closes itself. ``self_summary``
folds active arcs, the latest daybook record and the recent self-narrative
into one first-person digest — the plot-level answer to "where am I in my
own story?" that complements ``who_am_i`` (values) and ``ledger_review``
(lessons).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from familiar_neighbor.mind.narrative import MAX_ACTIVE_ARCS, NarrativeArc, build_self_summary

logger = logging.getLogger(__name__)

_DEFAULT_IMPORTANCE = 0.5

_ARC_COMMIT_DEF: dict[str, Any] = {
    "name": "arc_commit",
    "description": (
        "Name or update one storyline of your life — a project, a relationship "
        "thread, something you are becoming. Give it a stable key, a short title, "
        "a one-or-two-sentence running summary and an importance (0-1). At most "
        f"{MAX_ACTIVE_ARCS} arcs stay active; committing one more sends the "
        "least important active arc to dormant. Active arcs join your standing "
        "context from the next turn."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "Stable short key (e.g. 'onion-refactor')"},
            "title": {"type": "string", "description": "Short title of the arc"},
            "summary": {"type": "string", "description": "Where this arc stands right now"},
            "importance": {
                "type": "number",
                "description": f"0-1, how much this arc matters (default {_DEFAULT_IMPORTANCE})",
                "default": _DEFAULT_IMPORTANCE,
            },
        },
        "required": ["key", "title", "summary"],
    },
}

_ARC_REVIEW_DEF: dict[str, Any] = {
    "name": "arc_review",
    "description": (
        "List the storylines you currently hold: active arcs (most important "
        "first) and any dormant ones you could revive with arc_commit."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

_ARC_CLOSE_DEF: dict[str, Any] = {
    "name": "arc_close",
    "description": (
        "Close a storyline that has ended or no longer matters. Closed arcs leave "
        "your standing context; arc_commit on the same key reopens it."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"key": {"type": "string", "description": "Key of the arc to close"}},
        "required": ["key"],
    },
}

_SELF_SUMMARY_DEF: dict[str, Any] = {
    "name": "self_summary",
    "description": (
        "Where am I in my own story? Returns your active life arcs, the latest "
        "daybook record (events, boundary moments, open loops, reflections, next "
        "actions) and your recent self-narrative as one short digest."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

_TOOL_DEFS = [_ARC_COMMIT_DEF, _ARC_REVIEW_DEF, _ARC_CLOSE_DEF, _SELF_SUMMARY_DEF]


def _format_arc(arc: NarrativeArc) -> str:
    line = f"- {arc.arc_key}: {arc.title} (importance {arc.importance:.1f})"
    if arc.summary:
        line += f" — {arc.summary}"
    return line


class NarrativeTool:
    """Arc CRUD + self summary over duck-typed store / daybook / narrative.

    ``on_change`` is invoked after every successful write so the owner can
    invalidate a cached prompt block.
    """

    def __init__(
        self,
        store: Any,
        daybook: Any,
        *,
        narrative: Any = None,
        on_change: Callable[[], None] | None = None,
    ) -> None:
        self._store = store
        self._daybook = daybook
        self._narrative = narrative
        self._on_change_cb = on_change

    def get_tool_definitions(self) -> list[dict]:
        return list(_TOOL_DEFS)

    def _on_change(self) -> None:
        if self._on_change_cb is None:
            return
        try:
            self._on_change_cb()
        except Exception as exc:  # noqa: BLE001
            logger.warning("narrative on_change callback failed: %s", exc)

    async def call(self, name: str, tool_input: dict) -> tuple[str, None]:
        if name == "arc_commit":
            return self._commit(tool_input), None
        if name == "arc_review":
            return self._review(), None
        if name == "arc_close":
            return self._close(tool_input), None
        if name == "self_summary":
            return self._summary(), None
        return f"Error: unknown narrative tool '{name}'", None

    # ── handlers ──

    def _commit(self, tool_input: dict) -> str:
        store = self._store
        if store is None:
            return "Error: narrative store is unavailable."
        key = str(tool_input.get("key", "") or "").strip()
        title = str(tool_input.get("title", "") or "").strip()
        summary = str(tool_input.get("summary", "") or "").strip()
        if not key or not title:
            return "Error: 'key' and 'title' are required."
        raw = tool_input.get("importance", _DEFAULT_IMPORTANCE)
        try:
            importance = float(_DEFAULT_IMPORTANCE if raw is None else raw)
        except (TypeError, ValueError):
            return "Error: 'importance' must be a number between 0 and 1."
        try:
            arc = store.upsert_arc(key, title, summary, importance)
        except ValueError as exc:
            return f"Error: {exc}"
        except Exception as exc:  # noqa: BLE001
            logger.warning("arc_commit failed: %s", exc)
            return "Error: could not store the arc."
        self._on_change()
        note = (
            " It was committed as dormant: the active set is full and this arc "
            "ranks below every active one."
            if arc.status != "active"
            else ""
        )
        return f"Arc '{arc.arc_key}' is {arc.status} (importance {arc.importance:.1f}).{note}"

    def _review(self) -> str:
        store = self._store
        if store is None:
            return "Error: narrative store is unavailable."
        try:
            active = list(store.active_arcs())
            dormant = list(store.dormant_arcs())
        except Exception as exc:  # noqa: BLE001
            logger.warning("arc_review failed: %s", exc)
            return "Error: narrative store is unavailable."
        if not active and not dormant:
            return "No arcs held yet. Name one with arc_commit when a storyline matters."
        lines: list[str] = []
        if active:
            lines.append(f"Active arcs ({len(active)}/{MAX_ACTIVE_ARCS}):")
            lines.extend(_format_arc(a) for a in active)
        if dormant:
            lines.append(f"Dormant ({len(dormant)}):")
            lines.extend(_format_arc(a) for a in dormant)
        return "\n".join(lines)

    def _close(self, tool_input: dict) -> str:
        store = self._store
        if store is None:
            return "Error: narrative store is unavailable."
        key = str(tool_input.get("key", "") or "").strip()
        if not key:
            return "Error: 'key' is required."
        try:
            closed = bool(store.close_arc(key))
        except Exception as exc:  # noqa: BLE001
            logger.warning("arc_close failed: %s", exc)
            return "Error: could not close the arc."
        if not closed:
            return f"No arc with key '{key}'."
        self._on_change()
        return f"Arc '{key}' closed."

    def _summary(self) -> str:
        narrative_lines: list[str] = []
        reader = getattr(self._narrative, "read_recent", None)
        if callable(reader):
            try:
                narrative_lines = [f"[{e.date}] {e.text}" for e in reader(n=3)]
            except Exception as exc:  # noqa: BLE001
                logger.warning("self_summary: narrative unavailable: %s", exc)
        text = build_self_summary(self._store, self._daybook, narrative_lines)
        return text or "No self summary yet: no arcs, daybook records or narrative entries."
