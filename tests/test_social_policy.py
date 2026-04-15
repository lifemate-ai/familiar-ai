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
