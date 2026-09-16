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


@pytest.mark.asyncio
async def test_agent_withholds_camera_tools_on_social_turn() -> None:
    """With social reflex on, a venting utterance must not offer see/look to the model."""
    from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

    from familiar_agent.agent import EmbodiedAgent
    from familiar_agent.backend import TurnResult

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent.config = MagicMock(max_tokens=100, auto_say=False)
    agent._turn_count = 5
    agent._session_input_tokens = agent._session_output_tokens = agent._last_context_tokens = 0
    agent._post_compact = False
    agent._background_tasks = set()
    agent._cached_plan_ctx = agent._cached_workspace_ctx = ""
    agent._cached_temporal_ctx = None
    agent._cached_companion_mood = "engaged"
    agent._started_at = 0.0
    agent.messages = []
    agent._me_md = ""
    agent._social_reflex = True
    agent._prompt_profile = "compact"
    agent._camera = agent._mobility = agent._tts = agent._scene = agent._mcp = None
    agent._memory_worker = None
    agent._self_state = None
    agent._relationship = MagicMock(context_for_prompt=MagicMock(return_value=""))
    agent._exploration = MagicMock(context_for_prompt=MagicMock(return_value=""))
    agent._concerns = agent._prediction = None
    agent._attention_schema = MagicMock(current_focus=MagicMock(return_value=None))
    agent._mood, agent._mood_intensity, agent._mood_set_at = "neutral", 0.0, 0.0
    tool_defs = [{"name": n} for n in ("say", "see", "look", "remember")]
    agent._tape_backend = lambda: None
    agent._spawn_background_task = MagicMock()
    agent._should_compact = lambda: False

    mem = MagicMock()
    mem.is_embedding_ready = MagicMock(return_value=True)
    for name in (
        "recall_async",
        "recent_feelings_async",
        "recall_semantic_facts_async",
        "recall_behavior_policies_async",
    ):
        setattr(mem, name, AsyncMock(return_value=[]))
    agent._memory = mem

    seen_tools: list[list[str]] = []

    async def fake_stream_turn(system, messages, tools, max_tokens, on_text=None):
        seen_tools.append([t["name"] for t in tools])
        return TurnResult("end_turn", "お疲れさん。<tool_code>{}</tool_code>", []), {
            "role": "assistant",
            "content": "x",
        }

    backend = MagicMock()
    backend.stream_turn = fake_stream_turn
    backend.make_user_message = lambda t: {"role": "user", "content": t}
    backend.make_assistant_message = lambda r, raw: raw
    agent.backend = backend

    with patch.object(EmbodiedAgent, "_all_tool_defs", new_callable=PropertyMock) as defs:
        defs.return_value = tool_defs
        out = await agent.run("今日ほんま疲れた…")
        assert seen_tools == [["say", "remember"]]
        assert out == "お疲れさん。"

        seen_tools.clear()
        await agent.run("見て見て、これ買ったやつ！")
        assert seen_tools == [["say", "see", "look", "remember"]]


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
