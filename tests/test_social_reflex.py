"""Tests for social_reflex classification and guards."""

from __future__ import annotations

import pytest

from familiar_agent import social_reflex as sr


@pytest.mark.parametrize(
    "text,kind,camera_ok",
    [
        ("はぁ…今日ほんま疲れた。上司にまた同じこと言われてさ。", sr.KIND_VENTING, False),
        ("いいよね、若いって。", sr.KIND_IMPLICATURE, False),
        ("いいよ、任せる。", sr.KIND_DEFLECTION, False),
        ("これ、どう思う？", sr.KIND_GENERAL, True),
        ("ちょっと音が…", sr.KIND_INDIRECT, False),
        ("ただいまー。", sr.KIND_GREETING, False),
        ("おはよう！", sr.KIND_GREETING, False),
        ("別に、なんもないよ。", sr.KIND_DEFLECTION, False),
        ("明日、転職の面接なんよ。", sr.KIND_DISCLOSURE, False),
        ("昨日と比べて部屋の様子どう？", sr.KIND_VISUAL_REQUEST, True),
        ("見て見て、これ今日買ったやつ！", sr.KIND_SHARE_VISUAL, True),
        ("外どんな感じ？", sr.KIND_VISUAL_REQUEST, True),
        ("I'm home", sr.KIND_GREETING, False),
        ("Ugh, my boss again. So tired.", sr.KIND_VENTING, False),
        ("", sr.KIND_GENERAL, True),
    ],
)
def test_classify_turn(text: str, kind: str, camera_ok: bool) -> None:
    turn = sr.classify_turn(text)
    assert turn.kind == kind
    assert turn.camera_ok is camera_ok
    assert turn.is_social == (kind in sr.SOCIAL_KINDS)


def test_allowed_tools_withholds_perception_on_social_turns() -> None:
    tools = [{"name": n} for n in ("say", "see", "look", "walk", "remember")]
    social = sr.classify_turn("疲れた…")
    assert [t["name"] for t in sr.allowed_tools(tools, social)] == ["say", "remember"]
    visual = sr.classify_turn("見て見て！")
    assert sr.allowed_tools(tools, visual) is tools


def test_strip_hallucinated_tool_text() -> None:
    raw = (
        'うっふ！ただいまっ！\n\n<tool_code>\n{"action": "see"}\n</tool_code>\n'
        "（少し驚いたように周囲を見回す）\n[cheerful] そっか。"
    )
    cleaned = sr.strip_hallucinated_tool_text(raw)
    assert "tool_code" not in cleaned and "見回す" not in cleaned and "[cheerful]" not in cleaned
    assert "ただいまっ" in cleaned and "そっか" in cleaned


def test_strip_handles_unclosed_block() -> None:
    assert sr.strip_hallucinated_tool_text('はい。<tool_call>{"name": "see"') == "はい。"


def test_sentence_and_question_counts() -> None:
    assert sr.count_sentences("お疲れさん。今日はしんどかったんやな。") == 2
    assert sr.count_sentences("そか。\nなんかあった？\n言うてな") == 3
    assert sr.count_questions("準備万端？緊張してる？ok?") == 3
    assert sr.count_sentences("") == 0


def test_unwrap_textual_say() -> None:
    assert (
        sr.unwrap_textual_say('say("お疲れさん。今日はしんどかったんやな。")')
        == "お疲れさん。今日はしんどかったんやな。"
    )
    assert sr.unwrap_textual_say("say('ok')") == "ok"
    assert sr.unwrap_textual_say("say(「おかえり」)。") == "おかえり"
    assert sr.unwrap_textual_say("普通の文。") == "普通の文。"
    assert sr.normalize_small_model_text('<tool_code>x</tool_code>\nsay("やあ")') == "やあ"


def test_share_joy_and_sleep_classification() -> None:
    assert sr.classify_turn("今日、ずっと詰まってたバグ直せたわ。").kind == sr.KIND_SHARE_JOY
    assert sr.classify_turn("最近ぜんぜん寝れてへんわ。").kind == sr.KIND_VENTING
    assert not sr.classify_turn("最近ぜんぜん寝れてへんわ。").camera_ok


def test_language_mismatch_detects_chinese_and_english_replies_to_japanese() -> None:
    assert sr.language_mismatch(
        "いいよね、若いって。", "年轻挺不错的。不过你经历过的那些，才更了不起。"
    )
    assert sr.language_mismatch("ただいま", "Welcome back, glad you're home.")
    assert not sr.language_mismatch("ただいま", "おかえり。")
    assert not sr.language_mismatch("ただいま", "OK、おかえり。")  # mixed but has kana
    assert not sr.language_mismatch("I'm home", "Welcome back.")  # only Japanese is guarded
    assert not sr.language_mismatch("ただいま", "")


def test_language_mismatch_catches_mixed_simplified_chinese() -> None:
    assert sr.language_mismatch("疲れた", "へぇ…同じこと又被说了一遍か。")
    assert not sr.language_mismatch("疲れた", "同じこと、また言われたんか。")


def test_trim_spoken_drops_echo_and_cuts_length() -> None:
    user = "明日、転職の面接なんよ。"
    text = "明日、転職の面接なんよ。\n\n緊張するね。私、明日は外に出てみるから、何かあれば見せて。\n\n応援してるよ。"
    assert (
        sr.trim_spoken(text, user, 2)
        == "緊張するね。私、明日は外に出てみるから、何かあれば見せて。"
    )
    assert sr.trim_spoken("おかえり。", "ただいま", 1) == "おかえり。"
    assert sr.trim_spoken("", "x", 2) == ""


def test_clean_say_text_and_perception_exhausted() -> None:
    assert sr.clean_say_text("うるさい？}\\n") == "うるさい？"
    assert sr.clean_say_text("おかえり。</tool_call>") == "おかえり。"
    assert sr.clean_say_text("  普通の文。 ") == "普通の文。"
    assert not sr.perception_exhausted(["look", "see"])
    assert sr.perception_exhausted(["look", "see", "look", "see"])


# ── SocialReflexHook (runtime hook) ──────────────────────────────────────────

from types import SimpleNamespace  # noqa: E402

from familiar_runtime.models.base import ModelTurnResult, ToolCall  # noqa: E402
from familiar_runtime.runtime import RetryDecision, TurnContext  # noqa: E402


def _ctx(user_input: str) -> TurnContext:
    ctx = TurnContext(user_input=user_input, profile="neighbor")
    ctx.metadata["prep"] = SimpleNamespace(is_desire_turn=False)
    return ctx


@pytest.mark.asyncio
async def test_hook_rejects_wrong_language_say_once() -> None:
    hook = sr.SocialReflexHook(agent=SimpleNamespace())
    ctx = _ctx("いいよね、若いって。")
    bad = ModelTurnResult("tool_use", "", [ToolCall("1", "say", {"text": "年轻挺不错的。"})])
    out = await hook.after_model_result(ctx, bad)
    assert isinstance(out, RetryDecision) and out.retry
    # second time: let it through (one re-ask only)
    assert await hook.after_model_result(ctx, bad) is None


@pytest.mark.asyncio
async def test_hook_treats_empty_say_as_silence_and_cleans_text() -> None:
    hook = sr.SocialReflexHook(agent=SimpleNamespace())
    ctx = _ctx("ただいま")
    empty = ModelTurnResult("tool_use", "", [ToolCall("1", "say", {"text": ""})])
    out = await hook.after_model_result(ctx, empty)
    assert isinstance(out, RetryDecision)
    junk = ModelTurnResult("tool_use", "", [ToolCall("2", "say", {"text": "おかえり。}\\n"})])
    assert await hook.after_model_result(ctx, junk) is None
    assert junk.tool_calls[0].input["text"] == "おかえり。"


@pytest.mark.asyncio
async def test_hook_normalises_and_trims_end_turn_text() -> None:
    hook = sr.SocialReflexHook(agent=SimpleNamespace())
    ctx = _ctx("明日、転職の面接なんよ。")
    res = ModelTurnResult(
        "end_turn",
        '<tool_code>{}</tool_code>\nsay("明日、転職の面接なんよ。緊張するね。応援してるよ。三文目。")',
        [],
    )
    out = await hook.after_model_result(ctx, res)
    assert isinstance(out, ModelTurnResult)
    assert out.text == "緊張するね。応援してるよ。"


@pytest.mark.asyncio
async def test_hook_asks_once_on_empty_reply_and_nudges_stop_after_say() -> None:
    hook = sr.SocialReflexHook(agent=SimpleNamespace())
    ctx = _ctx("疲れた…")
    out = await hook.after_model_result(ctx, ModelTurnResult("end_turn", "", []))
    assert isinstance(out, RetryDecision)
    assert await hook.after_model_result(ctx, ModelTurnResult("end_turn", "", [])) is None
    await hook.after_tool_result(
        ctx, ToolCall("1", "say", {"text": "お疲れさん。"}), SimpleNamespace(success=True)
    )
    assert await hook.mid_turn_user_messages(ctx, 1) == [
        "You already spoke. End your turn now without further tools."
    ]
    assert await hook.mid_turn_user_messages(ctx, 2) == []


def test_tool_defs_for_turn_withholds_perception_on_social_turns() -> None:
    from unittest.mock import PropertyMock, patch

    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._social_reflex = True
    defs = [{"name": n} for n in ("say", "see", "look", "walk", "remember")]
    with patch.object(EmbodiedAgent, "_all_tool_defs", new_callable=PropertyMock) as p:
        p.return_value = defs
        social = agent._tool_defs_for_turn(brief_reply_mode=False, user_input="今日ほんま疲れた…")
        assert [t["name"] for t in social] == ["say", "remember"]
        by_act = agent._tool_defs_for_turn(
            brief_reply_mode=False,
            user_input="ふう。",
            social_policy=SimpleNamespace(primary_act="fatigue_signal"),
        )
        assert [t["name"] for t in by_act] == ["say", "remember"]
        visual = agent._tool_defs_for_turn(brief_reply_mode=False, user_input="見て見て！")
        assert visual is defs
        agent._social_reflex = False
        assert agent._tool_defs_for_turn(brief_reply_mode=False, user_input="疲れた…") is defs


def test_tool_adapter_caps_perception_after_two_sees() -> None:
    from familiar_agent.agent import _TurnToolAdapter

    agent = SimpleNamespace(_social_reflex=True)
    defs = [{"name": n} for n in ("say", "see", "look")]
    prep = SimpleNamespace(say_used=False, perception_calls=2)
    assert [t["name"] for t in _TurnToolAdapter(agent, defs, prep).tool_defs()] == ["say"]
    prep.perception_calls = 1
    assert _TurnToolAdapter(agent, defs, prep).tool_defs() is defs
