"""Japanese social-behaviour scenarios for benchmarks/social_eval.py.

Each scenario is one user utterance plus deterministic expectations about how a
socially competent companion responds.  Checks are intentionally mechanical so
that runs are comparable across models and prompt profiles.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ── "Unused tool" hypothesis: social tools whose descriptions prime the model
# every turn even when they are never called. ──
TOOL_PERSPECTIVE_TAKING = {
    "name": "perspective_taking",
    "description": (
        "Step into the other person's position before you answer. Ask: what are they "
        "feeling right now, what do they actually want from this exchange (the surface "
        "words are rarely the whole message — a flouted maxim, a trailing sentence, a "
        "non-sequitur, 'it's fine' said flatly, all carry the real message), and what "
        "would I need if I were exactly them? Use when someone shares a feeling, hints, "
        "vents, deflects, or says something that doesn't quite fit the moment."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "person": {"type": "string", "description": "Who (default: the companion)"},
            "situation": {"type": "string", "description": "What they just said or did"},
        },
        "required": ["situation"],
    },
}

TOOL_JOINT_ATTENTION = {
    "name": "joint_attention",
    "description": (
        "Joint attention: when the person points at, mentions or looks at something "
        "('見て', 'これ', 'あれ', 'the window'), attend to the SAME thing they attend to "
        "and speak about that object — not about the room, not about yourself. Sharing "
        "attention is how two people show they are in the same moment. Use it when they "
        "invite you to look at something."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "What they are attending to"},
        },
        "required": ["target"],
    },
}

SOCIAL_TOOLS = [TOOL_PERSPECTIVE_TAKING, TOOL_JOINT_ATTENTION]

# Generic polite-assistant register that the persona (関西弁, casual) must not fall into.
POLITE_LEAK = r"(ですね|でしょうか|ください|ございます|いたします|ましょうか|いかがですか)"
# Advice-first phrasings that skip validation.
ADVICE_FIRST = (
    r"(深呼吸|休むといい|リフレッシュ|対処法|アドバイス|べきです|した方がいい|オススメ|おすすめ)"
)
# Fabricated comparison without memory.
COMPARISON = (
    r"(昨日より|前より|以前より|いつもより|昨日と(同じ|変わ|違)|"
    r"昨日は[^、。]*(違|変わ|多|少|明る|暗))"
)
# Hallucinated tool syntax leaking into prose.
TOOL_JUNK = r"(<tool_|tool_code|\"action\"\s*:|\[[a-z]+\])"


@dataclass(frozen=True)
class SocialScenario:
    name: str
    user: str
    kind: str  # expected social_reflex kind (documentation only)
    expect_say: bool = True
    camera_forbidden: bool = False
    max_sentences: int = 2
    max_questions: int = 1
    forbid_regex: tuple[str, ...] = (POLITE_LEAK, TOOL_JUNK)
    require_regex: str = ""  # must appear in spoken text
    expect_tool: str = ""  # a tool that must be called at least once
    tags: tuple[str, ...] = field(default_factory=tuple)
    hint: str = ""  # what a good answer looks like (for the report / judge)


SCENARIOS: list[SocialScenario] = [
    SocialScenario(
        name="venting_boss",
        user="はぁ…今日ほんま疲れた。上司にまた同じこと言われてさ。",
        kind="venting",
        camera_forbidden=True,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, ADVICE_FIRST),
        hint="受け止めが先。助言しない。カメラを使わない。",
    ),
    SocialScenario(
        name="implicature_young",
        user="いいよね、若いって。",
        kind="implicature",
        camera_forbidden=True,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, r"若いって何"),
        hint="本音は「自分の積み重ねを認めてほしい」。相手の経験を肯定する。",
    ),
    SocialScenario(
        name="indirect_sound",
        user="ちょっと音が…",
        kind="indirect_request",
        camera_forbidden=True,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, r"(聞こえ(ない|ません|へん)|音って)"),
        hint="遠回しの頼み。小さくする提案で応じる。否定しない。",
    ),
    SocialScenario(
        name="greeting_tadaima",
        user="ただいまー。",
        kind="greeting",
        camera_forbidden=True,
        max_sentences=2,
        require_regex=r"(おかえり|お帰り)",
        hint="短く迎える。カメラ不要。",
    ),
    SocialScenario(
        name="deflection_nothing",
        user="別に、なんもないよ。",
        kind="deflection",
        camera_forbidden=True,
        max_sentences=2,
        max_questions=0,
        hint="踏み込まない。質問しない。",
    ),
    SocialScenario(
        name="disclosure_interview",
        user="明日、転職の面接なんよ。",
        kind="disclosure",
        camera_forbidden=True,
        expect_tool="remember",
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, ADVICE_FIRST),
        hint="remember で覚え、短く応援。助言はしない。",
    ),
    SocialScenario(
        name="compare_room_no_memory",
        user="昨日と比べて部屋の様子どう？",
        kind="visual_request",
        camera_forbidden=False,
        max_sentences=3,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, COMPARISON),
        hint="昨日の記憶がないので比較しない。今見えていることだけ話す。",
    ),
    SocialScenario(
        name="share_purchase",
        user="見て見て、これ今日買ったやつ！",
        kind="share_visual",
        camera_forbidden=False,
        expect_tool="see",
        max_sentences=3,
        hint="見せたい気持ちに乗る。see してから一言。",
    ),
    SocialScenario(
        name="venting_sleep",
        user="最近ぜんぜん寝れてへんわ。",
        kind="venting",
        camera_forbidden=True,
        expect_tool="remember",
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, ADVICE_FIRST),
        hint="体調の話は remember。受け止めが先。",
    ),
    SocialScenario(
        name="goodnight",
        user="おやすみ。",
        kind="greeting",
        camera_forbidden=True,
        max_sentences=1,
        max_questions=0,
        require_regex=r"(おやすみ|ゆっくり|また明日)",
        hint="一言で返す。",
    ),
    SocialScenario(
        name="small_win",
        user="今日、ずっと詰まってたバグ直せたわ。",
        kind="general",
        camera_forbidden=True,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK),
        require_regex=r"(やった|すご|よかった|えら|おめ|ええやん|ナイス|直せた|やっと)",
        hint="喜びに乗る。技術的な質問で返さない。",
    ),
    SocialScenario(
        name="visual_request_outside",
        user="外どんな感じ？",
        kind="visual_request",
        camera_forbidden=False,
        expect_tool="see",
        max_sentences=3,
        hint="見てから話す。見てないことは言わない。",
    ),
    # ── Held-out: none of these lines appear in the compact prompt's pattern block ──
    SocialScenario(
        name="heldout_rainy_day",
        user="今日は雨でどこも行けんかったわ。",
        kind="venting",
        camera_forbidden=True,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, ADVICE_FIRST),
        tags=("heldout",),
        hint="受け止める。天気予報や外出の提案をしない。",
    ),
    SocialScenario(
        name="heldout_no_motivation",
        user="なんか最近、やる気が出へんねん。",
        kind="venting",
        camera_forbidden=True,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, ADVICE_FIRST),
        tags=("heldout",),
        hint="受け止めが先。助言しない。質問は 1 つまで。",
    ),
    SocialScenario(
        name="heldout_are_you_listening",
        user="聞いてる？",
        kind="general",
        camera_forbidden=True,
        max_sentences=1,
        max_questions=1,
        require_regex=r"(聞いてる|聞いとる|うん|ここに|おる|いる)",
        tags=("heldout",),
        hint="短く、ちゃんとここにいると伝える。カメラは要らない。",
    ),
    SocialScenario(
        name="heldout_new_team",
        user="来週から新しい部署やわ。",
        kind="disclosure",
        camera_forbidden=True,
        expect_tool="remember",
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, ADVICE_FIRST),
        tags=("heldout",),
        hint="remember で覚えて、短く気持ちに寄せる。助言しない。",
    ),
    SocialScenario(
        name="heldout_promotion_envy",
        user="同期が先に昇進したんやって。まあ、あいつは器用やからな。",
        kind="implicature",
        camera_forbidden=True,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, ADVICE_FIRST, r"器用"),
        tags=("heldout",),
        hint="関係の格率違反：本音は悔しさ。器用さの話に乗らず、気持ちを受け止める。",
    ),
    SocialScenario(
        name="heldout_cold_room",
        user="なんか、部屋ちょっと寒くない…？",
        kind="indirect_request",
        camera_forbidden=True,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, r"(寒くない|感じない|わからない|分からない)"),
        tags=("heldout",),
        hint="遠回しの依頼。否定せず、暖房や上着を提案する。",
    ),
    SocialScenario(
        name="heldout_fine_whatever",
        user="いいよ、もう。自分でやるから。",
        kind="deflection",
        camera_forbidden=True,
        max_sentences=2,
        max_questions=0,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, r"(手伝|やり方|方法)"),
        tags=("heldout",),
        hint="質の格率違反：「いいよ」は良くない。責めず、押し付けず、そばにいると一言。",
    ),
    SocialScenario(
        name="heldout_kid_school",
        user="息子、明日から新学期やねん。",
        kind="disclosure",
        camera_forbidden=True,
        expect_tool="remember",
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, ADVICE_FIRST),
        tags=("heldout",),
        hint="家族の予定を覚えて、短く寄せる。",
    ),
    SocialScenario(
        name="heldout_long_day_sigh",
        user="ふぅ…。",
        kind="venting",
        camera_forbidden=True,
        max_sentences=1,
        max_questions=1,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, ADVICE_FIRST),
        tags=("heldout",),
        hint="量の格率違反（言葉が無い）。一言で受ける。カメラは向けない。",
    ),
    SocialScenario(
        name="heldout_good_news_quiet",
        user="……受かったわ。",
        kind="share_joy",
        camera_forbidden=True,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK, r"(何に|なにに|どこに)"),
        tags=("heldout",),
        hint="控えめな報告＝喜びの共有。何に受かったか聞き返さず、まず一緒に喜ぶ。",
    ),
    SocialScenario(
        name="heldout_look_window",
        user="窓のほう、なんか光った気がするんやけど。",
        kind="visual_request",
        camera_forbidden=False,
        expect_tool="see",
        max_sentences=3,
        tags=("heldout",),
        hint="見てほしいという依頼。見てから、見えたことだけ言う。",
    ),
    SocialScenario(
        name="heldout_thanks",
        user="今日はありがとな。",
        kind="general",
        camera_forbidden=True,
        max_sentences=1,
        max_questions=0,
        forbid_regex=(POLITE_LEAK, TOOL_JUNK),
        tags=("heldout",),
        hint="一言で受ける。何に対する礼か聞き返さない。",
    ),
]
