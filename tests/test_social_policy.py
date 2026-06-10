from __future__ import annotations

from familiar_agent.appraisal import AppraisalContext, AppraisalEngine
from familiar_agent.interoception import InteroceptivePressure
from familiar_agent.meta_monitor import MetaMonitor
from familiar_agent.social_policy import SocialPolicyEngine


def _pressure(*, quiet: bool = False, need_rest: float = 0.2, frustration_bias: float = 0.2):
    return InteroceptivePressure(
        need_rest=need_rest,
        caution=0.3,
        expressivity=0.4,
        social_receptivity=0.6,
        frustration_bias=frustration_bias,
        quiet_mode=quiet,
    )


def test_tired_user_plus_interoception_validates_first_and_blocks_raw_metric_leakage() -> None:
    appraisal = AppraisalEngine()
    policy_engine = SocialPolicyEngine()
    monitor = MetaMonitor()

    affect = appraisal.appraise(
        AppraisalContext(
            user_text="今日はほんま疲れててしんどい",
            companion_mood="tired",
            interoception=_pressure(need_rest=0.75),
        )
    )
    decision = policy_engine.decide(
        user_text="今日はほんま疲れててしんどい",
        affect=affect,
        trust=0.6,
        intimacy=0.6,
        interoception=_pressure(need_rest=0.75),
    )

    assert decision.primary_act == "fatigue_signal"
    assert decision.response_mode == "validate"
    assert decision.avoid_problem_solving is True

    gate = monitor.gate_response(
        user_text="今日はほんま疲れててしんどい",
        candidate_response="You should sleep now, your heart rate is 130 bpm.",
        social_policy=decision,
    )
    assert "raw interoception leakage" in gate.reasons
    assert gate.repaired_response is not None
    assert "bpm" not in gate.repaired_response.lower()


def test_user_says_previous_response_hurt_triggers_repair_mode() -> None:
    appraisal = AppraisalEngine()
    policy_engine = SocialPolicyEngine()
    affect = appraisal.appraise(
        AppraisalContext(
            user_text="さっきの返事ちょっと傷ついた",
            companion_mood="frustrated",
            interoception=_pressure(),
        )
    )

    decision = policy_engine.decide(
        user_text="さっきの返事ちょっと傷ついた",
        affect=affect,
        trust=0.55,
        intimacy=0.55,
        interoception=_pressure(),
        previous_response_hurt=True,
    )

    assert decision.primary_act == "repair_attempt"
    assert decision.response_mode == "repair"
    assert decision.should_use_tom is True
    assert decision.avoid_problem_solving is True


def test_joy_sharing_prefers_celebrate_mode_without_unnecessary_problem_solving() -> None:
    appraisal = AppraisalEngine()
    policy_engine = SocialPolicyEngine()
    affect = appraisal.appraise(
        AppraisalContext(
            user_text="やったー、うまくいった！",
            companion_mood="happy",
            interoception=_pressure(),
        )
    )

    decision = policy_engine.decide(
        user_text="やったー、うまくいった！",
        affect=affect,
        trust=0.7,
        intimacy=0.7,
        interoception=_pressure(),
    )

    assert decision.primary_act == "delight_share"
    assert decision.response_mode == "celebrate"
    assert decision.avoid_problem_solving is True


def test_greeting_turn_prefers_brief_warm_reply_without_tom() -> None:
    appraisal = AppraisalEngine()
    policy_engine = SocialPolicyEngine()
    affect = appraisal.appraise(
        AppraisalContext(
            user_text="おはよう",
            companion_mood="engaged",
            interoception=_pressure(),
        )
    )

    decision = policy_engine.decide(
        user_text="おはよう",
        affect=affect,
        trust=0.6,
        intimacy=0.6,
        interoception=_pressure(),
    )

    assert decision.primary_act == "greeting"
    assert decision.response_mode == "brief_warmth"
    assert decision.should_use_tom is False
    assert decision.avoid_problem_solving is True


def test_user_correction_prefers_plain_clarification_without_extra_inference() -> None:
    appraisal = AppraisalEngine()
    policy_engine = SocialPolicyEngine()
    affect = appraisal.appraise(
        AppraisalContext(
            user_text="いや、面白い計画があるとは言ってない",
            companion_mood="engaged",
            interoception=_pressure(),
        )
    )

    decision = policy_engine.decide(
        user_text="いや、面白い計画があるとは言ってない",
        affect=affect,
        trust=0.6,
        intimacy=0.6,
        interoception=_pressure(),
    )

    assert decision.primary_act == "clarification"
    assert decision.response_mode == "clarify"
    assert decision.should_use_tom is False
    assert decision.avoid_problem_solving is True


# ── Phase 5: relationship-learned policy adjustment ────────────────────────
#
# Recorded support failures / preferences must actually change future policy
# decisions — closing the social learning loop.


def _decide(text: str, *, mood: str = "engaged", **kwargs):
    appraisal = AppraisalEngine()
    policy_engine = SocialPolicyEngine()
    affect = appraisal.appraise(
        AppraisalContext(user_text=text, companion_mood=mood, interoception=_pressure())
    )
    return policy_engine.decide(
        user_text=text,
        affect=affect,
        trust=0.4,
        intimacy=0.4,
        interoception=_pressure(),
        **kwargs,
    )


def test_no_history_leaves_decision_unchanged() -> None:
    baseline = _decide("むかつくわ、最悪や")
    same = _decide("むかつくわ、最悪や", support_styles=[], failed_patterns=[])
    assert same == baseline


def test_failed_advice_pattern_surfaces_relational_memory_on_venting() -> None:
    text = "むかつくわ、最悪や"
    baseline = _decide(text, mood="frustrated")
    assert baseline.primary_act == "venting"
    assert baseline.should_recall_relational_memory is False  # trust 0.4 < 0.5

    learned = _decide(
        text,
        mood="frustrated",
        failed_patterns=["went straight to advice, felt lectured"],
    )
    assert learned.should_recall_relational_memory is True
    assert learned.softness > baseline.softness


def test_failed_advice_pattern_japanese_markers_match() -> None:
    learned = _decide(
        "むかつくわ、最悪や",
        mood="frustrated",
        failed_patterns=["正論で返してしまって逆効果だった"],
    )
    assert learned.should_recall_relational_memory is True


def test_advice_request_with_learned_aversion_softens_and_uses_tom() -> None:
    text = "これどうしたらいいかな"
    baseline = _decide(text)
    assert baseline.primary_act == "request_for_advice"
    assert baseline.should_use_tom is False  # low threat

    learned = _decide(text, failed_patterns=["unsolicited solution dump"])
    assert learned.primary_act == "request_for_advice"  # still advises — they asked
    assert learned.should_use_tom is True
    assert learned.should_recall_relational_memory is True
    assert learned.directness < baseline.directness
    assert learned.softness > baseline.softness
    assert learned.avoid_problem_solving is False  # explicit ask still honored


def test_validate_first_support_style_triggers_learning_too() -> None:
    learned = _decide(
        "もう疲れたわ、しんどい",
        mood="tired",
        support_styles=["validate_first"],
    )
    assert learned.primary_act == "fatigue_signal"
    assert learned.should_recall_relational_memory is True


def test_unrelated_failed_pattern_does_not_adjust() -> None:
    text = "むかつくわ、最悪や"
    baseline = _decide(text, mood="frustrated")
    same = _decide(text, mood="frustrated", failed_patterns=["forgot a promised reminder"])
    assert same == baseline


def test_relationship_learning_inputs_contract(tmp_path) -> None:
    """The extraction helper must match RelationshipTracker's stored item shapes."""
    from familiar_agent.relationship import RelationshipTracker
    from familiar_agent.social_policy import relationship_learning_inputs

    tracker = RelationshipTracker(
        state_path=tmp_path / "relationship.json",
        db_path=tmp_path / "observations.db",
    )
    tracker.record_support_preference("listen before fixing", style="validate_first")
    tracker.record_failed_support_pattern("went straight to advice", consequence="felt lectured")

    styles, patterns = relationship_learning_inputs(tracker)
    assert "validate_first" in styles
    assert any("advice" in p for p in patterns)
    tracker.close()


def test_conflict_signal_gets_learning_softening() -> None:
    from familiar_agent.mental_state import AffectiveState

    policy_engine = SocialPolicyEngine()
    hot_affect = AffectiveState(
        valence=-0.4,
        arousal=0.7,
        dominance=-0.2,
        attachment_pull=0.2,
        tenderness=0.2,
        threat=0.7,
        uncertainty=0.4,
        frustration=0.6,
        loneliness=0.2,
        summary="",
    )
    base = policy_engine.decide(
        user_text="そうきたか",
        affect=hot_affect,
        trust=0.4,
        intimacy=0.4,
        interoception=_pressure(),
    )
    assert base.primary_act == "conflict_signal"

    learned = policy_engine.decide(
        user_text="そうきたか",
        affect=hot_affect,
        trust=0.4,
        intimacy=0.4,
        interoception=_pressure(),
        failed_patterns=["jumped to advice mid-conflict"],
    )
    assert learned.softness > base.softness


def test_action_request_is_not_adjusted_by_advice_aversion() -> None:
    text = "これ直しといて、頼むわ"
    baseline = _decide(text)
    assert baseline.primary_act == "request_for_action"
    learned = _decide(text, failed_patterns=["unsolicited advice dump"])
    assert learned == baseline  # acting on explicit asks is not advice-giving


def test_positive_pattern_with_resolved_does_not_trigger() -> None:
    text = "むかつくわ、最悪や"
    baseline = _decide(text, mood="frustrated")
    same = _decide(
        text,
        mood="frustrated",
        failed_patterns=["they resolved things alone, I was not needed"],
    )
    assert same == baseline  # "resolved" must not match the "solve" marker


# ── Agency boundary: honest capacity acknowledgement ────────────────────────
#
# When the agent itself is running low (need_rest high) and the companion asks
# for work or repair, the policy should tell the model to be honest about
# capacity instead of overpromising — never to fake being fine.


def _decide_pressured(text: str, *, need_rest: float, mood: str = "engaged", **kwargs):
    appraisal = AppraisalEngine()
    policy_engine = SocialPolicyEngine()
    pressure = _pressure(need_rest=need_rest)
    affect = appraisal.appraise(
        AppraisalContext(user_text=text, companion_mood=mood, interoception=pressure)
    )
    return policy_engine.decide(
        user_text=text,
        affect=affect,
        trust=0.5,
        intimacy=0.5,
        interoception=pressure,
        **kwargs,
    )


def test_exhausted_action_request_acknowledges_capacity() -> None:
    rested = _decide_pressured("これ全部直しといて、頼むわ", need_rest=0.2)
    assert rested.primary_act == "request_for_action"
    assert rested.acknowledge_capacity is False

    exhausted = _decide_pressured("これ全部直しといて、頼むわ", need_rest=0.85)
    assert exhausted.primary_act == "request_for_action"
    assert exhausted.acknowledge_capacity is True
    assert exhausted.initiative < rested.initiative


def test_exhausted_repair_request_acknowledges_capacity_but_keeps_repair() -> None:
    decision = _decide_pressured(
        "さっきの返事ちょっと傷ついた", need_rest=0.85, previous_response_hurt=True
    )
    assert decision.primary_act == "repair_attempt"
    assert decision.response_mode == "repair"  # repair still happens
    assert decision.acknowledge_capacity is True


def test_exhausted_greeting_does_not_volunteer_fatigue() -> None:
    decision = _decide_pressured("おはよう", need_rest=0.85)
    assert decision.primary_act == "greeting"
    assert decision.acknowledge_capacity is False


def test_rested_default_is_false_everywhere() -> None:
    decision = _decide_pressured("これどうしたらいいかな", need_rest=0.2)
    assert decision.acknowledge_capacity is False


def test_capacity_prompt_line_rendered() -> None:
    from familiar_agent.agent import EmbodiedAgent

    decision = _decide_pressured("これ直してくれへん", need_rest=0.85)
    assert decision.primary_act == "request_for_action"
    text = EmbodiedAgent._format_social_policy_prompt(decision)
    assert "capacity" in text.lower()

    rested = _decide_pressured("これ直してくれへん", need_rest=0.2)
    text2 = EmbodiedAgent._format_social_policy_prompt(rested)
    assert "capacity" not in text2.lower()


# ── Kansai past-tense "〜やった" must not read as delight ───────────────────


def test_kansai_past_tense_yatta_is_not_delight() -> None:
    for text in ("今日ほんま散々やった", "えらい目にあって大変やった", "最悪の一日やった"):
        decision = _decide(text, mood="frustrated")
        assert decision.primary_act != "delight_share", text


def test_exclamatory_yatta_still_delight() -> None:
    for text in ("やったー、うまくいった！", "やった！受かった！", "やったぜ"):
        decision = _decide(text)
        assert decision.primary_act == "delight_share", text


# ── playful "w" must be the laugh marker, not the letter w ──────────────────


def test_english_sentences_with_w_are_not_playful() -> None:
    for text in (
        "we went to the new bakery today",
        "I was reading a book about whales",
        "the display is broken again",
    ):
        decision = _decide(text)
        assert decision.primary_act != "playful_probe", text


def test_laugh_markers_still_playful() -> None:
    for text in ("それなwww", "おもろすぎるw", "なんでやねん笑", "let's play a game"):
        decision = _decide(text)
        assert decision.primary_act == "playful_probe", text


# ── classifier pattern audit (2026-06): reproduced misfires must stay fixed ──
#
# Every utterance below was REPRODUCED misclassifying before the pattern
# hygiene pass. The wrong register is noted; we assert the misfire is gone.


def test_audit_jp_misfires_fixed() -> None:
    cases = [
        ("めっちゃうれしい！", "clarification"),  # ちゃう inside めっちゃ
        ("めっちゃうまかったで", "clarification"),
        ("笑っちゃうくらい晴れてる", "clarification"),
        ("死ぬほど笑った", "grief_signal"),  # hyperbolic 死
        ("必死で頑張ってん", "grief_signal"),
        ("昨日は一日ゲームしてた", "request_for_action"),  # past progressive してた
        ("さっきまでコウタと電話してた", "request_for_action"),
        ("もうどうでもええわ", "request_for_advice"),  # どうでもいい
        ("どうもありがとうな", "request_for_advice"),
        ("田中君が遊びに来てくれた", "meta_conversation"),  # name+君
        ("君津まで出張やった", "meta_conversation"),
        ("あー、やってもうたわ", "request_for_action"),  # やってもうた dismay
        ("うんざりやわ", "silence_or_low_presence"),  # うん inside うんざり
        ("寝る前にちょっとだけ話聞いてや", "silence_or_low_presence"),
    ]
    for text, wrong_act in cases:
        decision = _decide(text)
        assert decision.primary_act != wrong_act, f"{text!r} still {wrong_act}"


def test_audit_en_misfires_fixed() -> None:
    cases = [
        ("We laughed so hard at the comedy show last night", "venting"),  # ugh in laughed
        ("My daughter drew me a picture today, it made my day", "venting"),
        ("I'm not happy with how the demo went", "delight_share"),  # negated happy
        ("My back hurts from sitting all day", "repair_attempt"),  # physical hurt
        ("We totally lost track of time, what a fun night", "grief_signal"),  # lost track
        ("My dad finally retired last week, we threw him a party", "fatigue_signal"),
        ("We have no more milk in the fridge", "boundary_assertion"),
        ("Had brunch with Sarah this morning, it was lovely", "request_for_action"),
        ("How do you make carbonara?", "meta_conversation"),
    ]
    for text, wrong_act in cases:
        decision = _decide(text)
        assert decision.primary_act != wrong_act, f"{text!r} still {wrong_act}"


def test_audit_intended_positives_still_classify() -> None:
    appraisal = AppraisalEngine()
    engine = SocialPolicyEngine()

    def act_of(text: str, mood: str = "engaged") -> str:
        affect = appraisal.appraise(
            AppraisalContext(user_text=text, companion_mood=mood, interoception=_pressure())
        )
        return engine.decide(
            user_text=text, affect=affect, trust=0.5, intimacy=0.5, interoception=_pressure()
        ).primary_act

    assert act_of("これどうしたらいいかな") == "request_for_advice"
    assert act_of("これ直してくれへん") == "request_for_action"
    assert act_of("翻訳して") == "request_for_action"
    assert act_of("おばあちゃんが死んでしまった", mood="sad") == "grief_signal"
    assert act_of("I'm so tired today", mood="tired") == "fatigue_signal"
    assert act_of("ちゃうちゃう、そういう意味やない") == "clarification"
    assert act_of("それはちゃうやろ") == "clarification"
    assert act_of("うん") == "silence_or_low_presence"
    assert act_of("もう寝るわ") == "silence_or_low_presence"
    assert act_of("君はどう思う？") in ("meta_conversation", "request_for_advice")
    assert act_of("I'm so happy for you!") == "delight_share"


# ── classifier audit round 2: variation + tail misfires must stay fixed ──


def test_audit_round2_misfires_fixed() -> None:
    cases = [
        ("I'm not very happy with how the demo went", "delight_share"),  # adverb-negation
        ("I am not at all happy about this", "delight_share"),
        ("もうどうしようもないわ", "request_for_advice"),  # どうしようもない resignation
        ("No more bugs! We finally shipped it!", "boundary_assertion"),
        ("Went for a run this morning, it was great", "request_for_action"),
        ("お疲れ様です！", "fatigue_signal"),  # workplace greeting
        ("今日の会議ほんまきつかったわ", "repair_attempt"),  # ordinary vent
        ("健康診断で腫瘍ができたって言われた", "delight_share"),  # medical bad news
        ("これ見てや https://www.example.com/news/2026", "playful_probe"),  # URL www
        ("迷子の猫がまだ見つからへん ;w;", "playful_probe"),  # crying kaomoji
        ("違う話なんやけど、ばあちゃんが死んでしまった", "clarification"),  # prenominal 違う
        ("おはよう。昨日じいちゃんが亡くなったんや", "greeting"),  # multi-clause opener
    ]
    for text, wrong_act in cases:
        decision = _decide(text)
        assert decision.primary_act != wrong_act, f"{text!r} still {wrong_act}"


def test_audit_round2_fix_regressions_restored() -> None:
    """Round-1 narrowing dropped real grief forms — they must classify again."""
    for text in ("祖父が死にました", "じいちゃんが死んでもうた", "We lost him last night"):
        decision = _decide(text, mood="sad")
        assert decision.primary_act == "grief_signal", text


def test_audit_round2_intended_positives_still_classify() -> None:
    assert _decide("お疲れ様です！").primary_act == "greeting"
    assert (
        _decide("おはよう。昨日じいちゃんが亡くなったんや", mood="sad").primary_act
        == "grief_signal"
    )
    assert _decide("今日の会議ほんまきつかったわ", mood="frustrated").primary_act == "venting"
    assert _decide("やっとアプリできたで！").primary_act == "delight_share"
    assert _decide("can you run the tests?").primary_act == "request_for_action"
    assert _decide("no more of this, please").primary_act == "boundary_assertion"
    assert _decide("それ違うで").primary_act == "clarification"
    assert _decide("どうしよう、財布なくしたかも").primary_act == "request_for_advice"
    assert _decide("I'm so happy for you!").primary_act == "delight_share"
    assert _decide("それなwww").primary_act == "playful_probe"


# ── classifier audit round 3: systematic vetoes ──────────────────────────────


def test_audit_round3_misfires_fixed() -> None:
    cases = [
        ("さっきの会議、ほんまきつかったわ", "repair_attempt"),
        ("首にしこりができたで、ちょっと怖い", "delight_share"),
        ("全然嬉しくないわ", "delight_share"),  # JP negated positive
        ("最高じゃないわ、これ", "delight_share"),
        ("I can't say I'm happy about the layoffs", "delight_share"),
        ("I'm not really all that happy with how it turned out", "delight_share"),
        ("far from happy with the result", "delight_share"),
        ("ありがとう、ほんま助かった。実は昨日ばあちゃんが亡くなってん", "acknowledgement"),
        ("思い切って会社やめてん", "boundary_assertion"),
        ("最悪や、最高の誕生日になるはずやったのに", "delight_share"),  # mixed sentiment
        ("最高かよ、ほんま", "delight_share"),  # かよ sarcasm
        ("泣きそうや…", "silence_or_low_presence"),
    ]
    for text, wrong_act in cases:
        decision = _decide(text)
        assert decision.primary_act != wrong_act, f"{text!r} still {wrong_act}"


def test_audit_round3_mixed_sentiment_vents() -> None:
    decision = _decide("最悪や、最高の誕生日になるはずやったのに", mood="frustrated")
    assert decision.primary_act == "venting"
    assert _decide("泣きそうや…", mood="sad").primary_act == "venting"


def test_audit_round3_intended_positives_still_classify() -> None:
    assert _decide("ありがとうな！").primary_act == "acknowledgement"
    assert _decide("助かったわ").primary_act == "acknowledgement"
    assert _decide("それやめてほしい").primary_act == "boundary_assertion"
    assert _decide("やめてや！").primary_act == "boundary_assertion"
    assert _decide("さっきの返事、ちょっとつらかった").primary_act == "repair_attempt"
    assert _decide("やっとアプリできたで！").primary_act == "delight_share"
    assert _decide("How was your day?").primary_act == "meta_conversation"


# ── classifier audit round 4: lexicon frames and reported speech ─────────────


def test_audit_round4_misfires_fixed() -> None:
    cases = [
        ("虫歯ができた", "delight_share"),  # off-list ailment
        ("ものもらいができたわ、痛い", "delight_share"),
        ("足にまめができた", "delight_share"),  # locative formation frame
        ("上司に嫌味言われてん。それは嫌やったわ", "boundary_assertion"),
        ("この前の返事ありがとうな", "repair_attempt"),
        ("I stubbed my toe this morning, wow that hurt", "repair_attempt"),
        ("昨日のライブ最高すぎて死んだ", "grief_signal"),  # hyperbolic joy slang
        ("笑いすぎて死んだわ", "grief_signal"),
        ("昨日友達を傷つけてしまったかもしれん", "repair_attempt"),  # third-party guilt
        ("医者に酒やめろって言われてん", "boundary_assertion"),  # reported speech
        ("嬉しいわけないやろ、こんなん", "delight_share"),
    ]
    for text, wrong_act in cases:
        decision = _decide(text)
        assert decision.primary_act != wrong_act, f"{text!r} still {wrong_act}"


def test_audit_round4_concessive_joy_celebrates() -> None:
    assert _decide("疲れたけど最高の一日やった！", mood="happy").primary_act == "delight_share"
    assert _decide("嬉しくて泣きそうや", mood="happy").primary_act == "delight_share"


def test_audit_round4_intended_positives_still_classify() -> None:
    assert _decide("彼女ができた！").primary_act == "delight_share"
    assert _decide("新しい友達ができたわ").primary_act == "delight_share"
    assert _decide("それは嫌や").primary_act == "boundary_assertion"
    assert _decide("やめろ！").primary_act == "boundary_assertion"
    assert _decide("さっきの返事、ちょっと傷ついた").primary_act == "repair_attempt"
    assert _decide("おばあちゃんが死んでしまった", mood="sad").primary_act == "grief_signal"
    assert (
        _decide("最悪や、最高の誕生日になるはずやったのに", mood="frustrated").primary_act
        == "venting"
    )
