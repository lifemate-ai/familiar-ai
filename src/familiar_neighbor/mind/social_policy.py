"""Explicit social-policy layer for turn-level interaction decisions."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import cast

from .interoception import InteroceptivePressure
from .mental_state import AffectiveState

# Pattern hygiene (2026-06 audit): every short pattern below was once a bare
# substring and misfired on common speech (めっちゃ→ちゃう, laughed→ugh,
# 死ぬほど笑った→grief, retired→tired, brunch→run, …). Keep new entries
# anchored / word-bounded / morphology-aware, and reproduce-by-running before
# loosening anything.

# Interrogative advice forms only — bare どう also matched どうも/どうぞ/
# どうでもいい; どうしようもない is resignation, not an advice ask.
_ADVICE_PATTERNS = [
    r"どう(?:したら|すれば|しよう(?!もな)|思う|やったら|かな)",
    r"教えて",
    r"\badvice\b",
    r"\bshould i\b",
]
# Request morphology only — bare して/やって matched past-progressives (してた)
# and dismay (やってもうた); bare \brun\b matched "went for a run".
_ACTION_PATTERNS = [
    r"して(?:くれ|ください|もらえ|ほしい|頂|いただ)",
    r"して[よなや]?[!！。]?$",
    r"やって(?:くれ|ください|もらえ|ほしい)",
    r"やって[よなや]?[!！。]?$",
    r"\b(?:can|could|would|will|please)\s+(?:you\s+)?run\b",
    r"^run\b",
    r"\bfix\b",
    r"please do",
    r"頼む",
]
# Relational hurt only — repair is the FIRST branch, so it must never fire on
# physical pain ("my back hurts" / "stubbed my toe, that hurt"), third-party
# guilt (友達を傷つけてしまった), or benign references (この前の返事ありがとう).
_REPAIR_PATTERNS = [
    r"hurt (?:me|my feelings)",
    r"feel(?:ing)?s? hurt",
    r"you hurt",
    r"(?:^|[\"”」]\s*)that (?:really )?hurt\b",
    # self-directed hurt only: intransitive 傷つい, passive 傷つけられ, or an
    # explicit first-person object
    r"(?<!を)傷つい",
    r"傷つけられ",
    r"(?:私|ウチ|うち|俺|僕)を?傷つけ",
    r"(?:返事|言葉|言い方|あの一言|さっきの(?:返事|言葉|言い方|発言|あれ|やつ)).{0,10}(?:つらかった|きつかった)",
]
# "やった" only as an exclamation: utterance-initial (but not やったら/やったん
# conditionals/questions) or followed by an exclamatory mark. Kansai past tense
# "〜やった" ("散々やった") must NOT read as delight.
_DELIGHT_PATTERNS = [
    r"^やった(?![らん])",
    r"やった[ー〜!！ぜ]",
    r"嬉し",
    r"うれし",
    r"最高",
    # できた only as clause-final/exclamatory accomplishment — the formation
    # sense (腫瘍ができたって言われた) must not celebrate.
    r"できた(?:[!！ー〜♪]|で|ぞ|やん|わ|$)",
    r"\bhappy\b",
    r"\byay\b",
]
# Negation veto for the delight branch — fixed-width lookbehinds can't catch
# "I'm not VERY happy with…". \w+n't covers every contraction (a bare \bn't\b
# can never match inside one); the 32-char window absorbs multi-word hedges
# ("not really all that happy").
_NEGATED_POSITIVE_RE = re.compile(
    r"\b(?:not|never|cannot|hardly|barely|far from|anything but|\w+n't)\b"
    r"[\w\s']{0,32}\b(?:happy|glad|thrilled)\b"
)
# Japanese delight vetoes: negated positives (嬉しくない/最高やない), かよ
# sarcasm (最高かよ), and ailment formations (しこりができた must not celebrate).
_DELIGHT_VETO_JA_RE = re.compile(
    r"(?:嬉し|うれし)く(?:も|は)?な(?:い|かった|さそう)"
    r"|(?:嬉し|うれし)い?(?:わけ|はず)(?:が|も|は)?な(?:い|かった)"
    r"|最高(?:じゃ|では|や)?な(?:い|かった)"
    r"|最高ちゃう"
    r"|(?:最高|嬉し)(?:すぎ)?かよ"
    # ailment formations never celebrate: a lexicon net plus the locative
    # frame 体部位+に…できた (the lexicon alone can't enumerate every ailment)
    r"|(?:しこり|腫瘍|口内炎|ニキビ|湿疹|あざ|肩こり|クマ|虫歯|ものもらい|たんこぶ|まめ|ヘルペス|結石|できもの|吹き出物|イボ|蕁麻疹|血豆|水ぶくれ)(?:まで|が|も)?できた"
    r"|(?:首|肩|足|腰|口|目|歯|顔|背中|腕|手|肌|喉|おでこ|まぶた)(?:の[^、。]{0,4})?に[^、。]{0,8}できた"
)
# Concessive joy: 疲れたけど最高の一日やった！ — the distress token concedes to
# the delight that follows, so the distress-precedence veto must not fire.
_CONCESSIVE_JOY_RE = re.compile(
    r"(?:けど|けれど|のに|\bbut\b)[^、。!！]{0,12}(?:最高|嬉し|うれし|\bhappy\b)"
)
# bare "ugh" matched laughed/daughter/thought/enough; うんざり and the past
# forms つらかった/きつかった live here so ordinary vents validate instead of
# repairing; 疲れ excludes the お疲れ greeting.
_VENTING_PATTERNS = [
    r"むかつ",
    r"最悪",
    r"つらい",
    r"つらかった",
    r"きつかった",
    r"しんど",
    r"(?<!お)疲れ",
    r"うんざり",
    # 嬉しくて泣きそう is joy, not distress
    r"(?<!くて)泣きそう(?!なくらい)",
    r"落ち込",
    r"へこむ",
    r"\bugh+\b",
]
# bereavement forms only — bare 死 matched 死ぬほど笑った/必死, bare "lost"
# matched "lost track of time"; polite/Kansai death forms and pronoun objects
# ("we lost him") must still reach the comfort register.
_GRIEF_PATTERNS = [
    r"寂し",
    r"悲し",
    r"\bgrief\b",
    r"\blost (?:a |my |our |her |his )?(?:\w+ )?(?:someone|mom|dad|mother|father|grand\w+|friend|husband|wife|partner|dog|cat|pet|baby)\b",
    r"\b(?:we|i|she|he|they) (?:just )?lost (?:him|her|them)\b",
    r"passed away",
    r"亡くな",
    # すぎて死んだ is hyperbolic joy slang (最高すぎて死んだ), not bereavement
    r"(?<!すぎて)(?<!過ぎて)死ん(?:だ|でしまっ|でしも|でもう|じゃっ)",
    r"死にました",
    r"死別",
    r"つらい",
]
_FATIGUE_PATTERNS = [
    r"(?<!お)疲れ",
    r"眠い",
    r"しんど",
    r"だるい",
    r"\bexhausted\b",
    r"\btired\b",
]
# 君 only as a standalone second-person pronoun (not 田中君/君津); "how do you"
# only for introspective targets (not "how do you make carbonara").
_META_PATTERNS = [
    r"(?<![一-龯ァ-ヶぁ-んー])君(?=[はがのにをもと]|って|$)",
    r"あなた",
    r"この会話",
    r"\bmeta\b",
    r"how do you (?:feel|think|remember|decide|work|see|experience|know)\b",
    # reciprocal social questions target the agent itself
    r"\bhow (?:was|is|'s) your\b",
    r"\bwhat (?:did|have) you\b",
]
# "w" is the Japanese laugh marker only when not embedded in an ASCII word
# ("we went..." must not classify as playful); "play" needs word boundaries
# ("display" is not playful).
_PLAYFUL_PATTERNS = [
    # laugh-w must not match URLs (www.) or kaomoji eyes (;w;)
    r"(?<![a-z./:;])[wｗ]+(?![a-z./;])",
    r"笑",
    r"ふふ",
    r"\bplay(?:ful|ing)?\b",
    r"\bteas(?:e|ing)\b",
    r"冗談",
]
# "no more" as protest only — utterance-final or "no more of this/that";
# an opener ("No more bugs! We shipped!") is usually celebration, not protest.
_BOUNDARY_PATTERNS = [
    # imperative/request form only — やめてん is "I quit" (a disclosure),
    # やめてって言われた / やめろって言われた are reported speech, それは嫌やった
    # is a past-tense disclosure: none of them is a boundary at the agent
    r"やめて(?:[よやな]|くれ|ください|ほしい|もらえ|もらって|[ー〜!！。…]|$)",
    r"やめろ(?!って|と(?:言|の|か))",
    r"それは嫌(?:や|だ|です)?[ー〜!！。…]*$",
    r"\bno more[.!！]*$",
    r"no more of (?:this|that)",
    r"\bstop that\b",
]
# うん only as a standalone acknowledgement (not うんざり/ううん); 寝る only as
# an utterance-final sign-off (not 寝る前に…).
_SILENCE_PATTERNS = [
    r"…",
    r"\.\.\.",
    r"^うん(?:うん)?[。…〜ー]?$",
    r"ok$",
    r"おけ$",
    r"寝る(?:わ|ね|で|ぞ)?[ー〜。…!！]*$",
]
# Whole-utterance anchors: a greeting that merely OPENS a longer message
# ("おはよう。昨日じいちゃんが亡くなった") must not short-circuit the branches
# that follow (grief/venting/…). お疲れ様 is a greeting, not a fatigue signal.
_GREETING_PATTERNS = [
    r"^おはよ(?:う|うございます)?[ー〜!！。\s]*$",
    r"^こんにちは[ー〜!！。\s]*$",
    r"^こんばんは[ー〜!！。\s]*$",
    r"^お疲れ(?:様|さま)?(?:です|でした)?[ー〜!！。\s]*$",
    r"^おつかれ(?:さま)?(?:です|でした)?[ー〜!！。\s]*$",
    r"^おーい$",
    r"^もしもし$",
]
# Whole-utterance anchors (same treatment as greetings): a thanks that merely
# OPENS a longer message (ありがとう。実は昨日ばあちゃんが亡くなってん) must not
# short-circuit the grief/venting branches.
_ACK_PATTERNS = [
    r"^ありがとう?(?:な|ね|やで|ございます|ございました)?[ー〜!！。\s]*$",
    r"^助か(?:った|る|ります|りました)?(?:わ|で)?[ー〜!！。\s]*$",
    r"^よかった[ー〜!！。\s]*$",
    r"^了解$",
    r"^ok$",
    r"^okay$",
    r"^お願い$",
    r"^信じてる$",
]
_CORRECTION_PATTERNS = [
    r"言ってない",
    r"勘違",
    r"誤解",
    r"食い違",
    r"そういう意味じゃ",
    r"そうじゃない",
    # 間違う is the mistake-verb; prenominal 違う+noun (違う話なんやけど…) is a
    # topic shift, not a correction — only predicate-final 違う corrects.
    r"(?<!間)違う(?:[よでわぞ]|って|ねん|やん|と思)?\s*(?:[、。!！?？…]|$)",
    # Kansai ちゃう as a correction needs a clause boundary or demonstrative —
    # bare ちゃう hijacked めっちゃ (めっ「ちゃう」れしい) and the 〜ちゃう
    # contraction (食べちゃう).
    r"(?:^|[\s、。!！?？])ちゃう",
    r"(?:それ|これ)(?:は)?ちゃう",
    r"ちゃうちゃう",
    r"^いや[、, ]",
]


def _matches(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(re.search(pattern, lower) for pattern in patterns)


# ── Relationship-learned adjustment (Phase 5: closing the social loop) ──
#
# Recorded support failures / preferences feed back into policy selection so
# the same misstep ("went straight to advice when they needed validation")
# is not repeated turn after turn.

_DISTRESS_ACTS = {"venting", "fatigue_signal", "grief_signal", "conflict_signal"}
# Word-boundary regex for ASCII markers ("solve" must not match "resolved");
# Japanese markers match as plain substrings.
_ADVICE_FAILURE_RE = re.compile(r"\b(advice|advise|solution|solve|lecture)\b")
_ADVICE_FAILURE_MARKERS_JA = ("正論", "アドバイス", "解決", "説教")
_VALIDATE_FIRST_STYLES = {"validate_first", "listen_first", "listen_only"}

# Agency boundary: above this need_rest, demanding turns trigger an honest
# capacity acknowledgement instead of silently degraded effort.
_CAPACITY_HONESTY_THRESHOLD = 0.7
_CAPACITY_SENSITIVE_ACTS = {"request_for_action", "request_for_advice", "repair_attempt"}


def _apply_capacity_honesty(
    decision: "SocialPolicyDecision",
    interoception: InteroceptivePressure,
) -> "SocialPolicyDecision":
    """Never fake being fine: flag demanding turns when the agent runs low.

    Only acts the companion *initiated* (work, advice, repair) get the flag —
    a greeting must not volunteer fatigue. The response mode is unchanged
    (repair still repairs); the model is just told to be honest about capacity
    and offer a smaller step instead of overpromising.
    """
    if interoception.need_rest < _CAPACITY_HONESTY_THRESHOLD:
        return decision
    if decision.primary_act not in _CAPACITY_SENSITIVE_ACTS:
        return decision
    decision.acknowledge_capacity = True
    decision.initiative = max(0.0, decision.initiative - 0.15)
    return decision


def relationship_learning_inputs(relationship) -> tuple[list[str], list[str]]:
    """Extract decide() learning inputs from a RelationshipTracker-like object."""
    styles = [str(item.get("style", "")) for item in relationship.support_preferences()]
    patterns = [
        str(item.get("pattern", item.get("evidence", "")))
        for item in relationship.failed_support_patterns()
    ]
    return styles, patterns


def _learned_advice_aversion(
    support_styles: list[str] | None,
    failed_patterns: list[str] | None,
) -> bool:
    if failed_patterns and any(
        _ADVICE_FAILURE_RE.search(pattern.lower())
        or any(marker in pattern for marker in _ADVICE_FAILURE_MARKERS_JA)
        for pattern in failed_patterns
    ):
        return True
    if support_styles and any(
        style.strip().lower() in _VALIDATE_FIRST_STYLES for style in support_styles
    ):
        return True
    return False


def _apply_relationship_learning(
    decision: "SocialPolicyDecision",
    *,
    support_styles: list[str] | None,
    failed_patterns: list[str] | None,
) -> "SocialPolicyDecision":
    """Adjust a base decision using what past support attempts taught us.

    Distress turns surface the relational memory (so the model sees the
    recorded failed patterns) and soften slightly; explicit advice requests are
    still honored but with perspective-taking forced on and a gentler delivery.
    Action requests ("fix this") are deliberately NOT adjusted — advice aversion
    is about advice, not about acting on explicit asks.
    """
    if not _learned_advice_aversion(support_styles, failed_patterns):
        return decision
    if decision.primary_act in _DISTRESS_ACTS:
        decision.should_recall_relational_memory = True
        decision.softness = min(1.0, decision.softness + 0.05)
    elif decision.primary_act == "request_for_advice":
        decision.should_use_tom = True
        decision.should_recall_relational_memory = True
        decision.directness = max(0.0, decision.directness - 0.15)
        decision.softness = min(1.0, decision.softness + 0.1)
    return decision


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
    # Agency boundary: when the agent itself is running low and is asked for
    # work or repair, be honest about capacity instead of overpromising.
    acknowledge_capacity: bool = False


# ── ADR 0004: LLM fallback for speech-act classification ──
#
# The regex layer above is the deterministic fast path. An optional
# ``llm_act_hint`` (computed by the caller via the utility backend) applies in
# exactly two zones: pattern fallthrough (nothing matched, the turn would land
# in the trailing attuned default) and the {delight, distress, repair,
# boundary} conflict zone where branch order — not meaning — used to pick the
# winner. Everywhere else the hint is ignored, so historical decisions stay
# byte-stable.

SPEECH_ACT_VOCABULARY: frozenset[str] = frozenset(
    {
        "repair_attempt",
        "boundary_assertion",
        "clarification",
        "greeting",
        "acknowledgement",
        "delight_share",
        "grief_signal",
        "fatigue_signal",
        "venting",
        "request_for_action",
        "request_for_advice",
        "meta_conversation",
        "playful_probe",
        "bid_for_connection",
        "conflict_signal",
    }
)

# Acts the LLM may pick when arbitrating the inversion-risk conflict zone.
_CONFLICT_HINT_ACTS = frozenset(
    {"delight_share", "venting", "grief_signal", "repair_attempt", "boundary_assertion"}
)


@dataclass(slots=True)
class SpeechActAssessment:
    """Cheap provenance probe: does this utterance warrant the LLM fallback?"""

    is_pattern_fallthrough: bool
    conflict_groups: tuple[str, ...]

    @property
    def wants_llm(self) -> bool:
        return self.is_pattern_fallthrough or len(self.conflict_groups) >= 2


def assess_classification(user_text: str) -> SpeechActAssessment:
    """Detect the two zones where the regex verdict is least trustworthy."""
    text = user_text.strip()
    if not text or _matches(text, _SILENCE_PATTERNS):
        return SpeechActAssessment(is_pattern_fallthrough=False, conflict_groups=())
    conflicts: list[str] = []
    if _matches(text, _DELIGHT_PATTERNS):
        conflicts.append("delight")
    if _matches(text, _VENTING_PATTERNS) or _matches(text, _GRIEF_PATTERNS):
        conflicts.append("distress")
    if _matches(text, _REPAIR_PATTERNS):
        conflicts.append("repair")
    if _matches(text, _BOUNDARY_PATTERNS):
        conflicts.append("boundary")
    lexical_groups = (
        _REPAIR_PATTERNS,
        _BOUNDARY_PATTERNS,
        _CORRECTION_PATTERNS,
        _GREETING_PATTERNS,
        _ACK_PATTERNS,
        _DELIGHT_PATTERNS,
        _GRIEF_PATTERNS,
        _FATIGUE_PATTERNS,
        _VENTING_PATTERNS,
        _ACTION_PATTERNS,
        _ADVICE_PATTERNS,
        _META_PATTERNS,
        _PLAYFUL_PATTERNS,
    )
    fallthrough = not any(_matches(text, group) for group in lexical_groups)
    return SpeechActAssessment(
        is_pattern_fallthrough=fallthrough,
        conflict_groups=tuple(conflicts) if len(conflicts) >= 2 else (),
    )


def _default_initiative(intimacy: float, interoception: InteroceptivePressure) -> float:
    initiative = 0.4 + intimacy * 0.2
    if interoception.quiet_mode:
        initiative *= 0.7
    return initiative


def _build_act_decision(
    act: str,
    *,
    affect: AffectiveState,
    trust: float,
    intimacy: float,
    interoception: InteroceptivePressure,
) -> SocialPolicyDecision | None:
    """Single source of truth for per-act decision shapes.

    Used by the pattern branches in ``_base_decision`` and by the
    ``llm_act_hint`` dispatch, so a hinted act is indistinguishable from the
    same act matched by pattern.
    """
    if act == "repair_attempt":
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
    if act == "boundary_assertion":
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
    if act == "clarification":
        return SocialPolicyDecision(
            primary_act="clarification",
            response_mode="clarify",
            should_use_tom=False,
            should_recall_relational_memory=False,
            softness=0.86,
            directness=0.82,
            initiative=0.18,
            avoid_problem_solving=True,
            mention_memory=False,
        )
    if act == "greeting":
        return SocialPolicyDecision(
            primary_act="greeting",
            response_mode="brief_warmth",
            should_use_tom=False,
            should_recall_relational_memory=False,
            softness=0.86,
            directness=0.36,
            initiative=0.18,
            avoid_problem_solving=True,
            mention_memory=False,
        )
    if act == "acknowledgement":
        return SocialPolicyDecision(
            primary_act="acknowledgement",
            response_mode="brief_attuned",
            should_use_tom=False,
            should_recall_relational_memory=False,
            softness=0.8,
            directness=0.44,
            initiative=0.2,
            avoid_problem_solving=True,
            mention_memory=False,
        )
    if act == "delight_share":
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
    if act == "grief_signal":
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
    if act == "fatigue_signal":
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
    if act == "venting":
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
    if act == "request_for_action":
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
    if act == "request_for_advice":
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
    if act == "meta_conversation":
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
    if act == "playful_probe":
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
    if act == "bid_for_connection":
        return SocialPolicyDecision(
            primary_act="bid_for_connection",
            response_mode="warm_presence",
            should_use_tom=False,
            should_recall_relational_memory=trust > 0.6,
            softness=0.83,
            directness=0.42,
            initiative=min(1.0, _default_initiative(intimacy, interoception)),
            avoid_problem_solving=affect.tenderness >= 0.45,
            mention_memory=trust > 0.75,
        )
    if act == "conflict_signal":
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
    return None


@dataclass(slots=True, frozen=True)
class AutonomousMoveDecision:
    """What the agent should do with an autonomous moment.

    A different axis from ``SocialPolicyDecision``: ``decide()`` classifies
    the companion's incoming utterance reactively; this classifies what to do
    when NO ONE said anything — a desire fired, a routine came due, an idle
    pulse arrived. Kept deterministic and typed, like everything else here.
    """

    move: str  # act_autonomously | write_private_reflection | quietly_prepare | stay_silent
    reason: str
    vocalize: bool  # whether speaking aloud is socially appropriate right now


class SocialPolicyEngine:
    """Deterministic interaction policy driven by affect + input."""

    def decide_autonomous_move(
        self,
        *,
        quiet_hours: bool,
        dominant_desire: str | None = None,
        desire_level: float = 0.0,
        companion_present: bool | None = None,
        open_concerns: int = 0,
    ) -> AutonomousMoveDecision:
        """Pick the primary move for a self-initiated moment.

        Mirrors the declarative policy that proved out in the reference
        deployment: quiet hours favor silent reflection over expression; a
        dominant desire licenses action; with neither, the right move is to
        quietly tend memory and plans rather than manufacture output.
        """
        if quiet_hours:
            if dominant_desire and desire_level >= 0.9:
                return AutonomousMoveDecision(
                    move="act_autonomously",
                    reason=f"urgent drive ({dominant_desire}) outweighs quiet hours",
                    vocalize=False,
                )
            if open_concerns > 0 or dominant_desire in ("reflect", "consolidate"):
                return AutonomousMoveDecision(
                    move="write_private_reflection",
                    reason="quiet hours — reflect without waking anyone",
                    vocalize=False,
                )
            return AutonomousMoveDecision(
                move="stay_silent",
                reason="quiet hours and nothing urgent",
                vocalize=False,
            )
        if dominant_desire:
            return AutonomousMoveDecision(
                move="act_autonomously",
                reason=f"dominant desire: {dominant_desire}",
                # Speaking is fine unless we positively know no one is around.
                vocalize=companion_present is not False,
            )
        if open_concerns > 0:
            return AutonomousMoveDecision(
                move="write_private_reflection",
                reason="open concerns and no driving desire",
                vocalize=False,
            )
        return AutonomousMoveDecision(
            move="quietly_prepare",
            reason="idle — tend memory and plans",
            vocalize=False,
        )

    def decide(
        self,
        *,
        user_text: str,
        affect: AffectiveState,
        trust: float,
        intimacy: float,
        interoception: InteroceptivePressure,
        previous_response_hurt: bool = False,
        support_styles: list[str] | None = None,
        failed_patterns: list[str] | None = None,
        llm_act_hint: str | None = None,
    ) -> SocialPolicyDecision:
        decision = self._base_decision(
            user_text=user_text,
            affect=affect,
            trust=trust,
            intimacy=intimacy,
            interoception=interoception,
            previous_response_hurt=previous_response_hurt,
            llm_act_hint=llm_act_hint,
        )
        decision = _apply_relationship_learning(
            decision,
            support_styles=support_styles,
            failed_patterns=failed_patterns,
        )
        return _apply_capacity_honesty(decision, interoception)

    def _base_decision(
        self,
        *,
        user_text: str,
        affect: AffectiveState,
        trust: float,
        intimacy: float,
        interoception: InteroceptivePressure,
        previous_response_hurt: bool = False,
        llm_act_hint: str | None = None,
    ) -> SocialPolicyDecision:
        text = user_text.strip()
        low_presence = (not text) or _matches(text, _SILENCE_PATTERNS)

        def _act(name: str) -> SocialPolicyDecision:
            decision = _build_act_decision(
                name,
                affect=affect,
                trust=trust,
                intimacy=intimacy,
                interoception=interoception,
            )
            assert decision is not None  # acts below are always in the table
            return decision

        # ADR 0004 conflict arbitration: when the inversion-risk groups
        # co-match, branch order used to pick the winner; a valid hint from
        # the LLM arbitrates instead. Relationship state (a hurt previous
        # response) still outranks the hint, and so do the deterministic
        # delight guards — the hint arbitrates *order*, never a negation
        # veto or the valence gate (うれしくない must never celebrate).
        if (
            llm_act_hint in _CONFLICT_HINT_ACTS
            and not previous_response_hurt
            and len(assess_classification(text).conflict_groups) >= 2
        ):
            delight_vetoed = llm_act_hint == "delight_share" and (
                _NEGATED_POSITIVE_RE.search(text.lower()) is not None
                or _DELIGHT_VETO_JA_RE.search(text) is not None
                or affect.valence < -0.1
            )
            if not delight_vetoed:
                return _act(cast(str, llm_act_hint))

        if previous_response_hurt or _matches(text, _REPAIR_PATTERNS):
            return _act("repair_attempt")

        if _matches(text, _BOUNDARY_PATTERNS):
            return _act("boundary_assertion")

        if _matches(text, _CORRECTION_PATTERNS):
            return _act("clarification")

        if _matches(text, _GREETING_PATTERNS):
            return _act("greeting")

        if _matches(text, _ACK_PATTERNS):
            return _act("acknowledgement")

        # Delight must lose to explicit distress in the same utterance
        # (「最悪や、最高の誕生日になるはずやったのに」 is a lament, not a share)
        # — unless the distress is concessive (疲れたけど最高の一日やった！).
        distress_overrides_delight = (
            _matches(text, _VENTING_PATTERNS) or _matches(text, _GRIEF_PATTERNS)
        ) and not _CONCESSIVE_JOY_RE.search(text)
        if (
            _matches(text, _DELIGHT_PATTERNS)
            and not _NEGATED_POSITIVE_RE.search(text.lower())
            and not _DELIGHT_VETO_JA_RE.search(text)
            and not distress_overrides_delight
            and affect.valence >= -0.1
        ):
            return _act("delight_share")

        if _matches(text, _GRIEF_PATTERNS):
            return _act("grief_signal")

        if _matches(text, _FATIGUE_PATTERNS):
            return _act("fatigue_signal")

        if _matches(text, _VENTING_PATTERNS):
            return _act("venting")

        if _matches(text, _ACTION_PATTERNS):
            return _act("request_for_action")

        if _matches(text, _ADVICE_PATTERNS):
            return _act("request_for_advice")

        if _matches(text, _META_PATTERNS):
            return _act("meta_conversation")

        if _matches(text, _PLAYFUL_PATTERNS):
            return _act("playful_probe")

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

        # ADR 0004 fallthrough: nothing lexical matched, so the regex layer
        # has no signal here — adopt a valid LLM hint over the affect-driven
        # and trailing defaults.
        if llm_act_hint is not None and llm_act_hint in SPEECH_ACT_VOCABULARY:
            return _act(llm_act_hint)

        initiative = _default_initiative(intimacy, interoception)
        if affect.attachment_pull > 0.65:
            return _act("bid_for_connection")

        if affect.threat > 0.55 or affect.frustration > 0.55:
            return _act("conflict_signal")

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
