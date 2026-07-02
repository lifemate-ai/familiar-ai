"""Reality monitor — epistemic provenance and perception-claim checking.

Waking is continuously maintained reality-testing: generation disciplined by
prediction error from the world. An ungrounded reply that *claims* fresh
perception is the agent dreaming out loud — the honesty rules in the prompt
say so, but small local models drown them. This module makes the rule state
logic, following the identity layer's discipline: checkers are code, the
pattern library is fixed data, inputs are length-capped.

Three pieces:

- ``Provenance`` + cheap mappers — epistemic origin (perceived / recalled /
  generated) derived from existing tags (coalition source, memory kind).
  Derived, never stored: no re-plumb of Coalition or the memory schema.
- ``looks_like_fresh_perception_claim`` — does a reply assert present-tense
  perception? Conservative: memory- or uncertainty-framed sentences are
  excluded, so false negatives are preferred over false positives.
- ``GroundingTracker`` — a session-scoped ring buffer of "did this turn touch
  the world?", feeding the consciousness profile's reality_testing dimension.
"""

from __future__ import annotations

import re
from collections import deque
from enum import Enum

__all__ = [
    "GroundingTracker",
    "Provenance",
    "looks_like_fresh_perception_claim",
    "provenance_of_coalition",
    "provenance_of_memory_kind",
]

# ReDoS discipline (mirrors mind/identity.py): bounded input, fixed patterns.
_MAX_INPUT_CHARS = 2000

_PERCEIVED_SOURCES = frozenset({"scene", "prediction", "exploration"})
_RECALLED_SOURCES = frozenset({"memory", "default_mode", "narrative"})

_PERCEIVED_KINDS = frozenset({"observation", "観察"})
_GENERATED_KINDS = frozenset({"dream", "curiosity", "好奇心"})


class Provenance(str, Enum):
    PERCEIVED = "perceived"
    RECALLED = "recalled"
    GENERATED = "generated"


def provenance_of_coalition(source: str) -> Provenance:
    """Epistemic origin of a workspace coalition, derived from its source tag."""
    if source in _PERCEIVED_SOURCES:
        return Provenance.PERCEIVED
    if source in _RECALLED_SOURCES:
        return Provenance.RECALLED
    return Provenance.GENERATED


def provenance_of_memory_kind(kind: str) -> Provenance:
    """Epistemic origin of a stored memory, derived from its kind tag."""
    if kind in _PERCEIVED_KINDS:
        return Provenance.PERCEIVED
    if kind in _GENERATED_KINDS:
        return Provenance.GENERATED
    return Provenance.RECALLED


# A claim needs BOTH a present-tense perception verb AND a spatial anchor.
# "I see" alone is mostly a discourse marker ("I see, that makes sense") and
# 見える alone is mostly metaphor (希望が見える); requiring a concrete
# perception-domain noun in the same reply kills those without a semantic
# model. Fixed and generic — persona content never lives here. The accepted
# cost is false negatives (e.g. anchor-less "目の前にトラックがあります"),
# which is the declared safe direction.
_VERB_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bI (?:can )?see\b", re.IGNORECASE),
    re.compile(r"\bI(?:'m| am) looking at\b", re.IGNORECASE),
    re.compile(r"見え(?:る|て(?:い?る|います)?|ます)"),
)

# Temporal deixis ("what I see RIGHT NOW is …") asserts live perception even
# without a spatial noun — self-sufficient claims.
_DEICTIC_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?:今|いま)[、 ]?見え"),
    re.compile(r"\bright now\b.{0,30}\bI (?:can )?see\b", re.IGNORECASE),
    re.compile(r"\bI (?:can )?see\b.{0,40}\bright now\b", re.IGNORECASE),
)

_ANCHOR_PATTERN: re.Pattern[str] = re.compile(
    r"window|outside|camera|street|\bsky\b|\broom\b|\bdoor\b|ceiling|balcony"
    r"|in front of me"
    r"|窓|カメラ|部屋|空|通り|玄関|天井|床|ベランダ|目の前|外",
    re.IGNORECASE,
)

# Memory framing, uncertainty hedges, negation, and cognitive objects exempt
# the reply — the safe failure direction is a missed claim, not a false
# re-ask on honest recall or figurative speech.
_EXCLUSION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(remember|remembered|recall|recalled|earlier|yesterday)\b", re.IGNORECASE),
    re.compile(r"\bsee (?:why|what|how|that|your)\b", re.IGNORECASE),
    re.compile(r"覚えて"),
    re.compile(r"思い出"),
    re.compile(r"昨日"),
    re.compile(r"さっき"),
    re.compile(r"この前"),
    re.compile(r"気がする"),
    re.compile(r"かも(?:しれ|ね|な|。|$)"),
    re.compile(r"見え(?:ない|ません|へん|なかった|た)"),
    re.compile(r"わけ(?:じゃ|では)ない"),
    # Cognitive/metaphor objects of 見える — never camera perception.
    re.compile(r"(?:理由|意味|答え|解決策|希望|未来|可能性|方向性|道筋)が?見え"),
)


def looks_like_fresh_perception_claim(text: str) -> bool:
    """True when the reply asserts present-tense, anchored perception.

    claim = (temporal deixis ∨ (perception verb ∧ spatial anchor))
            ∧ no memory/hedge/negation/metaphor framing.
    """
    if not text:
        return False
    capped = text[:_MAX_INPUT_CHARS]
    deictic = any(p.search(capped) for p in _DEICTIC_PATTERNS)
    anchored = any(p.search(capped) for p in _VERB_PATTERNS) and bool(
        _ANCHOR_PATTERN.search(capped)
    )
    if not (deictic or anchored):
        return False
    return not any(p.search(capped) for p in _EXCLUSION_PATTERNS)


class GroundingTracker:
    """Session-scoped record of how recently the agent touched the world.

    ``note_turn(grounded)`` per turn; ``ratio()`` over the recent window and
    ``turns_since_grounded()`` feed the consciousness profile's
    reality_testing dimension. In-memory only — grounding is a property of
    the running session, not of history.
    """

    def __init__(self, window: int = 20) -> None:
        self._turns: deque[bool] = deque(maxlen=window)
        self._since_grounded = 0

    def note_turn(self, grounded: bool) -> None:
        self._turns.append(bool(grounded))
        self._since_grounded = 0 if grounded else self._since_grounded + 1

    def ratio(self) -> float:
        """Grounded fraction of recent turns (1.0 before any turn — benefit of the doubt)."""
        if not self._turns:
            return 1.0
        return sum(self._turns) / len(self._turns)

    def turns_since_grounded(self) -> int:
        return self._since_grounded
