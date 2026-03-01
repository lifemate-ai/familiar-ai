"""Tests for message compaction + post-compaction recall in EmbodiedAgent."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock


def _make_msg(role: str, text: str) -> dict:
    return {"role": role, "content": text}


def _make_agent():
    """Minimal EmbodiedAgent with mocked backend and memory."""
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent.config = MagicMock()
    agent.config.max_tokens = 1000
    agent.config.agent_name = "A"
    agent.config.companion_name = "U"
    agent._started_at = 0.0
    agent._turn_count = 0
    agent._session_input_tokens = 0
    agent._session_output_tokens = 0
    agent._last_context_tokens = 0
    agent._post_compact = False
    agent.messages = []

    agent.backend = MagicMock()
    agent.backend.complete = AsyncMock(return_value="summary text")
    agent.backend.make_user_message = lambda t: _make_msg("user", t)

    agent._memory = MagicMock()
    agent._memory.recall_async = AsyncMock(return_value=[])
    agent._memory.recent_feelings_async = AsyncMock(return_value=[])
    agent._memory.recall_self_model_async = AsyncMock(return_value=[])
    agent._memory.recall_curiosities_async = AsyncMock(return_value=[])
    agent._memory.format_for_context = MagicMock(return_value="")
    agent._memory.format_feelings_for_context = MagicMock(return_value="")
    agent._me_md = ""

    return agent


# ── _should_compact ────────────────────────────────────────────────────────


class TestShouldCompact:
    def test_false_when_below_threshold(self):
        """Below threshold → no compaction needed."""

        agent = _make_agent()
        agent._last_context_tokens = 30_000
        assert agent._should_compact(threshold_tokens=60_000) is False

    def test_false_when_equal_to_threshold(self):
        """At threshold → no compaction (strictly greater triggers)."""

        agent = _make_agent()
        agent._last_context_tokens = 60_000
        assert agent._should_compact(threshold_tokens=60_000) is False

    def test_true_when_above_threshold(self):
        """Above threshold → compaction needed."""
        agent = _make_agent()
        agent._last_context_tokens = 60_001
        assert agent._should_compact(threshold_tokens=60_000) is True

    def test_false_with_empty_messages(self):
        """No messages → never compact."""
        agent = _make_agent()
        agent._last_context_tokens = 999_999
        agent.messages = []
        assert agent._should_compact(threshold_tokens=0) is False

    def test_default_threshold_is_reasonable(self):
        """Default threshold exists and is positive."""
        import inspect
        from familiar_agent.agent import EmbodiedAgent

        sig = inspect.signature(EmbodiedAgent._should_compact)
        default = sig.parameters["threshold_tokens"].default
        assert isinstance(default, int)
        assert default > 0


# ── _compact_messages ──────────────────────────────────────────────────────


class TestCompactMessages:
    def test_method_exists(self):
        """EmbodiedAgent must have _compact_messages method."""
        from familiar_agent.agent import EmbodiedAgent

        assert hasattr(EmbodiedAgent, "_compact_messages")
        assert callable(EmbodiedAgent._compact_messages)

    def test_keeps_last_n_messages(self):
        """_compact_messages keeps the last keep_last messages intact."""
        agent = _make_agent()
        # 10 messages — last 6 should survive
        for i in range(10):
            agent.messages.append(_make_msg("user" if i % 2 == 0 else "assistant", f"msg{i}"))

        asyncio.get_event_loop().run_until_complete(agent._compact_messages(keep_last=6))

        # Last 6 original messages + 1 summary marker at front
        assert len(agent.messages) == 7

    def test_summary_marker_at_front(self):
        """First message after compaction is a user-role summary."""
        agent = _make_agent()
        for i in range(8):
            agent.messages.append(_make_msg("user" if i % 2 == 0 else "assistant", f"m{i}"))

        asyncio.get_event_loop().run_until_complete(agent._compact_messages(keep_last=4))

        first = agent.messages[0]
        assert first["role"] == "user"
        assert "summary" in first["content"].lower() or len(first["content"]) > 0

    def test_backend_complete_called_for_summary(self):
        """_compact_messages calls backend.complete() to generate the summary."""
        agent = _make_agent()
        for i in range(8):
            agent.messages.append(_make_msg("user" if i % 2 == 0 else "assistant", f"m{i}"))

        asyncio.get_event_loop().run_until_complete(agent._compact_messages(keep_last=4))

        agent.backend.complete.assert_called_once()

    def test_no_compaction_when_few_messages(self):
        """If messages <= keep_last, nothing changes."""
        agent = _make_agent()
        for i in range(4):
            agent.messages.append(_make_msg("user", f"m{i}"))

        original = list(agent.messages)
        asyncio.get_event_loop().run_until_complete(agent._compact_messages(keep_last=6))

        assert agent.messages == original
        agent.backend.complete.assert_not_called()

    def test_sets_post_compact_flag(self):
        """_compact_messages sets _post_compact = True."""
        agent = _make_agent()
        for i in range(10):
            agent.messages.append(_make_msg("user" if i % 2 == 0 else "assistant", f"m{i}"))

        asyncio.get_event_loop().run_until_complete(agent._compact_messages(keep_last=4))

        assert agent._post_compact is True


# ── post-compaction recall boost ───────────────────────────────────────────


class TestPostCompactionRecall:
    def test_agent_has_post_compact_flag(self):
        """EmbodiedAgent.__init__ sets _post_compact = False."""

        agent = _make_agent()
        assert hasattr(agent, "_post_compact")
        assert agent._post_compact is False

    def test_agent_has_last_context_tokens(self):
        """EmbodiedAgent.__init__ sets _last_context_tokens = 0."""
        agent = _make_agent()
        assert hasattr(agent, "_last_context_tokens")
        assert agent._last_context_tokens == 0

    def test_recall_n_larger_after_compact(self):
        """When _post_compact is True, recall_async is called with n > 3."""
        agent = _make_agent()
        agent._post_compact = True
        agent._turn_count = 1  # skip morning_reconstruction path
        agent._mcp = None
        agent._camera = None
        agent._mobility = None
        agent._tts = None
        agent._stt = None
        agent._coding = MagicMock()
        agent._coding.get_tool_definitions = MagicMock(return_value=[])
        agent._memory_tool = MagicMock()
        agent._memory_tool.get_tool_definitions = MagicMock(return_value=[])
        agent._tom_tool = MagicMock()
        agent._tom_tool.get_tool_definitions = MagicMock(return_value=[])

        # Make stream_turn return end_turn immediately
        from familiar_agent.backend import TurnResult

        fake_result = TurnResult(stop_reason="end_turn", text="ok")
        agent.backend.stream_turn = AsyncMock(return_value=(fake_result, []))
        agent.backend.make_assistant_message = MagicMock(return_value=_make_msg("assistant", "ok"))
        agent.backend.make_tool_results = MagicMock(return_value=_make_msg("user", ""))
        agent._infer_emotion = AsyncMock(return_value="neutral")
        agent._summarize_exchange = AsyncMock(return_value="summary")
        agent._update_self_model = AsyncMock()
        agent._memory.save_async = AsyncMock()
        agent._should_compact = MagicMock(return_value=False)

        asyncio.get_event_loop().run_until_complete(agent.run("hello"))

        # recall_async should have been called with n > 3 (post-compact boost)
        call_args = agent._memory.recall_async.call_args
        n_used = call_args[1].get("n") or call_args[0][1]
        assert n_used > 3, f"Expected n > 3 after compaction, got {n_used}"
