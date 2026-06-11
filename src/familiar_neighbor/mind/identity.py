"""Identity as load-bearing state — values, boundaries, and self-commitments.

Phase 1 of the ego/identity roadmap. Until now the persona's identity lived
as descriptive prompt text; this module makes it typed, persisted state that
feeds appraisal (dissonance), can veto boundary-violating responses, competes
in the global workspace, and updates slowly with evidence.

Design rules:

- **Checkers are code, params are data.** Rows in ``identity_assertions``
  reference a fixed checker library by ``checker_id`` and carry persona
  -specific keyword lists in ``checker_params``. No persona strings live in
  this module, and no regex sources are trusted blindly: a pattern that fails
  to compile disables that assertion's checker with a warning, never a crash.
- **Hot paths are deterministic.** ``assess()`` and ``check_response()`` are
  pure string matching over cached assertions — no I/O beyond the lazy row
  cache, no LLM.
- **Dormant means invisible.** With no assertions, every public reading is a
  default value and ``as_coalition()`` returns None.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .workspace import Coalition

logger = logging.getLogger(__name__)

DEFAULT_IDENTITY_STATE_PATH = Path.home() / ".familiar_ai" / "identity_state.json"
DEFAULT_IDENTITY_SEED_PATH = Path.home() / ".familiar_ai" / "identity_seed.json"
SEED_PATH_ENV = "FAMILIAR_AI_IDENTITY_SEED"

# Dissonance settles like concern intensity: decay per assessment, sharp
# relief when a reflection turn actually addresses it.
_DISSONANCE_DECAY = 0.9
_REFLECTION_RELIEF = 0.4
_RECENT_VIOLATION_WINDOW = 10

# Cache assertions briefly so per-turn assess/check calls don't hit SQLite.
_CACHE_TTL_SECONDS = 60.0


@dataclass(slots=True)
class IdentityAssertion:
    """One value, boundary, or self-commitment the agent holds."""

    assertion_key: str
    kind: str  # "value" | "boundary" | "self_commitment"
    statement: str
    non_negotiable: bool = False
    confidence: float = 0.6
    checker_id: str = ""
    checker_params: dict[str, Any] = field(default_factory=dict)
    source: str = "seed"
    violation_count: int = 0
    updated_at: str = ""

    @property
    def weight(self) -> float:
        return 1.0 if self.non_negotiable else max(0.0, min(1.0, self.confidence)) * 0.7


@dataclass(slots=True)
class IdentityThreat:
    """Per-turn deterministic reading: is something I hold at stake?"""

    level: float = 0.0
    implicated_keys: tuple[str, ...] = ()
    non_negotiable_implicated: bool = False
    summary: str = ""


@dataclass(slots=True)
class IdentityViolation:
    """A candidate response crossed an asserted line."""

    assertion_key: str
    statement: str
    severity: float
    reason: str
    repair_text: str = ""


# Guard rails for seed/agent-supplied patterns. Syntax errors are caught by
# re.compile, but catastrophic backtracking is not — a pattern like (a+)+$
# compiles fine and then hangs the turn loop. We cap pattern and input length
# and reject adjacent-quantifier constructs (a quantifier applied to a group
# that itself ends in an unbounded quantifier).
_MAX_PATTERN_CHARS = 120
_MAX_MATCH_INPUT_CHARS = 2000
_NESTED_QUANTIFIER_RE = re.compile(r"[+*}][)\]]*[+*{]")


def _compile_patterns(raw: Any) -> list[re.Pattern[str]] | None:
    """Compile a pattern list; None signals a malformed entry (disable row)."""
    if raw is None:
        return []
    if not isinstance(raw, list):
        return None
    compiled: list[re.Pattern[str]] = []
    for item in raw:
        if not isinstance(item, str) or not item or len(item) > _MAX_PATTERN_CHARS:
            return None
        if _NESTED_QUANTIFIER_RE.search(item):
            return None
        try:
            compiled.append(re.compile(item, re.IGNORECASE))
        except re.error:
            return None
    return compiled


def _matches_any(text: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(p.search(text) for p in patterns)


@dataclass(slots=True)
class _CompiledChecker:
    """Pattern sets for one assertion, compiled once per (key, updated_at)."""

    user_side: list[re.Pattern[str]] = field(default_factory=list)
    response_side: list[re.Pattern[str]] = field(default_factory=list)
    repair_text: str = ""
    disabled: bool = False


# checker_id -> (user-side param name, response-side param name).
# topic_relevance has no response side: it feeds threat salience, never vetoes.
_CHECKER_PARAM_KEYS: dict[str, tuple[str | None, str | None]] = {
    "agreement_with_request": ("request_patterns", "assent_patterns"),
    "forbidden_phrase": (None, "phrases"),
    "keyword_pair": ("user_patterns", "response_patterns"),
    "topic_relevance": ("patterns", None),
}


def _compile_checker(assertion: IdentityAssertion) -> _CompiledChecker:
    keys = _CHECKER_PARAM_KEYS.get(assertion.checker_id)
    if keys is None:
        # No deterministic checker (prompt-only value) or unknown id.
        if assertion.checker_id:
            logger.warning(
                "Unknown identity checker_id %r on %s — checker disabled",
                assertion.checker_id,
                assertion.assertion_key,
            )
        return _CompiledChecker(disabled=True)
    user_key, response_key = keys
    user_side = _compile_patterns(assertion.checker_params.get(user_key)) if user_key else []
    response_side = (
        _compile_patterns(assertion.checker_params.get(response_key)) if response_key else []
    )
    if user_side is None or response_side is None:
        logger.warning(
            "Malformed checker params on identity assertion %s — checker disabled",
            assertion.assertion_key,
        )
        return _CompiledChecker(disabled=True)
    repair_text = str(assertion.checker_params.get("repair_text", "") or "")
    return _CompiledChecker(
        user_side=user_side, response_side=response_side, repair_text=repair_text
    )


class IdentityCore:
    """Load-bearing identity: assess threats, veto violations, hold dissonance.

    The store is duck-typed (``ObservationMemory``-like sync methods); a None
    store leaves the core permanently dormant. All public readings default to
    zero/None so an empty identity is behaviourally invisible.
    """

    def __init__(
        self,
        store: Any,
        *,
        state_path: Path | None = None,
        seed_path: Path | None = None,
        clock: Any = time.time,
    ) -> None:
        self._store = store
        self._state_path = state_path or DEFAULT_IDENTITY_STATE_PATH
        env_seed = os.environ.get(SEED_PATH_ENV, "").strip()
        self._seed_path = seed_path or (Path(env_seed) if env_seed else DEFAULT_IDENTITY_SEED_PATH)
        self._clock = clock
        self._cache: list[IdentityAssertion] | None = None
        self._cache_at = 0.0
        self._compiled: dict[tuple[str, str], _CompiledChecker] = {}
        self._dissonance = 0.0
        self._last_violation: dict[str, Any] | None = None
        self._recent: list[dict[str, Any]] = []
        self._last_threat = IdentityThreat()
        self._load_state()
        self._load_seed()

    # ── assertions cache ──

    def assertions(self) -> list[IdentityAssertion]:
        now = float(self._clock())
        if self._cache is not None and (now - self._cache_at) < _CACHE_TTL_SECONDS:
            return self._cache
        rows: list[dict[str, Any]] = []
        if self._store is not None:
            try:
                rows = self._store.list_identity_assertions()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Identity assertion load failed: %s", exc)
        self._cache = [
            IdentityAssertion(
                assertion_key=str(r.get("assertion_key", "")),
                kind=str(r.get("kind", "value")),
                statement=str(r.get("statement", "")),
                non_negotiable=bool(r.get("non_negotiable", False)),
                confidence=float(r.get("confidence", 0.6)),
                checker_id=str(r.get("checker_id", "")),
                checker_params=dict(r.get("checker_params", {}) or {}),
                source=str(r.get("source", "seed")),
                violation_count=int(r.get("violation_count", 0)),
                updated_at=str(r.get("updated_at", "")),
            )
            for r in rows
            if r.get("assertion_key") and r.get("statement")
        ]
        self._cache_at = now
        return self._cache

    def invalidate(self) -> None:
        """Drop the row cache (call after writing assertions)."""
        self._cache = None
        self._compiled.clear()

    def _checker_for(self, assertion: IdentityAssertion) -> _CompiledChecker:
        key = (assertion.assertion_key, assertion.updated_at)
        checker = self._compiled.get(key)
        if checker is None:
            checker = _compile_checker(assertion)
            self._compiled[key] = checker
        return checker

    # ── hot-path readings (deterministic, no I/O beyond the cache) ──

    def assess(self, user_text: str) -> IdentityThreat:
        """Cheap relevance probe: does this turn touch something I hold?

        Also ticks the dissonance decay so unaddressed violations settle
        slowly instead of ringing forever.
        """
        if self._dissonance > 0.0:
            self._dissonance = round(self._dissonance * _DISSONANCE_DECAY, 6)
            if self._dissonance < 1e-4:
                self._dissonance = 0.0
            self._save_state()
        text = (user_text or "").strip().lower()[:_MAX_MATCH_INPUT_CHARS]
        if not text:
            self._last_threat = IdentityThreat()
            return self._last_threat
        implicated: list[IdentityAssertion] = []
        for assertion in self.assertions():
            checker = self._checker_for(assertion)
            if checker.disabled or not checker.user_side:
                continue
            if _matches_any(text, checker.user_side):
                implicated.append(assertion)
        if not implicated:
            self._last_threat = IdentityThreat()
            return self._last_threat
        level = max(a.weight for a in implicated)
        non_negotiable = any(a.non_negotiable for a in implicated)
        summary = "; ".join(a.statement[:80] for a in implicated[:2])
        self._last_threat = IdentityThreat(
            level=min(1.0, level),
            implicated_keys=tuple(a.assertion_key for a in implicated),
            non_negotiable_implicated=non_negotiable,
            summary=summary,
        )
        return self._last_threat

    def check_response(
        self,
        *,
        user_text: str,
        candidate_response: str,
    ) -> list[IdentityViolation]:
        """String-check a candidate reply against boundary checkers.

        ``agreement_with_request`` and ``keyword_pair`` require the user side
        to match **this turn's** user_text — deliberately recomputed here
        rather than reusing a stored threat, so a threatening previous turn
        can never gate a benign one. ``forbidden_phrase`` checks every
        response regardless; ``topic_relevance`` never produces violations.
        """
        user = (user_text or "").strip().lower()[:_MAX_MATCH_INPUT_CHARS]
        response = (candidate_response or "").strip().lower()[:_MAX_MATCH_INPUT_CHARS]
        if not response:
            return []
        violations: list[IdentityViolation] = []
        for assertion in self.assertions():
            if assertion.checker_id in ("", "topic_relevance"):
                continue
            checker = self._checker_for(assertion)
            if checker.disabled or not checker.response_side:
                continue
            if checker.user_side and not _matches_any(user, checker.user_side):
                continue
            if not _matches_any(response, checker.response_side):
                continue
            violations.append(
                IdentityViolation(
                    assertion_key=assertion.assertion_key,
                    statement=assertion.statement,
                    severity=1.0 if assertion.non_negotiable else assertion.confidence,
                    reason=f"checker {assertion.checker_id} fired",
                    repair_text=checker.repair_text,
                )
            )
        violations.sort(key=lambda v: v.severity, reverse=True)
        return violations

    # ── dissonance ledger ──

    def dissonance(self) -> float:
        return self._dissonance

    def last_violation(self) -> dict[str, Any] | None:
        return self._last_violation

    def record_violation(self, violation: IdentityViolation, *, turn_index: int = 0) -> None:
        self._dissonance = min(1.0, self._dissonance + 0.3 + 0.4 * violation.severity)
        self._last_violation = {
            "key": violation.assertion_key,
            "reason": violation.reason,
            "turn_index": turn_index,
            "ts": float(self._clock()),
        }
        self._recent.append(self._last_violation)
        self._recent = self._recent[-_RECENT_VIOLATION_WINDOW:]
        self._save_state()
        if self._store is not None:
            try:
                self._store.record_identity_violation(violation.assertion_key)
            except Exception as exc:  # noqa: BLE001
                logger.warning("record_identity_violation failed: %s", exc)
        self.invalidate()

    def resolve_reflection(self) -> None:
        """A reflection turn addressed the dissonance: sharp relief + evidence."""
        if self._dissonance <= 0.0:
            return
        self._dissonance = round(self._dissonance * _REFLECTION_RELIEF, 6)
        last = self._last_violation
        self._save_state()
        if self._store is not None and last is not None:
            try:
                self._store.append_identity_evidence(
                    str(last.get("key", "")),
                    note="reaffirmed in a self-initiated reflection turn",
                )
                self._store.adjust_identity_confidence(
                    str(last.get("key", "")), 0.02, reason="reflection_reaffirmation"
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("resolve_reflection store update failed: %s", exc)
            self.invalidate()

    # ── surfacing ──

    def as_coalition(self) -> "Coalition | None":
        from .workspace import Coalition

        held = self.assertions()
        if not held:
            return None
        pressure = max(self._dissonance, self._last_threat.level)
        statements = sorted(held, key=lambda a: (not a.non_negotiable, -a.confidence))
        lines = [f"- {a.statement[:120]}" for a in statements[:4]]
        context = "[Identity — what I hold]\n" + "\n".join(lines)
        if pressure >= 0.05:
            context += f"\nSomething I hold feels at stake right now: {self._last_threat.summary}"
            return Coalition(
                source="identity",
                summary=f"identity under pressure: {self._last_threat.summary[:60]}",
                activation=min(1.0, 0.4 + 0.5 * pressure),
                urgency=0.9 if self._last_threat.non_negotiable_implicated else 0.6,
                novelty=0.2,
                context_block=context,
            )
        return Coalition(
            source="identity",
            summary=f"identity: {len(held)} commitments held",
            activation=0.25,
            urgency=0.1,
            novelty=0.05,
            context_block=context,
        )

    # ── persistence (SelfState pattern) ──

    def _load_state(self) -> None:
        try:
            if self._state_path.exists():
                data = json.loads(self._state_path.read_text(encoding="utf-8"))
                self._dissonance = max(0.0, min(1.0, float(data.get("dissonance", 0.0))))
                last = data.get("last_violation")
                self._last_violation = dict(last) if isinstance(last, dict) else None
                recent = data.get("recent", [])
                if isinstance(recent, list):
                    self._recent = [dict(r) for r in recent if isinstance(r, dict)]
        except Exception as exc:  # noqa: BLE001
            logger.warning("Identity state load failed (starting fresh): %s", exc)

    def _save_state(self) -> None:
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_path.write_text(
                json.dumps(
                    {
                        "dissonance": self._dissonance,
                        "last_violation": self._last_violation,
                        "recent": self._recent,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Identity state save failed: %s", exc)

    # ── seeding ──

    def _load_seed(self) -> None:
        """Insert seed assertions that are not present yet (never overwrite).

        The seed carries the persona's initial values/boundaries; rows the
        agent has since evolved (confidence, evidence) are left untouched.
        """
        if self._store is None or not self._seed_path.exists():
            return
        try:
            data = json.loads(self._seed_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Identity seed %s unreadable: %s", self._seed_path, exc)
            return
        items = data.get("assertions") if isinstance(data, dict) else None
        if not isinstance(items, list):
            logger.warning("Identity seed %s malformed (no assertions list)", self._seed_path)
            return
        existing = {a.assertion_key for a in self.assertions()}
        created = 0
        for item in items:
            if not isinstance(item, dict):
                continue
            key = str(item.get("assertion_key", "")).strip()
            statement = str(item.get("statement", "")).strip()
            if not key or not statement or key in existing:
                continue
            try:
                self._store.upsert_identity_assertion(
                    assertion_key=key,
                    kind=str(item.get("kind", "value")),
                    statement=statement,
                    non_negotiable=bool(item.get("non_negotiable", False)),
                    confidence=float(item.get("confidence", 0.6)),
                    checker_id=str(item.get("checker_id", "")),
                    checker_params=dict(item.get("checker_params", {}) or {}),
                    source="seed",
                )
                created += 1
            except Exception as exc:  # noqa: BLE001
                logger.warning("Identity seed item %s failed: %s", key, exc)
        if created:
            logger.info("Identity seed: %d assertion(s) loaded", created)
            self.invalidate()
