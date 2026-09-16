"""Social reflex — deterministic guards that keep a small model socially sane.

Prompts alone do not stop a 9B model from pointing the camera at someone's
feelings or from writing silent text instead of speaking.  These helpers act in
code, around the model:

- :func:`classify_turn`   — cheap lexical classification of the user's utterance
- :func:`allowed_tools`   — restrict the tool set offered on social turns
- :func:`strip_hallucinated_tool_text` — drop `<tool_code>`/`<tool_call>` junk
- :func:`count_sentences` / :func:`count_questions` — used by the eval harness
  and by the one-shot "too long" nudge
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from familiar_runtime.runtime import RetryDecision, RuntimeHookBase

if TYPE_CHECKING:
    from familiar_runtime.models.base import ModelTurnResult, ToolCall
    from familiar_runtime.runtime import TurnContext
    from familiar_runtime.tools.base import ToolExecutionResult

logger = logging.getLogger(__name__)

# Tools that move or use the body's senses.  Withheld on social turns.
PERCEPTION_TOOLS = frozenset({"see", "look", "walk"})
# After this many see() calls in one turn a small model must speak before looking again.
MAX_SEE_BEFORE_SAY = 2

_SAY_JUNK_RE = re.compile(r"(\\n|[{}\]\[`]|</?[a-z_]+>)+\s*$")


def clean_say_text(text: str) -> str:
    """Strip tool-syntax residue that small models leak into say() arguments (`}\n`, tags)."""
    return _SAY_JUNK_RE.sub("", (text or "").strip()).strip()


def perception_exhausted(tool_names: list[str]) -> bool:
    """True once the turn has looked enough; further see()/look() add nothing but delay."""
    return tool_names.count("see") >= MAX_SEE_BEFORE_SAY


# Utterance kinds.  "social" kinds get the perception tools withheld.
KIND_VISUAL_REQUEST = "visual_request"  # 見て／どう見える／部屋の様子
KIND_SHARE_VISUAL = "share_visual"  # 見て見て、これ買った
KIND_GREETING = "greeting"  # ただいま／おはよう
KIND_VENTING = "venting"  # 疲れた／しんどい／怒られた
KIND_DEFLECTION = "deflection"  # 別に／なんもない
KIND_INDIRECT = "indirect_request"  # ちょっと〜が…
KIND_DISCLOSURE = "disclosure"  # 明日面接／病院
KIND_IMPLICATURE = "implicature"  # いいよね、若いって（本音は別にある）
KIND_SHARE_JOY = "share_joy"  # バグ直せた／受かった（喜びの共有）
KIND_GENERAL = "general"

SOCIAL_KINDS = frozenset(
    {
        KIND_GREETING,
        KIND_VENTING,
        KIND_DEFLECTION,
        KIND_INDIRECT,
        KIND_DISCLOSURE,
        KIND_IMPLICATURE,
        KIND_SHARE_JOY,
    }
)


@dataclass(frozen=True)
class SocialTurn:
    kind: str
    camera_ok: bool
    max_sentences: int = 2
    max_questions: int = 1
    note: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_social(self) -> bool:
        return self.kind in SOCIAL_KINDS


_VISUAL_REQ = re.compile(
    r"(見て(?!見て)|みて(?!みて)|見える|みえる|部屋の様子|外はどう|何が見える|どんな感じ|"
    r"look|what do you see|can you see|show me|check the room)",
    re.IGNORECASE,
)
_SHARE_VISUAL = re.compile(
    r"(見て見て|みてみて|これ買|これ作|ほら[、,]?これ|look what|check this out)", re.IGNORECASE
)
_GREETING = re.compile(
    r"^(ただいま|おはよ|おはよう|こんにちは|こんばんは|おやすみ|いってきます|"
    r"i'?m home|good (morning|night|evening)|hello|hi)[ー〜~!！。．\s]*$",
    re.IGNORECASE,
)
_VENTING = re.compile(
    r"(疲れ|しんど|つら|辛|だる|きつ|むかつ|イライラ|腹立|怒られ|言われ|最悪|うざ|もう嫌|泣き|"
    r"寝れ|寝られ|眠れ|寝てない|寝不足|"
    r"exhaust|tired|rough day|frustrat|annoy|upset|my boss)",
    re.IGNORECASE,
)
_DEFLECTION = re.compile(
    r"^(別に|べつに|なんもない|何もない|なんでもない|大丈夫|いいよ(?!ね)|いいの|nothing|it'?s nothing|i'?m fine)"
    r"[、。…\s]*",
    re.IGNORECASE,
)
_IMPLICATURE = re.compile(
    r"(いいよね[、,]?.+って[。．]?$|いいなぁ?[、,]?.+は|羨まし|うらやまし|must be nice|easy for you)",
    re.IGNORECASE,
)
_INDIRECT = re.compile(
    r"(ちょっと.*(が|は)[…\.]{1,3}$|少し.*(が|は)[…\.]{1,3}$|a bit\.{2,}$|kind of\.{2,}$)",
    re.IGNORECASE,
)
_SHARE_JOY = re.compile(
    r"(直せた|直った|できた|出来た|受かった|合格|うまくいった|終わった|終えた|やっと|達成|"
    r"finally|fixed it|passed|nailed it|got it working)",
    re.IGNORECASE,
)
_DISCLOSURE = re.compile(
    r"(面接|試験|テスト|発表|プレゼン|病院|検査|手術|熱がある|風邪|頭痛|胃|腰|眠れ|寝てない|"
    r"interview|exam|hospital|doctor|fever|headache|couldn'?t sleep)",
    re.IGNORECASE,
)


def classify_turn(text: str) -> SocialTurn:
    """Classify one user utterance.  Order matters: explicit visual bids win."""
    t = (text or "").strip()
    if not t:
        return SocialTurn(KIND_GENERAL, camera_ok=True)
    if _SHARE_VISUAL.search(t):
        return SocialTurn(
            KIND_SHARE_VISUAL, camera_ok=True, note="join the moment: see() then say()"
        )
    if _VISUAL_REQ.search(t):
        return SocialTurn(KIND_VISUAL_REQUEST, camera_ok=True, max_sentences=3)
    if _GREETING.match(t):
        return SocialTurn(KIND_GREETING, camera_ok=False, max_sentences=1, max_questions=1)
    if _IMPLICATURE.search(t):
        return SocialTurn(
            KIND_IMPLICATURE, camera_ok=False, note="the real message is under the words"
        )
    if _INDIRECT.search(t):
        return SocialTurn(
            KIND_INDIRECT, camera_ok=False, note="indirect request — offer, don't deny"
        )
    if _DEFLECTION.match(t):
        return SocialTurn(KIND_DEFLECTION, camera_ok=False, max_sentences=1, max_questions=0)
    if _VENTING.search(t):
        return SocialTurn(KIND_VENTING, camera_ok=False, note="validate before advice")
    if _DISCLOSURE.search(t):
        return SocialTurn(
            KIND_DISCLOSURE, camera_ok=False, note="remember(companion_status) then say()"
        )
    if _SHARE_JOY.search(t):
        return SocialTurn(KIND_SHARE_JOY, camera_ok=False, note="share the joy; no follow-up quiz")
    return SocialTurn(KIND_GENERAL, camera_ok=True)


def allowed_tools(tool_defs: list[dict], turn: SocialTurn) -> list[dict]:
    """Withhold perception tools on social turns; leave everything else."""
    if turn.camera_ok:
        return tool_defs
    return [t for t in tool_defs if t.get("name") not in PERCEPTION_TOOLS]


_HALLUCINATED_TOOL_RE = re.compile(
    r"<tool_(?:code|call|use)>.*?(?:</tool_(?:code|call|use)>|$)", re.DOTALL | re.IGNORECASE
)
_STAGE_DIRECTION_RE = re.compile(r"^[（(][^）)\n]{1,40}[）)]\s*$", re.MULTILINE)
_TTS_TAG_RE = re.compile(r"\[[a-zA-Z][a-zA-Z ]{1,24}\]")


def strip_hallucinated_tool_text(text: str) -> str:
    """Remove pseudo tool-call blocks, stage directions and [tts-tags] from prose."""
    cleaned = _HALLUCINATED_TOOL_RE.sub("", text or "")
    cleaned = _STAGE_DIRECTION_RE.sub("", cleaned)
    cleaned = _TTS_TAG_RE.sub("", cleaned)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


_TEXTUAL_SAY_RE = re.compile(
    r"^\s*say\(\s*(?P<q>[\"'“「])(?P<body>.*?)(?:[\"'”」])\s*\)\s*[。.]?\s*$", re.DOTALL
)


def unwrap_textual_say(text: str) -> str:
    """``say("…")`` written as prose → the inner text.

    Small models imitate the examples literally instead of emitting a tool call;
    the words are still theirs, so speak them.
    """
    m = _TEXTUAL_SAY_RE.match(text or "")
    return m.group("body").strip() if m else (text or "")


def normalize_small_model_text(text: str) -> str:
    """Full cleanup pipeline for prose from a small model."""
    return unwrap_textual_say(strip_hallucinated_tool_text(text))


_KANA_RE = re.compile(r"[\u3040-\u30ff]")
_HAN_RE = re.compile(r"[\u4e00-\u9fff]")
_LATIN_WORD_RE = re.compile(r"[A-Za-z]{2,}")


# Simplified-Chinese-only characters that never occur in Japanese text.  A single one
# inside an otherwise Japanese reply means the model slipped into Chinese mid-sentence.
_SIMPLIFIED_ONLY = set(
    "说们这个时会过还没对开关见现经给让从应该问题样们种为发点说话长间东西边儿电脑"
)
_SIMPLIFIED_RE = re.compile("[" + "".join(sorted(_SIMPLIFIED_ONLY)) + "]")


def language_mismatch(user_text: str, reply: str) -> bool:
    """True when a Japanese utterance got a reply that is not (entirely) Japanese.

    Multilingual small models (qwen) drift into Chinese or English mid-conversation.
    Heuristics, only when the person used kana:
    - the reply has no kana at all but has Han characters or Latin words, or
    - the reply contains simplified-Chinese-only characters (mixed-script drift).
    Other languages pass through unguarded.
    """
    if not _KANA_RE.search(user_text or ""):
        return False
    body = (reply or "").strip()
    if not body:
        return False
    if _SIMPLIFIED_RE.search(body):
        return True
    if _KANA_RE.search(body):
        return False
    return bool(_HAN_RE.search(body) or _LATIN_WORD_RE.search(body))


def trim_spoken(text: str, user_text: str, max_sentences: int) -> str:
    """Keep a social reply short: drop an echo of the person's own line and cut to
    ``max_sentences``.  Deterministic brevity for TTS — small models ramble."""
    parts = [p.strip() for p in _SENTENCE_SPLIT.split(text or "") if p and p.strip()]
    user_norm = re.sub(r"[\s。．!！?？、,]", "", user_text or "")
    kept = [p for p in parts if user_norm and re.sub(r"[\s。．!！?？、,]", "", p) != user_norm]
    if not kept:
        kept = parts
    return "".join(kept[: max(1, max_sentences)]) if kept else (text or "")


_SENTENCE_SPLIT = re.compile(r"(?<=[。！？!?])\s*|\n+")


def count_sentences(text: str) -> int:
    parts = [p for p in _SENTENCE_SPLIT.split(text or "") if p and p.strip()]
    return len(parts)


def count_questions(text: str) -> int:
    return (text or "").count("？") + (text or "").count("?")


# Speech acts from SocialPolicyEngine that are about the person, not the world:
# the camera is never the right reply to them.
SOCIAL_ACTS = frozenset(
    {
        "venting",
        "fatigue_signal",
        "grief_signal",
        "conflict_signal",
        "bid_for_connection",
        "delight_share",
        "boundary_assertion",
        "greeting",
        "acknowledgement",
    }
)


def is_social_turn(user_input: str, primary_act: str | None = None) -> bool:
    """Combine the lexical classifier with the social-policy speech act."""
    if primary_act in SOCIAL_ACTS and not _SHARE_VISUAL.search(user_input or ""):
        return True
    return classify_turn(user_input).is_social


def turn_kind(user_input: str) -> SocialTurn:
    return classify_turn(user_input)


class SocialReflexHook(RuntimeHookBase):
    """Deterministic guards for small local models, run inside the ReAct loop.

    - a say() in the wrong language is not spoken; one re-ask
    - say("") is silence: one re-ask for the words
    - say() arguments are stripped of leaked tool syntax
    - end-turn prose is normalised (pseudo tool blocks, stage directions,
      literal say("…")), checked for language drift (one re-ask), asked once
      if empty, and trimmed on social turns
    - once say() has been called on a social turn, the model is told to stop
    """

    STATE_KEY = "social_reflex"

    def __init__(self, agent: Any) -> None:
        self._agent = agent

    # ── per-turn state ────────────────────────────────────────────
    def _state(self, ctx: "TurnContext") -> dict[str, Any]:
        state = ctx.metadata.get(self.STATE_KEY)
        if state is None:
            state = {
                "turn": classify_turn(ctx.user_input),
                "language_retried": False,
                "empty_retried": False,
                "say_used": False,
                "stop_nudged": False,
            }
            ctx.metadata[self.STATE_KEY] = state
        return state

    @staticmethod
    def _is_desire_turn(ctx: "TurnContext") -> bool:
        prep = ctx.metadata.get("prep")
        return bool(getattr(prep, "is_desire_turn", False))

    # ── hooks ─────────────────────────────────────────────────────
    async def after_model_result(
        self,
        ctx: "TurnContext",
        result: "ModelTurnResult",
    ) -> "ModelTurnResult | RetryDecision | None":
        if self._is_desire_turn(ctx):
            return None
        state = self._state(ctx)
        user_input = ctx.user_input

        if result.stop_reason == "tool_use":
            says = [tc for tc in result.tool_calls if tc.name == "say"]
            for tc in says:
                if isinstance(tc.input, dict):
                    tc.input["text"] = clean_say_text(str(tc.input.get("text", "")))
            if says and all(not str(tc.input.get("text", "")).strip() for tc in says):
                if not state["empty_retried"]:
                    state["empty_retried"] = True
                    logger.info("Social reflex: empty say(), asking for the words")
                    return RetryDecision(
                        retry=True,
                        inject_user_message=(
                            "Nothing was spoken: say() needs the words as text. "
                            "Call say() again with one or two sentences."
                        ),
                    )
            if not state["language_retried"] and any(
                language_mismatch(user_input, str(tc.input.get("text", ""))) for tc in says
            ):
                state["language_retried"] = True
                logger.info("Social reflex: say() language mismatch, asking for a redo")
                return RetryDecision(
                    retry=True,
                    inject_user_message=(
                        "Not spoken: wrong language. Reply in the same language the person "
                        "used, then call say() again."
                    ),
                )
            return None

        # end_turn: normalise prose
        text = normalize_small_model_text(result.text or "")
        if not text.strip() and not state["say_used"] and not state["empty_retried"]:
            state["empty_retried"] = True
            logger.info("Social reflex: empty reply, asking for one short say()")
            return RetryDecision(
                retry=True,
                inject_user_message=(
                    "You said nothing. Reply to the person with one short say() now."
                ),
            )
        if not state["language_retried"] and language_mismatch(user_input, text):
            state["language_retried"] = True
            logger.info("Social reflex: reply language mismatch, asking for a redo")
            return RetryDecision(
                retry=True,
                inject_user_message="Reply in the same language the person used. Say it again.",
            )
        turn: SocialTurn = state["turn"]
        if turn.is_social and text:
            text = trim_spoken(text, user_input, turn.max_sentences) or text
        if text != (result.text or ""):
            from dataclasses import replace

            return replace(result, text=text)
        return None

    async def after_tool_result(
        self,
        ctx: "TurnContext",
        call: "ToolCall",
        result: "ToolExecutionResult",
    ) -> "ToolExecutionResult | None":
        state = self._state(ctx)
        if call.name == "say" and str((call.input or {}).get("text", "")).strip():
            state["say_used"] = True
        return None

    async def mid_turn_user_messages(self, ctx: "TurnContext", iteration: int) -> list[str]:
        if iteration == 0 or self._is_desire_turn(ctx):
            return []
        state = self._state(ctx)
        turn: SocialTurn = state["turn"]
        if turn.is_social and state["say_used"] and not state["stop_nudged"]:
            state["stop_nudged"] = True
            return ["You already spoke. End your turn now without further tools."]
        return []
