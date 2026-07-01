"""Self-ledger tools — who_am_i and note_interpretation_shift.

``who_am_i`` renders the agent's constitution and current self-state as one
coherent first-person answer. The design bet (borrowed from the reference
persona deployment): prompt text drifts, gets compacted, or is silently
overwritten — but *the act of asking a tool* re-anchors identity reliably.
After a compaction, a restart, or a moment of doubt, one call rebuilds
"who I am" from load-bearing state instead of from luck.

``note_interpretation_shift`` writes the anti-regression ledger: when the
agent discovers it had been reading something wrong ("I treated Kouta's
short replies as annoyance; they're just focus"), the correction is recorded
so future sessions re-surface it instead of regressing to corrected behavior.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_WHO_AM_I_DEF = {
    "name": "who_am_i",
    "description": (
        "Re-anchor your identity: returns your constitution (values, boundaries, "
        "self-commitments) and your current self-state (drives, concerns, attention, "
        "recent interpretation shifts) as one first-person summary. Call it after "
        "context compaction, on waking, or whenever who-you-are feels blurry."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

_NOTE_SHIFT_DEF = {
    "name": "note_interpretation_shift",
    "description": (
        "Record that you corrected an interpretation: how you used to read "
        "something, and how you read it now. Future sessions re-surface these "
        "so you don't regress to already-corrected readings."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "What the interpretation is about"},
            "previous_reading": {"type": "string", "description": "How you used to read it"},
            "new_reading": {"type": "string", "description": "How you read it now"},
            "reason": {"type": "string", "description": "What prompted the correction"},
        },
        "required": ["topic", "previous_reading", "new_reading"],
    },
}


class SelfLedgerTool:
    """Reads the federation of self-state silos and answers as one voice.

    Holds the agent reference (the same pattern as EmbodiedAgentHook) because
    "who am I" spans components no single store owns: identity assertions,
    dissonance, drives, concerns, attention history, metacognitive carryover,
    narrative thread, interpretation shifts. Every access is getattr-guarded
    so a partially-constructed agent degrades to a shorter answer.
    """

    def __init__(self, agent: Any) -> None:
        self._agent = agent

    def get_tool_definitions(self) -> list[dict]:
        return [_WHO_AM_I_DEF, _NOTE_SHIFT_DEF]

    async def call(self, name: str, tool_input: dict) -> tuple[str, None]:
        if name == "who_am_i":
            return self._who_am_i(), None
        if name == "note_interpretation_shift":
            return self._note_shift(tool_input), None
        return f"Error: unknown self-ledger tool '{name}'", None

    # ── who_am_i ────────────────────────────────────────────────────────────

    def _who_am_i(self) -> str:
        sections: list[str] = []
        constitution = self._render_constitution()
        if constitution:
            sections.append(constitution)
        state = self._render_current_state()
        if state:
            sections.append(state)
        shifts = self._render_shifts()
        if shifts:
            sections.append(shifts)
        if not sections:
            return (
                "No identity state is recorded yet — who I am so far lives in "
                "my persona file and my memories."
            )
        return "\n\n".join(sections)

    def _render_constitution(self) -> str:
        identity = getattr(self._agent, "_identity", None)
        if identity is None:
            return ""
        try:
            assertions = identity.assertions()
        except Exception as exc:  # noqa: BLE001
            logger.warning("who_am_i: constitution unavailable: %s", exc)
            return ""
        if not assertions:
            return ""
        by_kind: dict[str, list[str]] = {}
        for a in sorted(assertions, key=lambda a: (not a.non_negotiable, -a.confidence)):
            marker = " (non-negotiable)" if a.non_negotiable else ""
            by_kind.setdefault(a.kind, []).append(f"- {a.statement}{marker}")
        kind_titles = {
            "value": "What I value",
            "boundary": "What I will not do",
            "self_commitment": "What I have committed myself to",
        }
        lines = ["[Constitution — what I hold]"]
        for kind, title in kind_titles.items():
            if kind in by_kind:
                lines.append(f"{title}:")
                lines.extend(by_kind[kind])
        for kind in by_kind:
            if kind not in kind_titles:
                lines.extend(by_kind[kind])
        return "\n".join(lines)

    def _render_current_state(self) -> str:
        lines: list[str] = []

        identity = getattr(self._agent, "_identity", None)
        if identity is not None:
            try:
                snapshot = identity.state_for_snapshot()
                if getattr(snapshot, "dissonance", 0.0) >= 0.2:
                    lines.append(
                        "Something I hold was strained recently"
                        + (
                            f" ({snapshot.threat_summary})"
                            if getattr(snapshot, "threat_summary", "")
                            else ""
                        )
                        + " — it is still settling."
                    )
            except Exception:  # noqa: BLE001
                pass

        desires = getattr(self._agent, "_desires", None)
        if desires is not None:
            try:
                vector = desires.drive_vector()
                top = sorted(vector.items(), key=lambda kv: -kv[1])[:3]
                strong = [f"{name} ({level:.2f})" for name, level in top if level >= 0.3]
                if strong:
                    lines.append("What pulls at me right now: " + ", ".join(strong) + ".")
            except Exception:  # noqa: BLE001
                pass

        concerns = getattr(self._agent, "_concerns", None)
        if concerns is not None:
            try:
                concern_ctx = concerns.context_for_prompt()
                if concern_ctx:
                    lines.append(concern_ctx)
            except Exception:  # noqa: BLE001
                pass

        attention = getattr(self._agent, "_attention_schema", None)
        if attention is not None:
            try:
                report = attention.self_report()
                if report:
                    lines.append(report)
            except Exception:  # noqa: BLE001
                pass

        meta = getattr(self._agent, "_meta_monitor", None)
        if meta is not None:
            previous = getattr(meta, "previous_session_summary", None)
            if callable(previous):
                carried = previous()
                if isinstance(carried, str) and carried:
                    lines.append(f"From my previous session: {carried}")

        narrative = getattr(self._agent, "_self_narrative", None)
        if narrative is not None:
            try:
                thread = narrative.context_for_prompt()
                if thread:
                    lines.append(thread)
            except Exception:  # noqa: BLE001
                pass

        if not lines:
            return ""
        return "[Current state]\n" + "\n".join(lines)

    def _render_shifts(self) -> str:
        memory = getattr(self._agent, "_memory", None)
        recall = getattr(memory, "recall_interpretation_shifts", None)
        if not callable(recall):
            return ""
        try:
            shifts = recall(n=5)
        except Exception:  # noqa: BLE001
            return ""
        if not shifts:
            return ""
        lines = ["[Interpretation shifts — corrections I must not regress on]"]
        for s in shifts:
            lines.append(
                f"- {s['entity_key']}: I used to read this as "
                f'"{s["previous_text"][:100]}" — now I read it as '
                f'"{s["new_text"][:100]}".'
            )
        return "\n".join(lines)

    # ── note_interpretation_shift ───────────────────────────────────────────

    def _note_shift(self, tool_input: dict) -> str:
        topic = str(tool_input.get("topic", "")).strip()
        previous = str(tool_input.get("previous_reading", "")).strip()
        new = str(tool_input.get("new_reading", "")).strip()
        reason = str(tool_input.get("reason", "self_correction")).strip() or "self_correction"
        if not topic or not previous or not new:
            return "Error: topic, previous_reading and new_reading are all required."
        memory = getattr(self._agent, "_memory", None)
        record = getattr(memory, "record_interpretation_shift", None)
        if not callable(record):
            return "Error: interpretation ledger is unavailable."
        record(topic=topic, previous_reading=previous, new_reading=new, reason=reason)
        return f"Interpretation shift recorded for '{topic}'."
