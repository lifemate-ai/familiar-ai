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

import re
from dataclasses import dataclass, field

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
