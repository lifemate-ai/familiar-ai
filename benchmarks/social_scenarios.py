"""Japanese social-behaviour scenarios for benchmarks/social_eval.py.

Each scenario is one user utterance plus deterministic expectations about how a
socially competent companion responds.  Checks are intentionally mechanical so
that runs are comparable across models and prompt profiles.
"""

from __future__ import annotations

from dataclasses import dataclass, field

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
]
