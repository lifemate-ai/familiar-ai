"""Tests for the EmbodiedAgent ReAct loop (run() method)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from familiar_agent.backend import ToolCall, TurnResult
from familiar_agent.exploration import ExplorationTracker


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _turn(stop: str, text: str = "", tool_calls: list | None = None) -> TurnResult:
    return TurnResult(
        stop_reason=stop,
        text=text,
        tool_calls=tool_calls or [],
        input_tokens=100,
        output_tokens=50,
    )


def _make_agent(*, with_tts: bool = False, with_camera: bool = False, with_mcp: bool = False):
    """Minimal EmbodiedAgent with all heavy dependencies mocked out."""
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent.config = MagicMock()
    agent.config.max_tokens = 1000
    agent.config.agent_name = "Kokone"
    agent.config.companion_name = "Kouta"

    agent._turn_count = 0
    agent._session_input_tokens = 0
    agent._session_output_tokens = 0
    agent._last_context_tokens = 0
    agent._post_compact = False
    agent._started_at = 0.0
    agent.messages = []
    agent._me_md = ""

    # Backend: make_tool_results must accept (tool_calls, results) and return a list
    backend = MagicMock()
    backend.complete = AsyncMock(return_value="")
    backend.make_user_message = lambda t: {"role": "user", "content": t}
    backend.make_assistant_message = lambda result, raw: {
        "role": "assistant",
        "content": result.text,
    }
    backend.make_tool_results = MagicMock(return_value=[{"role": "tool", "content": "ok"}])
    agent.backend = backend
    agent._utility_backend = backend

    # Memory
    mem = MagicMock()
    mem.is_embedding_ready = MagicMock(return_value=True)
    mem.recall_async = AsyncMock(return_value=[])
    mem.recent_feelings_async = AsyncMock(return_value=[])
    mem.recall_self_model_async = AsyncMock(return_value=[])
    mem.recall_curiosities_async = AsyncMock(return_value=[])
    mem.recall_day_summaries_async = AsyncMock(return_value=[])
    mem.recall_semantic_facts_async = AsyncMock(return_value=[])
    mem.recall_behavior_policies_async = AsyncMock(return_value=[])
    mem.format_for_context = MagicMock(return_value="")
    mem.format_feelings_for_context = MagicMock(return_value="")
    mem.format_day_summaries_for_context = MagicMock(return_value="")
    mem.format_semantic_facts_for_context = MagicMock(return_value="")
    mem.format_behavior_policies_for_context = MagicMock(return_value="")
    mem.format_self_model_for_context = MagicMock(return_value="")
    mem.format_curiosities_for_context = MagicMock(return_value="")
    mem.save_async = AsyncMock()
    mem.get_dates_with_observations = MagicMock(return_value=[])
    mem.get_dates_with_summaries = MagicMock(return_value=[])
    mem.as_coalition_async = AsyncMock(return_value=None)
    agent._memory = mem

    mem_tool = MagicMock()
    mem_tool.get_tool_definitions = MagicMock(return_value=[])
    mem_tool.call = AsyncMock(return_value=("remembered", None))
    agent._memory_tool = mem_tool

    tom = MagicMock()
    tom.get_tool_definitions = MagicMock(return_value=[])
    tom.call = AsyncMock(return_value=("tom result", None))
    agent._tom_tool = tom

    coding = MagicMock()
    coding.get_tool_definitions = MagicMock(return_value=[])
    coding.call = AsyncMock(return_value=("code result", None))
    agent._coding = coding

    agent._camera = None
    agent._mobility = None
    agent._mcp = None

    if with_tts:
        tts_tool = MagicMock()
        tts_tool.get_tool_definitions = MagicMock(return_value=[{"name": "say"}])
        tts_tool.call = AsyncMock(return_value=("spoken", None))
        agent._tts = tts_tool
    else:
        agent._tts = None

    if with_camera:
        cam = MagicMock()
        cam.get_tool_definitions = MagicMock(return_value=[{"name": "see"}, {"name": "look"}])
        cam.call = AsyncMock(return_value=("I see a room", "base64img"))
        agent._camera = cam

    if with_mcp:
        mcp_client = MagicMock()
        mcp_client.get_tool_definitions = MagicMock(return_value=[])
        mcp_client.call = AsyncMock(return_value=("mcp result", None))
        mcp_client.is_started = True
        agent._mcp = mcp_client

    agent._exploration = ExplorationTracker()
    agent._scene = None

    from familiar_agent.self_narrative import SelfNarrative
    from familiar_agent.relationship import RelationshipTracker
    from familiar_agent.workspace import GlobalWorkspace
    from familiar_agent.prediction import PredictionEngine
    from familiar_agent.attention_schema import AttentionSchema
    import time as _time

    agent._self_narrative = SelfNarrative()
    agent._relationship = RelationshipTracker()
    agent._workspace = GlobalWorkspace()
    agent._prediction = PredictionEngine()
    agent._attention_schema = AttentionSchema()
    agent._dmn = MagicMock()
    agent._dmn.wander = AsyncMock(return_value=None)
    agent._meta_monitor = MagicMock()
    agent._meta_monitor.as_coalition = MagicMock(return_value=None)
    agent._meta_monitor.record_step = MagicMock()
    agent._memory_worker = MagicMock()
    agent._memory_worker.is_running = True
    agent._mood = "neutral"
    agent._mood_intensity = 0.0
    agent._mood_set_at = _time.time()

    return agent


# Patches that suppress heavy async sub-calls in run()
_HEAVY_PATCHES = {
    "familiar_agent.agent.EmbodiedAgent._morning_reconstruction": AsyncMock(return_value=""),
    "familiar_agent.agent.EmbodiedAgent._infer_companion_mood": AsyncMock(return_value="engaged"),
    "familiar_agent.agent.EmbodiedAgent._infer_emotion": AsyncMock(return_value="neutral"),
    "familiar_agent.agent.EmbodiedAgent._summarize_exchange": AsyncMock(return_value="summary"),
    "familiar_agent.agent.EmbodiedAgent._update_self_model": AsyncMock(),
    "familiar_agent.agent.EmbodiedAgent.extract_curiosity": AsyncMock(return_value=None),
    "familiar_agent.agent.generate_plan": AsyncMock(return_value=""),
    "familiar_agent.agent.check_plan_blocked": AsyncMock(return_value=False),
}


def _patch_heavy(extra: dict | None = None):
    """Apply all heavy patches; returns a list of patch objects (must be started/stopped by caller)."""
    patches = dict(_HEAVY_PATCHES)
    if extra:
        patches.update(extra)
    return [patch(target, new) for target, new in patches.items()]


# ---------------------------------------------------------------------------
# Tests: basic single-turn end_turn
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_end_turn_returns_text():
    """run() with immediate end_turn returns the model's text."""
    agent = _make_agent()
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="Hello!"), "Hello!"))

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run("こんにちは")
    finally:
        for p in ps:
            p.stop()

    assert result == "Hello!"


@pytest.mark.asyncio
async def test_run_increments_turn_count():
    """run() increments _turn_count on each invocation."""
    agent = _make_agent()
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="Hi"), "Hi"))

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        assert agent._turn_count == 0
        await agent.run("test")
        assert agent._turn_count == 1
        await agent.run("test2")
        assert agent._turn_count == 2
    finally:
        for p in ps:
            p.stop()


@pytest.mark.asyncio
async def test_run_appends_user_message_to_history():
    """run() appends the user message to agent.messages."""
    agent = _make_agent()
    agent.backend.stream_turn = AsyncMock(
        return_value=(_turn("end_turn", text="response"), "response")
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        assert len(agent.messages) == 0
        await agent.run("hello from user")
        # At minimum, a user message was added
        assert any(m.get("role") == "user" for m in agent.messages)
    finally:
        for p in ps:
            p.stop()


@pytest.mark.asyncio
async def test_run_accumulates_tokens():
    """run() adds input/output tokens to session totals."""
    agent = _make_agent()
    agent.backend.stream_turn = AsyncMock(
        return_value=(
            _turn(
                "end_turn",
                text="ok",
            ),
            "ok",
        )
    )
    # Override to set token counts
    result_obj = TurnResult(stop_reason="end_turn", text="ok", input_tokens=200, output_tokens=80)
    agent.backend.stream_turn = AsyncMock(return_value=(result_obj, "ok"))

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("test")
    finally:
        for p in ps:
            p.stop()

    assert agent._session_input_tokens == 200
    assert agent._session_output_tokens == 80


# ---------------------------------------------------------------------------
# Tests: tool_use → end_turn sequence
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_tool_use_then_end_turn():
    """run() executes a tool call then gets end_turn on the next iteration."""
    agent = _make_agent()

    tc = ToolCall(id="tc1", name="remember", input={"content": "test memory"})
    turn1 = TurnResult(stop_reason="tool_use", text="", tool_calls=[tc])
    turn2 = TurnResult(stop_reason="end_turn", text="Done!", tool_calls=[])

    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (turn1, None),
            (turn2, "Done!"),
        ]
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run("remember something")
    finally:
        for p in ps:
            p.stop()

    assert result == "Done!"
    assert agent._memory_tool.call.called


@pytest.mark.asyncio
async def test_run_tool_results_added_to_messages():
    """Tool results are added to message history after tool execution."""
    agent = _make_agent()

    tc = ToolCall(id="tc1", name="remember", input={"content": "hi"})
    turn1 = TurnResult(stop_reason="tool_use", text="", tool_calls=[tc])
    turn2 = TurnResult(stop_reason="end_turn", text="Saved.", tool_calls=[])

    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (turn1, None),
            (turn2, "Saved."),
        ]
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("please remember")
    finally:
        for p in ps:
            p.stop()

    # make_tool_results was called with the tool call and its result
    assert agent.backend.make_tool_results.called


@pytest.mark.asyncio
async def test_run_passes_latest_pre_see_action_into_scene_update():
    """The last embodied action before see() conditions the scene update."""
    agent = _make_agent(with_camera=True)
    agent._scene = MagicMock()
    agent._scene.update = AsyncMock(return_value=[])
    agent._scene.context_for_prompt = MagicMock(return_value="")
    agent._scene_backend = MagicMock()
    agent._camera.call = AsyncMock(
        side_effect=[
            ("looked left", None),
            ("I see a room", "base64img"),
        ]
    )

    turn1 = TurnResult(
        stop_reason="tool_use",
        text="",
        tool_calls=[
            ToolCall(id="tc1", name="look", input={"direction": "left", "degrees": 45}),
            ToolCall(id="tc2", name="see", input={}),
        ],
    )
    turn2 = TurnResult(stop_reason="end_turn", text="There is a window.", tool_calls=[])
    agent.backend.stream_turn = AsyncMock(
        side_effect=[(turn1, None), (turn2, "There is a window.")]
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("look and report")
    finally:
        for p in ps:
            p.stop()

    agent._scene.update.assert_awaited_once()
    _, kwargs = agent._scene.update.call_args
    assert kwargs["action_name"] == "look"
    assert kwargs["action_input"] == {"direction": "left", "degrees": 45}


# ---------------------------------------------------------------------------
# Tests: auto-say
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_auto_say_fires_when_tts_available_and_no_say_call():
    """When TTS is present and model wrote text without calling say(), auto-say fires."""
    agent = _make_agent(with_tts=True)
    agent.backend.stream_turn = AsyncMock(
        return_value=(_turn("end_turn", text="Hello, I speak!"), "Hello, I speak!")
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("speak to me")
    finally:
        for p in ps:
            p.stop()

    agent._tts.call.assert_awaited_once()
    call_args = agent._tts.call.call_args
    assert call_args[0][0] == "say"


@pytest.mark.asyncio
async def test_run_no_auto_say_when_tts_absent():
    """Without TTS, no auto-say even if model wrote text."""
    agent = _make_agent(with_tts=False)
    agent.backend.stream_turn = AsyncMock(
        return_value=(_turn("end_turn", text="Silent response"), "Silent response")
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("respond")
    finally:
        for p in ps:
            p.stop()

    assert agent._tts is None


@pytest.mark.asyncio
async def test_run_no_auto_say_when_say_already_called():
    """If say() was called as a tool, auto-say should NOT fire again."""
    agent = _make_agent(with_tts=True)

    tc = ToolCall(id="tc1", name="say", input={"text": "I spoke"})
    turn1 = TurnResult(stop_reason="tool_use", text="", tool_calls=[tc])
    turn2 = TurnResult(stop_reason="end_turn", text="done", tool_calls=[])

    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (turn1, None),
            (turn2, "done"),
        ]
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("speak via tool")
    finally:
        for p in ps:
            p.stop()

    # say() was called once via tool execution; auto-say must NOT add a second call
    assert agent._tts.call.call_count == 1


# ---------------------------------------------------------------------------
# Tests: morning reconstruction on first turn
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_first_turn_calls_morning_reconstruction():
    """On the very first turn, _morning_reconstruction is invoked."""
    agent = _make_agent()
    agent.backend.stream_turn = AsyncMock(
        return_value=(_turn("end_turn", text="Good morning"), "Good morning")
    )

    morning_mock = AsyncMock(return_value="morning context")
    patches = dict(_HEAVY_PATCHES)
    patches["familiar_agent.agent.EmbodiedAgent._morning_reconstruction"] = morning_mock

    ps = [patch(t, n) for t, n in patches.items()]
    for p in ps:
        p.start()
    try:
        await agent.run("hello")
    finally:
        for p in ps:
            p.stop()

    morning_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_subsequent_turns_skip_morning_reconstruction():
    """_morning_reconstruction is NOT called on turns after the first."""
    agent = _make_agent()
    agent._turn_count = 5  # simulate subsequent turn
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="reply"), "reply"))

    morning_mock = AsyncMock(return_value="")
    patches = dict(_HEAVY_PATCHES)
    patches["familiar_agent.agent.EmbodiedAgent._morning_reconstruction"] = morning_mock

    ps = [patch(t, n) for t, n in patches.items()]
    for p in ps:
        p.start()
    try:
        await agent.run("follow up")
    finally:
        for p in ps:
            p.stop()

    morning_mock.assert_not_awaited()


# ---------------------------------------------------------------------------
# Tests: empty / edge cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_empty_text_returns_no_response_placeholder():
    """When model returns no text, run() returns the placeholder string."""
    agent = _make_agent()
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text=""), ""))

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run("hi")
    finally:
        for p in ps:
            p.stop()

    assert result == "(no response)"
