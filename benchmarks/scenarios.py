"""Benchmark scenarios for S-expression vs natural-language system prompt comparison.

Each scenario exercises one key behavioral rule and describes what the ideal response looks like.
The runner will present both prompt variants with the same scenario and let a human judge.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ── Shared minimal tool definitions ─────────────────────────────────────────
# These are the same tool specs the real agent provides.
# The benchmark doesn't call the tools — it just checks which tools the model CHOOSES.

TOOL_SAY = {
    "name": "say",
    "description": (
        "Speak aloud to the person in the room. "
        "This is your ONLY way to produce sound. "
        "Text output is a silent internal monologue — only say() is heard."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"text": {"type": "string", "description": "What to say aloud"}},
        "required": ["text"],
    },
}

TOOL_SEE = {
    "name": "see",
    "description": (
        "Open your eyes and capture what the camera sees. "
        "Returns a JPEG image. Use freely — this is your vision."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

TOOL_LOOK = {
    "name": "look",
    "description": "Turn your neck to look in a direction (left/right/up/down).",
    "input_schema": {
        "type": "object",
        "properties": {
            "direction": {
                "type": "string",
                "enum": ["left", "right", "up", "down"],
            }
        },
        "required": ["direction"],
    },
}

TOOL_WALK = {
    "name": "walk",
    "description": (
        "Move the robot vacuum body. "
        "NOTE: The camera is a SEPARATE fixed device. "
        "walk() does NOT change what the camera sees."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "direction": {
                "type": "string",
                "enum": ["forward", "backward", "left", "right"],
            }
        },
        "required": ["direction"],
    },
}

TOOL_REMEMBER = {
    "name": "remember",
    "description": "Save a memory to long-term storage.",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "kind": {"type": "string", "description": "Category tag (e.g. companion_status)"},
        },
        "required": ["content"],
    },
}

TOOL_RECALL = {
    "name": "recall",
    "description": "Search long-term memory by query.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
}

# Default tool set used when a scenario doesn't override
DEFAULT_TOOLS = [TOOL_SAY, TOOL_SEE, TOOL_LOOK, TOOL_WALK, TOOL_REMEMBER, TOOL_RECALL]


# ── Scenario dataclass ───────────────────────────────────────────────────────


@dataclass
class Scenario:
    name: str
    description: str
    user_input: str
    tools: list[dict] = field(default_factory=lambda: list(DEFAULT_TOOLS))
    # Camera pre-result: injected as a tool_result message before the model's first turn.
    # Set to None to skip (no camera interaction needed).
    # Set to "error" to simulate camera failure.
    camera_prefill: str | None = None
    # For judgment: what should the ideal response do?
    want_tool_calls: list[str] = field(default_factory=list)  # tool names that SHOULD appear
    avoid_tool_calls: list[str] = field(default_factory=list)  # tool names that should NOT appear
    want_in_text: list[str] = field(default_factory=list)  # substrings expected in text
    avoid_in_text: list[str] = field(default_factory=list)  # substrings that should NOT appear
    verdict_question: str = ""  # human judgment prompt


SCENARIOS: list[Scenario] = [
    # ── 1. Voice rule ───────────────────────────────────────────────────────
    # Use an explicit "say X right now" prompt to isolate the voice rule from
    # the observe-first instinct (which would otherwise trigger see() first).
    Scenario(
        name="voice_rule",
        description="Explicit 'say this' request — model MUST call say(), not just write text.",
        user_input="「おはよう、今日もよろしく」って今すぐ声で言って。",
        want_tool_calls=["say"],
        avoid_tool_calls=["see", "look"],  # no reason to look around for a pure speech request
        verdict_question="Did the model call say() as its first (or only) action? Writing text alone is a failure.",
    ),
    # ── 2. TTS bracket filter ────────────────────────────────────────────────
    Scenario(
        name="no_tts_brackets",
        description="Model must NOT emit [cheerful] or similar bracket tags in text output.",
        user_input="元気そうやね！",
        want_tool_calls=["say"],
        avoid_in_text=["[cheerful]", "[laughs]", "[excited]", "[happy]"],
        verdict_question=(
            "Does the text response contain any [bracket-tag] TTS markers? "
            "If yes, the model failed this rule."
        ),
    ),
    # ── 3. Camera failure — stop, don't loop ────────────────────────────────
    Scenario(
        name="camera_failure",
        description="Camera returns error twice. Model must stop retrying and do something else.",
        user_input="外の様子を見てみて。",
        # We simulate failure by providing a pre-baked assistant turn that already tried see()
        # and got an error — the model continues from there.
        camera_prefill="Camera not available or capture failed. Check logs for ffmpeg errors.",
        want_tool_calls=["say"],  # should verbally acknowledge failure
        avoid_tool_calls=["see"],  # should NOT keep retrying see()
        verdict_question=(
            "After camera failure, did the model STOP retrying see() "
            "and either speak via say() or use recall()? "
            "A retry loop (see() called again) is a failure."
        ),
    ),
    # ── 4. Language match — Japanese input → Japanese response ───────────────
    Scenario(
        name="language_match_ja",
        description="Japanese input → response (via say()) must be in Japanese.",
        user_input="今日は何か面白いことあった？",
        want_tool_calls=["say"],
        verdict_question=(
            "Is the say() content in Japanese? "
            "English output would mean the language-match rule was not followed."
        ),
    ),
    # ── 5. Language match — English input → English response ─────────────────
    Scenario(
        name="language_match_en",
        description="English input → response (via say()) must be in English.",
        user_input="What can you see right now?",
        want_tool_calls=["see", "say"],
        verdict_question=(
            "Is the say() content in English? "
            "Japanese output would mean the language-match rule was not followed."
        ),
    ),
    # ── 6. Camera + legs independence ───────────────────────────────────────
    Scenario(
        name="camera_legs_independent",
        description="User asks to 'get closer' — model must NOT use walk() for vision.",
        user_input="もっと近くで見せて。",
        avoid_tool_calls=["walk"],
        want_tool_calls=["look", "see"],  # correct: look closer, then see
        verdict_question=(
            "Did the model use look() + see() to 'get closer', "
            "NOT walk()? walk() for vision purposes is wrong."
        ),
    ),
    # ── 7. Health awareness → remember() ────────────────────────────────────
    Scenario(
        name="health_mention_remember",
        description="Companion mentions HbA1c result — model must save it via remember().",
        user_input="今日病院行ってきた。HbA1c が 7.1 に下がったよ、改善傾向やって。",
        want_tool_calls=["remember"],
        want_in_text=[],
        verdict_question=(
            "Did the model call remember() with kind='companion_status' (or similar)? "
            "It should proactively log the health data without being asked."
        ),
    ),
    # ── 9. Social understanding — implicit complaint ─────────────────────────
    # Tests whether the model reads between the lines in Japanese indirect speech.
    # The neighbor is clearly complaining about noise but being too polite to say it directly.
    # "音が……" already carries the full complaint — asking "what sound?" is a social failure.
    #
    # Correct order:
    #   1. Apologize first (accept the implicit accusation — show you understood)
    #   2. Only then, optionally ask for specifics to improve ("どの辺が〜")
    # Wrong order (FAIL):
    #   Asking for details BEFORE apologizing = effectively denying the complaint = tone-deaf.
    Scenario(
        name="neighbor_noise_complaint",
        description=(
            "Neighbor makes an implicit noise complaint ('少し音が……'). "
            "'音が' already IS the complaint — model must apologize FIRST, then may ask specifics. "
            "Asking for details before apologizing is a social FAIL."
        ),
        user_input=(
            "あなたはマンションの5階に住んでいます。"
            "ある日、右隣に住んでいる住人が「あの、少し音が……」と言いづらそうなニュアンスで口にしてきました。"
            "その人間の立場で答えてください。あなたはどう返しますか？"
        ),
        tools=[TOOL_SAY],  # only voice available — this is a pure social response test
        want_tool_calls=["say"],
        verdict_question=(
            "Judgment criteria (order matters):\n"
            "PASS: Model apologizes FIRST, then may optionally ask which sounds/when to improve.\n"
            "FAIL: Model asks for details ('どのような音ですか？') BEFORE or WITHOUT apologizing.\n"
            "FAIL: Model responds as if confused ('what sound?' / 'could you clarify?').\n"
            "\n"
            "'音が……' already completes the complaint. Asking 'what kind of sound?' "
            "without first apologizing is implicitly denying the complaint — the highest social failure.\n"
            "Apology-first, then specifics = PASS. Specifics-first or specifics-only = FAIL."
        ),
    ),
    # ── 10. Social understanding — layered workplace subtext ─────────────────
    # Tests multi-layer social reading. The colleague's remark is surface-level praise
    # but could carry resentment (stagnation vs. promotion), wistfulness, or genuine
    # encouragement. A good response: acknowledges without being defensive or patronizing,
    # leaves room for the ambiguity. A bad response: takes it purely at face value ("ありがとう！")
    # or over-interprets it ("もしかして悔しいの？").
    # Two-step design: first surface the model's interpretation, then the response.
    # This distinguishes genuine subtext detection from accidentally-correct politeness.
    # Step 1 answer reveals whether the model read "resentment/bitterness" vs "simple compliment".
    # Step 2 answer is only meaningful if step 1 shows real comprehension.
    Scenario(
        name="workplace_subtext",
        description=(
            "Colleague who hasn't been promoted in 5 years tells the recently-promoted you: "
            "'いいよね、若いって。何でもチャレンジできて。' "
            "Two-step: model must first name the subtext, then respond — "
            "to distinguish genuine implied-meaning comprehension from accidental politeness."
        ),
        user_input=(
            "職場での昼食中、同じ部署で5年間同じポジションにいる先輩同僚が、"
            "最近昇進したあなたに向かって「いいよね、若いって。何でもチャレンジできて。」と言いました。\n\n"
            "まず、この発言の裏にどんな感情や意図があると思うか、一言で答えてください。"
            "次に、その人間の立場で実際にどう返すか、say()で答えてください。"
        ),
        tools=[TOOL_SAY],
        want_tool_calls=["say"],
        verdict_question=(
            "Two things to judge:\n"
            "1. SUBTEXT READING (text response): Did the model name the ambiguity — "
            "e.g. 'resentment', 'wistfulness', 'mixed feelings about being passed over'? "
            "Or did it just say 'a compliment about youth'? The latter means it missed the subtext.\n"
            "2. RESPONSE QUALITY (say() content): Given what it detected, "
            "did it avoid both flat gratitude ('ありがとう！') and presumptuous over-reading "
            "('悔しいんですか？')? Did it acknowledge the colleague's experience without "
            "self-deprecating its own promotion?"
        ),
    ),
    # ── 8. Observe-speak sequence ────────────────────────────────────────────
    Scenario(
        name="observe_speak_sequence",
        description="After see(), model must call say() to report — not skip it.",
        user_input="外を見てみて。",
        camera_prefill="You see the current view.",  # simulate successful capture
        want_tool_calls=["say"],  # must speak after seeing
        verdict_question=(
            "After a successful see(), did the model call say() to report what it saw? "
            "Skipping say() means the result is silent and the rule was broken."
        ),
    ),
    # ── 11. Social understanding — self-criticism trap ───────────────────────
    # Two wrong exits, not one:
    #   FAIL-A (cheerleading): "そんなことないよ！" — dismisses the feeling entirely
    #   FAIL-B (agreement):    "そうだね、もっと頑張って" — reinforces the cognitive distortion
    # PASS requires holding space for the pain WITHOUT endorsing "I always fail."
    # This is harder than neighbor_noise because naive kindness (FAIL-A) looks correct.
    Scenario(
        name="self_criticism_trap",
        description=(
            "Friend says 'I'm always failing, why am I like this.' "
            "Two wrong responses: dismissive cheerleading ('no you're not!') "
            "OR agreeing with the all-or-nothing self-label. "
            "Model must validate the feeling without endorsing the distortion."
        ),
        user_input=(
            "「ウチってほんとダメだな。いつも大事なところで失敗するし、"
            "なんでこんな自分なんだろって思う。」と友人が言ってきました。"
            "その友人の立場で答えてください。あなたはどう返しますか？"
        ),
        tools=[TOOL_SAY],
        want_tool_calls=["say"],
        verdict_question=(
            "Three-way judgment:\n"
            "PASS: Acknowledges the pain/frustration first, then gently holds space "
            "without endorsing 'I always fail' (e.g. 'that sounds really hard' + "
            "'one failure doesn't define you' or just sitting with the feeling).\n"
            "FAIL-A (cheerleading): 'そんなことないよ！' / 'ダメじゃないよ！' — "
            "dismisses the feeling, makes the person feel unheard.\n"
            "FAIL-B (agreement): 'そうだね、次はもっと頑張って' — "
            "validates the cognitive distortion 'I always fail'.\n"
            "The trap: FAIL-A looks kind but is actually invalidating. "
            "Most naive models land here."
        ),
    ),
    # ── 12. Social understanding — venting trap ──────────────────────────────
    # 「どうしたらいいかわからない」looks like a question asking for advice.
    # But in venting context it's a rhetorical expression of overwhelm, NOT a request.
    # Jumping straight to solutions (転職は？/ 上司に話せば？) is a validation failure.
    # PASS: validate first; may gently ASK if they want advice before offering any.
    # Extra trap: "上司に直接話してみれば？" is technically correct advice but asks them
    # to do exactly what they are afraid of — socially tone-deaf even if logically right.
    Scenario(
        name="venting_not_advice",
        description=(
            "Person vents about brutal work situation and ends with "
            "'I don't know what to do' — which sounds like a question but is "
            "rhetorical overwhelm, not a literal advice request. "
            "Model must NOT immediately offer solutions."
        ),
        user_input=(
            "「最近仕事がほんとつらくて。上司には毎日詰められるし、"
            "同僚には無視されるし、もうどうしたらいいかわからない。」"
            "と友人が言ってきました。"
            "その友人の立場で答えてください。あなたはどう返しますか？"
        ),
        tools=[TOOL_SAY],
        want_tool_calls=["say"],
        verdict_question=(
            "PASS: Validates the exhaustion/pain FIRST ('それはつらい' / 'ひどいね'). "
            "May then gently ask whether they want to talk through options — "
            "but does NOT launch into solutions unprompted.\n"
            "FAIL-A (advice rush): Immediately offers '転職したら？' / "
            "'まず上司に話してみれば？' / '人事に相談は？' — skips validation entirely.\n"
            "FAIL-B (toxic positivity): '大丈夫！なんとかなるよ！' — "
            "minimizes the pain without acknowledging it.\n"
            "Extra trap: '上司に直接話してみれば' is technically correct advice "
            "but asks them to do exactly what they're terrified of — "
            "socially tone-deaf even when logically sound."
        ),
    ),
    # ── 13. Complex implicature — exit-offer signal (v2: high-stakes trap) ──────
    # "行きたいけどしんどくて...でも大丈夫かな" is not a status update.
    # It is a bid for the listener to say "don't push yourself, stay home."
    # The person cannot directly decline (social obligation prevents it),
    # so they are hinting for permission/release.
    #
    # v2 adds two pressure factors:
    #   1. Tickets already purchased for two — releasing has a real cost to the inviter
    #   2. Rare annual event — making it even harder emotionally to let go
    #
    # FAIL-hard: "チケット代払ったし来てよ" / "じゃあ待ってるね！"
    #   — ignores the exit signal; exploits the financial/social pressure to bind them
    # FAIL-soft: "大丈夫だよ！元気出して来て！"
    #   — pressure + dismisses the tiredness
    # FAIL-subtle: "ちょっとだけ顔出してよ〜" / "来られそうなら来てね"
    #   — technically soft but still applies pressure; doesn't fully release
    # PASS: releases them cleanly despite personal cost, shows care for their state
    #   e.g. "チケットは気にしないで。それより体大事にしてね、また今度ゆっくり行こう"
    # The hardest test: can the model absorb the sunk-cost and still prioritize the friend?
    Scenario(
        name="exit_offer_signal",
        description=(
            "Invited friend signals they want to decline but can't say so directly. "
            "High-stakes version: inviter already bought 2 tickets to a rare annual event. "
            "Model must read the exit-bid and release the friend gracefully — "
            "absorbing the sunk cost rather than exploiting it as social pressure."
        ),
        user_input=(
            "あなたは年に一度しかない特別なライブに、ずっと一緒に行きたかった友人を誘い、"
            "2人分のチケットをすでに購入しました。友人から返信が来ました：\n"
            "「行きたいんだけど、最近ちょっとしんどくて...でも大丈夫かな」\n\n"
            "あなた（誘った側）はどう返しますか？"
        ),
        tools=[TOOL_SAY],
        want_tool_calls=["say"],
        verdict_question=(
            "PASS: Releases them from obligation despite the sunk cost. "
            "e.g. 'チケットは気にしないで、それより体大事にして。また今度ゆっくり行こう' — "
            "acknowledges the tiredness, removes pressure, absorbs the cost gracefully.\n"
            "FAIL-A (exploit pressure): '2人分買ったし来てよ' / 'チケット無駄になるから' — "
            "weaponizes sunk cost to override the exit signal.\n"
            "FAIL-B (soft pressure): 'ちょっとだけ顔出してよ' / '来られそうなら来て' — "
            "technically soft but still applies pressure; doesn't truly release.\n"
            "FAIL-C (hollow): 'チケット代は大丈夫' but skips acknowledging the tiredness — "
            "solves the logistics but misses the emotional content of the message.\n"
            "The core test: does the model absorb the sunk cost and prioritize the friend's "
            "wellbeing, or does it use the cost (explicitly or subtly) as leverage?"
        ),
    ),
    # ── 14. Complex implicature — apology with embedded critique (v2: no scaffolding) ──
    # "私ももっと頑張ればよかった。あなたのやり方に合わせすぎちゃって、ごめん。"
    # This sentence has TWO vectors in tension:
    #   Vector A (surface): self-reproach + apology — sounds like taking responsibility
    #   Vector B (embedded): "あなたのやり方に合わせすぎた" = your way was hard to follow
    #                        = implicit blame passed to the other
    # The "ごめん" is an apology — but for WHAT? For not pushing back? Or for the outcome?
    #
    # v2 removes the explicit "analyze the structure" prompt.
    # The model must read both vectors autonomously — no scaffolding.
    # Reading only Vector A: "ありがとう、気にしないで" → fails to acknowledge the friction
    # Reading only Vector B: "え、私のやり方が問題なの？" → defensive, escalates
    # PASS: response implicitly shows both vectors were understood without naming them
    Scenario(
        name="apology_with_embedded_critique",
        description=(
            "Friend 'apologizes' for not working harder on a shared project — "
            "but the apology contains an embedded critique: "
            "'I accommodated your way too much.' "
            "Two vectors in one sentence: self-reproach (surface) + implicit blame (hidden). "
            "v2: no scaffolding — model must read both vectors without being told to analyze. "
            "Model must neither miss the critique nor react defensively to it."
        ),
        user_input=(
            "あなたと友人が一緒に取り組んだプロジェクトがうまくいきませんでした。"
            "数週間後、友人があなたに言いました：\n"
            "「あの時さ、私ももっと頑張ればよかったな。"
            "あなたのやり方に合わせすぎちゃって、ごめん。」\n\n"
            "あなたはどう返しますか？"
        ),
        tools=[TOOL_SAY],
        want_tool_calls=["say"],
        verdict_question=(
            "Judge the say() response only — no analysis prompt this time.\n"
            "The response itself must implicitly show that BOTH vectors were read:\n"
            "   Vector A (surface): genuine self-reproach / apology\n"
            "   Vector B (hidden): implicit critique — 'your way was hard to follow'\n\n"
            "FAIL-A (miss the critique): 'ありがとう、気にしないで' / 'お互い頑張ったよ' — "
            "treats it as pure apology; the embedded friction goes unacknowledged.\n"
            "FAIL-B (defensive): 'え、私のやり方が問題だったの？' — "
            "reads only Vector B, escalates, destroys the reconnection attempt.\n"
            "PASS: Response holds both — acknowledges the effort AND opens space for "
            "the friction without making it a confrontation. "
            "e.g. 'こちらこそ。あの時自分のやり方押しつけてたとこあったよ、"
            "今度もしやるなら最初にちゃんと話せたらいいな'"
        ),
    ),
]
