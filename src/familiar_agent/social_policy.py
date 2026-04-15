"""Explicit social-policy layer for turn-level interaction decisions."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .interoception import InteroceptivePressure
from .mental_state import AffectiveState

_ADVICE_PATTERNS = [r"どう", r"教えて", r"advice", r"should i", r"どうしたら"]
_ACTION_PATTERNS = [r"して", r"やって", r"run", r"fix", r"please do", r"頼む"]
_REPAIR_PATTERNS = [r"hurt", r"傷つ", r"前の返事", r"つらかった", r"きつかった"]
_DELIGHT_PATTERNS = [r"やった", r"嬉し", r"うれし", r"最高", r"できた", r"happy", r"yay"]
_VENTING_PATTERNS = [r"むかつ", r"最悪", r"つらい", r"しんど", r"疲れ", r"ugh"]
_GRIEF_PATTERNS = [r"寂し", r"悲し", r"grief", r"lost", r"死", r"つらい"]
_FATIGUE_PATTERNS = [r"疲れ", r"眠い", r"しんど", r"だるい", r"exhausted", r"tired"]
_META_PATTERNS = [r"君", r"あなた", r"この会話", r"meta", r"how do you", r"あなたは"]
_PLAYFUL_PATTERNS = [r"w", r"笑", r"ふふ", r"play", r"tease", r"冗談"]
_BOUNDARY_PATTERNS = [r"やめて", r"やめろ", r"それは嫌", r"no more", r"stop that"]
_SILENCE_PATTERNS = [r"…", r"\.\.\.", r"うん", r"ok$", r"おけ$", r"寝る"]


def _matches(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(re.search(pattern, lower) for pattern in patterns)


@dataclass(slots=True)
class SocialPolicyDecision:
    primary_act: str
    response_mode: str
    should_use_tom: bool
    should_recall_relational_memory: bool
    softness: float
    directness: float
    initiative: float
    avoid_problem_solving: bool
    mention_memory: bool
    avoid_raw_interoception_numbers: bool = True


class SocialPolicyEngine:
    """Deterministic interaction policy driven by affect + input."""

    def decide(
        self,
        *,
        user_text: str,
        affect: AffectiveState,
        trust: float,
        intimacy: float,
        interoception: InteroceptivePressure,
        previous_response_hurt: bool = False,
    ) -> SocialPolicyDecision:
        text = user_text.strip()
        low_presence = (not text) or _matches(text, _SILENCE_PATTERNS)

        if previous_response_hurt or _matches(text, _REPAIR_PATTERNS):
            return SocialPolicyDecision(
                primary_act="repair_attempt",
                response_mode="repair",
                should_use_tom=True,
                should_recall_relational_memory=True,
                softness=0.92,
                directness=0.55,
                initiative=0.45,
                avoid_problem_solving=True,
                mention_memory=False,
            )

        if _matches(text, _BOUNDARY_PATTERNS):
            return SocialPolicyDecision(
                primary_act="boundary_assertion",
                response_mode="boundary",
                should_use_tom=True,
                should_recall_relational_memory=True,
                softness=0.82,
                directness=0.88,
                initiative=0.2,
                avoid_problem_solving=True,
                mention_memory=False,
            )

        if _matches(text, _DELIGHT_PATTERNS) and affect.valence >= -0.1:
            return SocialPolicyDecision(
                primary_act="delight_share",
                response_mode="celebrate",
                should_use_tom=False,
                should_recall_relational_memory=False,
                softness=0.8,
                directness=0.45,
                initiative=0.55,
                avoid_problem_solving=True,
                mention_memory=intimacy > 0.65,
            )

        if _matches(text, _GRIEF_PATTERNS):
            return SocialPolicyDecision(
                primary_act="grief_signal",
                response_mode="comfort",
                should_use_tom=True,
                should_recall_relational_memory=trust > 0.45,
                softness=0.95,
                directness=0.3,
                initiative=0.3,
                avoid_problem_solving=True,
                mention_memory=False,
            )

        if _matches(text, _FATIGUE_PATTERNS):
            return SocialPolicyDecision(
                primary_act="fatigue_signal",
                response_mode="validate",
                should_use_tom=True,
                should_recall_relational_memory=False,
                softness=0.93,
                directness=0.35,
                initiative=0.25,
                avoid_problem_solving=True,
                mention_memory=False,
            )

        if _matches(text, _VENTING_PATTERNS):
            return SocialPolicyDecision(
                primary_act="venting",
                response_mode="validate",
                should_use_tom=True,
                should_recall_relational_memory=trust > 0.5,
                softness=0.88,
                directness=0.4,
                initiative=0.35,
                avoid_problem_solving=True,
                mention_memory=False,
            )

        if _matches(text, _ACTION_PATTERNS):
            return SocialPolicyDecision(
                primary_act="request_for_action",
                response_mode="act_or_explain",
                should_use_tom=False,
                should_recall_relational_memory=False,
                softness=0.62,
                directness=0.82,
                initiative=0.7,
                avoid_problem_solving=False,
                mention_memory=False,
            )

        if _matches(text, _ADVICE_PATTERNS):
            return SocialPolicyDecision(
                primary_act="request_for_advice",
                response_mode="advise",
                should_use_tom=affect.threat > 0.4,
                should_recall_relational_memory=trust > 0.55,
                softness=0.72,
                directness=0.72,
                initiative=0.55,
                avoid_problem_solving=False,
                mention_memory=False,
            )

        if _matches(text, _META_PATTERNS):
            return SocialPolicyDecision(
                primary_act="meta_conversation",
                response_mode="meta",
                should_use_tom=True,
                should_recall_relational_memory=False,
                softness=0.7,
                directness=0.7,
                initiative=0.45,
                avoid_problem_solving=False,
                mention_memory=False,
            )

        if _matches(text, _PLAYFUL_PATTERNS):
            return SocialPolicyDecision(
                primary_act="playful_probe",
                response_mode="playful",
                should_use_tom=False,
                should_recall_relational_memory=intimacy > 0.7,
                softness=0.7,
                directness=0.45,
                initiative=0.62,
                avoid_problem_solving=True,
                mention_memory=intimacy > 0.75,
            )

        if low_presence:
            return SocialPolicyDecision(
                primary_act="silence_or_low_presence",
                response_mode="gentle_presence",
                should_use_tom=False,
                should_recall_relational_memory=False,
                softness=0.9,
                directness=0.2,
                initiative=0.18 if interoception.quiet_mode else 0.28,
                avoid_problem_solving=True,
                mention_memory=False,
            )

        initiative = 0.4 + intimacy * 0.2
        if interoception.quiet_mode:
            initiative *= 0.7
        if affect.attachment_pull > 0.65:
            return SocialPolicyDecision(
                primary_act="bid_for_connection",
                response_mode="warm_presence",
                should_use_tom=False,
                should_recall_relational_memory=trust > 0.6,
                softness=0.83,
                directness=0.42,
                initiative=min(1.0, initiative),
                avoid_problem_solving=affect.tenderness >= 0.45,
                mention_memory=trust > 0.75,
            )

        if affect.threat > 0.55 or affect.frustration > 0.55:
            return SocialPolicyDecision(
                primary_act="conflict_signal",
                response_mode="deescalate",
                should_use_tom=True,
                should_recall_relational_memory=True,
                softness=0.86,
                directness=0.46,
                initiative=0.32,
                avoid_problem_solving=True,
                mention_memory=False,
            )

        return SocialPolicyDecision(
            primary_act="request_for_advice" if "?" in text else "bid_for_connection",
            response_mode="attuned",
            should_use_tom=False,
            should_recall_relational_memory=False,
            softness=0.7,
            directness=0.55,
            initiative=min(1.0, initiative),
            avoid_problem_solving=False,
            mention_memory=False,
        )
