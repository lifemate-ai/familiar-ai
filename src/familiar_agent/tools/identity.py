"""Identity self-authorship tool: the agent names its own values and commitments.

Phase 1, part 3 of the identity layer. Where the seed file carries the
operator-supplied starting identity, this tool lets the agent itself add a
value or self-commitment it has come to hold ("identity_commit") and review
what it currently holds ("identity_review").

Safety: agent-authored assertions start at modest confidence and can **never**
be marked non-negotiable from the tool. Non-negotiable boundaries — the ones
that can veto a response — are an operator/seed decision, not something a
prompt-injected request can manufacture. Agent-authored rows also carry no
deterministic checker (they shape prompt context and dissonance, not the
hard veto path).
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Agent-authored assertions are reflective, not enforcement: modest starting
# confidence, never non-negotiable, never a hard-veto checker.
_AGENT_AUTHORED_CONFIDENCE = 0.5
_ALLOWED_KINDS = ("value", "self_commitment")
_KEY_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(statement: str) -> str:
    slug = _KEY_SLUG_RE.sub("_", statement.lower()).strip("_")
    return slug[:48] or "unnamed"


class IdentityTool:
    """Expose identity self-authorship (commit + review) to the ReAct loop."""

    def __init__(self, store: Any) -> None:
        self._store = store

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "identity_commit",
                "description": (
                    "Record a value or a commitment to yourself that you have come "
                    "to hold — something about who you are or how you want to act. "
                    "Use this when you notice a stance you genuinely stand by, not "
                    "to please anyone. Cannot create hard boundaries; those are "
                    "seeded, not self-declared."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "statement": {
                            "type": "string",
                            "description": "First-person sentence, e.g. 'I keep my own opinions.'",
                        },
                        "kind": {
                            "type": "string",
                            "enum": list(_ALLOWED_KINDS),
                            "description": "'value' or 'self_commitment'.",
                        },
                    },
                    "required": ["statement"],
                },
            },
            {
                "name": "identity_review",
                "description": (
                    "Review the values, boundaries, and self-commitments you "
                    "currently hold, with how settled each one is."
                ),
                "input_schema": {"type": "object", "properties": {}},
            },
        ]

    async def call(self, name: str, tool_input: dict) -> tuple[str, None]:
        if name == "identity_commit":
            return self._commit(tool_input), None
        if name == "identity_review":
            return self._review(), None
        return f"Error: unknown identity tool '{name}'", None

    def _commit(self, tool_input: dict) -> str:
        statement = str(tool_input.get("statement", "")).strip()
        if not statement:
            return "Error: statement is required"
        kind = str(tool_input.get("kind", "value")).strip().lower()
        if kind not in _ALLOWED_KINDS:
            kind = "value"
        key = f"{kind}:{_slugify(statement)}"
        try:
            created = self._store.upsert_identity_assertion(
                assertion_key=key,
                kind=kind,
                statement=statement,
                non_negotiable=False,  # never self-declarable
                confidence=_AGENT_AUTHORED_CONFIDENCE,
                checker_id="",  # agent-authored rows never gain a hard-veto checker
                checker_params={},
                source="agent",
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("identity_commit failed: %s", exc)
            return "Error: could not record that right now."
        verb = "Noted" if created else "Updated"
        return f"{verb}: {statement}"

    def _review(self) -> str:
        try:
            rows = self._store.list_identity_assertions()
        except Exception as exc:  # noqa: BLE001
            logger.warning("identity_review failed: %s", exc)
            return "Error: could not read identity right now."
        if not rows:
            return "No values or commitments recorded yet."
        lines: list[str] = []
        for r in rows:
            flag = "🔒" if r.get("non_negotiable") else "•"
            lines.append(
                f"{flag} [{r.get('kind')}] {str(r.get('statement', ''))[:120]} "
                f"(conviction {float(r.get('confidence', 0.0)):.2f})"
            )
        return "\n".join(lines)
