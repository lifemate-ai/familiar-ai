"""Deterministic appraisal engine for low-dimensional affect updates."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from .interoception import InteroceptivePressure
from .mental_state import AffectiveState
from .prediction import PredictionSignal

_DISTRESS_PATTERNS = [
    r"hurt",
    r"つらい",
    r"しんど",
    r"悲し",
    r"苦し",
    r"疲れ",
    r"眠い",
    r"つかれ",
]
_JOY_PATTERNS = [
    r"やった",
    r"嬉し",
    r"うれし",
    r"最高",
    r"楽しい",
    r"love",
    r"happy",
    r"excited",
]
_REPAIR_PATTERNS = [r"hurt me", r"hurt", r"傷つ", r"前の返事", r"嫌だった", r"きつかった"]
_REQUEST_PATTERNS = [r"どう", r"help", r"教えて", r"して", r"お願い", r"\?"]


def _count_patterns(text: str, patterns: Iterable[str]) -> float:
    pattern_list = list(patterns)
    lower = text.lower()
    count = 0
    for pattern in pattern_list:
        if re.search(pattern, lower):
            count += 1
    return min(1.0, count / max(1, len(pattern_list)))


@dataclass(slots=True)
class AppraisalContext:
    user_text: str
    companion_mood: str = "engaged"
    relationship_trust: float = 0.5
    relationship_intimacy: float = 0.4
    recalled_memory_summaries: tuple[str, ...] = ()
    prediction_signal: PredictionSignal | None = None
    interoception: InteroceptivePressure | None = None
    blocked_drives: tuple[str, ...] = ()
    unfinished_business_count: int = 0


class AppraisalEngine:
    """Low-dimensional affect from closed-loop state inputs."""

    def appraise(self, ctx: AppraisalContext) -> AffectiveState:
        distress = _count_patterns(ctx.user_text, _DISTRESS_PATTERNS)
        joy = _count_patterns(ctx.user_text, _JOY_PATTERNS)
        repair = _count_patterns(ctx.user_text, _REPAIR_PATTERNS)
        asks = _count_patterns(ctx.user_text, _REQUEST_PATTERNS)

        intero = ctx.interoception
        pressure_rest = intero.need_rest if intero is not None else 0.0
        caution = intero.caution if intero is not None else 0.0
        frustration_bias = intero.frustration_bias if intero is not None else 0.0
        receptivity = intero.social_receptivity if intero is not None else 0.5

        prediction = ctx.prediction_signal
        agency_error = prediction.agency_error if prediction is not None else 0.0
        external_surprise = prediction.external_surprise if prediction is not None else 0.0

        blocked_bonus = min(1.0, len(ctx.blocked_drives) * 0.2)
        unfinished = min(1.0, ctx.unfinished_business_count * 0.15)
        relational_pull = min(1.0, ctx.relationship_intimacy * 0.6 + ctx.relationship_trust * 0.4)
        memory_pull = 0.2 if ctx.recalled_memory_summaries else 0.0

        valence = max(-1.0, min(1.0, joy * 0.9 - distress * 0.95 - repair * 0.35))
        arousal = min(1.0, joy * 0.55 + distress * 0.6 + external_surprise * 0.5 + caution * 0.25)
        dominance = max(-1.0, min(1.0, joy * 0.35 - distress * 0.45 - agency_error * 0.5))
        uncertainty = min(1.0, caution * 0.5 + external_surprise * 0.4 + asks * 0.2)
        attachment_pull = min(1.0, relational_pull * 0.55 + memory_pull + receptivity * 0.2)
        threat = min(1.0, distress * 0.65 + repair * 0.55 + caution * 0.4)
        tenderness = min(1.0, joy * 0.35 + relational_pull * 0.3 + receptivity * 0.3)
        frustration = min(
            1.0,
            frustration_bias * 0.35 + agency_error * 0.55 + blocked_bonus * 0.35 + repair * 0.15,
        )
        loneliness = min(1.0, unfinished * 0.35 + max(0.0, 0.55 - receptivity) * 0.5)

        if ctx.companion_mood == "tired":
            tenderness = min(1.0, tenderness + 0.2)
            attachment_pull = min(1.0, attachment_pull + 0.1)
            dominance = max(-1.0, dominance - 0.1)
        elif ctx.companion_mood == "frustrated":
            threat = min(1.0, threat + 0.1)
            frustration = min(1.0, frustration + 0.15)
            tenderness = min(1.0, tenderness + 0.1)
        elif ctx.companion_mood == "happy":
            valence = min(1.0, valence + 0.2)
            tenderness = min(1.0, tenderness + 0.1)

        if pressure_rest > 0.7:
            arousal = min(arousal, 0.55)
            dominance = max(-1.0, dominance - 0.15)

        summary_parts: list[str] = []
        if repair > 0.0:
            summary_parts.append("repair-sensitive")
        elif joy > distress and joy > 0.0:
            summary_parts.append("warmly-up")
        elif distress > 0.0:
            summary_parts.append("concerned")
        if frustration > 0.55:
            summary_parts.append("frustrated")
        if loneliness > 0.55:
            summary_parts.append("lonely")
        summary = ", ".join(summary_parts) if summary_parts else "steady"

        return AffectiveState(
            valence=valence,
            arousal=arousal,
            dominance=dominance,
            uncertainty=uncertainty,
            attachment_pull=attachment_pull,
            threat=threat,
            tenderness=tenderness,
            frustration=frustration,
            loneliness=loneliness,
            summary=summary,
        ).sanitized()
