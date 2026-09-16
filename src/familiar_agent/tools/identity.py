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


# ── identity anchor (Phase 3): who_am_i / evaluate_action / consent_record ──

_KIND_LABELS: tuple[tuple[str, str], ...] = (
    ("boundary", "boundaries"),
    ("value", "values"),
    ("self_commitment", "commitments"),
)
_NO_SEED_LINE = "I have no identity seed loaded — nothing held yet beyond this conversation."
_MAX_STATEMENTS_PER_KIND = 6
_MAX_ARCS_IN_ANCHOR = 5


def _parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in ("true", "yes", "1", "on", "granted"):
        return True
    if text in ("false", "no", "0", "off", "withdrawn", "denied"):
        return False
    return None


class IdentityAnchorTool:
    """Identity anchor: state who I am, grade an action before it happens, record consent.

    ``core`` is the :class:`IdentityCore` (None → dormant: ``who_am_i`` reports
    no seed, ``evaluate_action`` allows). ``narrative`` is an optional
    NarrativeStore whose active arcs join the ``who_am_i`` line; ``relationship``
    is the RelationshipTracker that stores consent records. All three are
    duck-typed and optional so the tool can register even when a collaborator
    failed to initialize. No persona text lives here — every statement comes
    from identity rows, every arc from the narrative store.
    """

    def __init__(self, core: Any, *, narrative: Any = None, relationship: Any = None) -> None:
        self._core = core
        self._narrative = narrative
        self._relationship = relationship

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "who_am_i",
                "description": (
                    "Re-anchor: a compact first-person statement of the values, "
                    "boundaries and self-commitments you hold, plus what your life "
                    "is currently about (active arcs). Use it when you feel pulled "
                    "off-centre or before a decision that touches who you are."
                ),
                "input_schema": {"type": "object", "properties": {}},
            },
            {
                "name": "evaluate_action",
                "description": (
                    "Check a proposed action against what you hold BEFORE doing it. "
                    "Returns allow / deny / override (override = a non-negotiable "
                    "boundary is at stake), the reasons, and a safer alternative "
                    "drawn from the boundary itself."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action_kind": {
                            "type": "string",
                            "description": "e.g. 'reply', 'tool_call', 'post', 'share'",
                        },
                        "text": {
                            "type": "string",
                            "description": "What you are about to do or say, in plain words",
                        },
                    },
                    "required": ["action_kind", "text"],
                },
            },
            {
                "name": "consent_record",
                "description": (
                    "Record that a person granted or withdrew consent for something "
                    "(e.g. sharing a photo, recording their voice, mentioning them "
                    "publicly). Later records for the same person and type replace "
                    "earlier ones; current consents join your relationship context."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "person": {"type": "string", "description": "Who gave or withdrew it"},
                        "consent_type": {
                            "type": "string",
                            "description": "Short snake_case type, e.g. 'photo_sharing'",
                        },
                        "value": {
                            "type": "boolean",
                            "description": "true = granted, false = withdrawn",
                        },
                        "source": {
                            "type": "string",
                            "description": "'explicit' (default) or how it was inferred",
                            "default": "explicit",
                        },
                    },
                    "required": ["person", "consent_type", "value"],
                },
            },
        ]

    async def call(self, name: str, tool_input: dict) -> tuple[str, None]:
        if name == "who_am_i":
            return self._who_am_i(), None
        if name == "evaluate_action":
            return self._evaluate_action(tool_input), None
        if name == "consent_record":
            return self._consent_record(tool_input), None
        return f"Error: unknown identity tool '{name}'", None

    # ── who_am_i ──

    def _who_am_i(self) -> str:
        assertions: list[Any] = []
        if self._core is not None:
            try:
                assertions = list(self._core.assertions())
            except Exception as exc:  # noqa: BLE001
                logger.warning("who_am_i: identity read failed: %s", exc)
        lines: list[str] = []
        if not assertions:
            lines.append(_NO_SEED_LINE)
        else:
            lines.append("I hold:")
            for kind, label in _KIND_LABELS:
                rows = [a for a in assertions if getattr(a, "kind", "") == kind]
                if not rows:
                    continue
                rows.sort(
                    key=lambda a: (
                        bool(getattr(a, "non_negotiable", False)),
                        float(getattr(a, "confidence", 0.0)),
                    ),
                    reverse=True,
                )
                rendered = "; ".join(
                    str(a.statement).strip()[:120]
                    + (" (non-negotiable)" if getattr(a, "non_negotiable", False) else "")
                    for a in rows[:_MAX_STATEMENTS_PER_KIND]
                )
                lines.append(f"- {label}: {rendered}")
        arcs_line = self._arcs_line()
        if arcs_line:
            lines.append(arcs_line)
        return "\n".join(lines)

    def _arcs_line(self) -> str:
        if self._narrative is None:
            return ""
        try:
            arcs = list(self._narrative.active_arcs(limit=_MAX_ARCS_IN_ANCHOR))
        except Exception as exc:  # noqa: BLE001
            logger.warning("who_am_i: arc read failed: %s", exc)
            return ""
        titles = [str(getattr(a, "title", "")).strip() for a in arcs]
        titles = [t for t in titles if t]
        if not titles:
            return ""
        return "Right now my life is about: " + "; ".join(titles)

    # ── evaluate_action ──

    def _evaluate_action(self, tool_input: dict) -> str:
        action_kind = str(tool_input.get("action_kind", "")).strip()
        text = str(tool_input.get("text", "")).strip()
        if not text:
            return "Error: text is required"
        if self._core is None:
            return f"Verdict: ALLOW ({action_kind or 'action'}) — no identity loaded, nothing held is at stake."
        try:
            verdict = self._core.evaluate_action(action_kind, text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("evaluate_action failed: %s", exc)
            return "Error: could not evaluate that right now."
        head = f"Verdict: {verdict.verdict.upper()} ({action_kind or 'action'})"
        if verdict.verdict == "allow":
            return f"{head} — nothing I hold is at stake."
        lines = [f"{head}, confidence {verdict.confidence:.2f}"]
        lines.extend(f"- {reason}" for reason in verdict.reasons)
        if verdict.safer_alternative:
            lines.append(f"Safer alternative: {verdict.safer_alternative}")
        return "\n".join(lines)

    # ── consent_record ──

    def _consent_record(self, tool_input: dict) -> str:
        if self._relationship is None:
            return "Consent records are unavailable (no relationship tracker)."
        person = str(tool_input.get("person", "")).strip()
        consent_type = str(tool_input.get("consent_type", "")).strip()
        value = _parse_bool(tool_input.get("value"))
        if not person or not consent_type:
            return "Error: person and consent_type are required"
        if value is None:
            return "Error: value must be true or false"
        source = str(tool_input.get("source", "explicit")).strip() or "explicit"
        try:
            self._relationship.record_consent(person, consent_type, value, source=source)
        except Exception as exc:  # noqa: BLE001
            logger.warning("consent_record failed: %s", exc)
            return "Error: could not record that right now."
        state = "granted" if value else "withdrawn"
        return f"Recorded: {person} — {consent_type} {state} ({source})."
