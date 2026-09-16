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

# Utterance kinds.  "social" kinds get the perception tools withheld.
KIND_VISUAL_REQUEST = "visual_request"  # 見て／どう見える／部屋の様子
KIND_SHARE_VISUAL = "share_visual"  # 見て見て、これ買った
KIND_GREETING = "greeting"  # ただいま／おはよう
KIND_VENTING = "venting"  # 疲れた／しんどい／怒られた
KIND_DEFLECTION = "deflection"  # 別に／なんもない
KIND_INDIRECT = "indirect_request"  # ちょっと〜が…
KIND_DISCLOSURE = "disclosure"  # 明日面接／病院
KIND_IMPLICATURE = "implicature"  # いいよね、若いって（本音は別にある）
KIND_GENERAL = "general"

SOCIAL_KINDS = frozenset(
    {
        KIND_GREETING,
        KIND_VENTING,
        KIND_DEFLECTION,
        KIND_INDIRECT,
        KIND_DISCLOSURE,
        KIND_IMPLICATURE,
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


_SENTENCE_SPLIT = re.compile(r"(?<=[。！？!?])\s*|\n+")


def count_sentences(text: str) -> int:
    parts = [p for p in _SENTENCE_SPLIT.split(text or "") if p and p.strip()]
    return len(parts)


def count_questions(text: str) -> int:
    return (text or "").count("？") + (text or "").count("?")
