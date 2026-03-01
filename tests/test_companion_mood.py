"""Tests for companion mood classifier and interoception companion field.

Feature: _infer_companion_mood() classifies the companion's emotional state
from their message text, and injects it into _interoception() as a felt quality.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock

import pytest


# ── Tests for _interoception() companion field ────────────────────────────────


class TestInteroceptionCompanionField:
    """_interoception() includes a companion field when mood is provided."""

    def _call_interoception(self, companion_mood: str) -> str:
        from familiar_agent.agent import _interoception

        return _interoception(started_at=time.time(), turn_count=1, companion_mood=companion_mood)

    def test_contains_companion_field(self):
        result = self._call_interoception("engaged")
        assert "companion" in result

    def test_engaged_mood(self):
        result = self._call_interoception("engaged")
        assert (
            "here with me" in result.lower()
            or "engaged" in result.lower()
            or "here" in result.lower()
        )

    def test_tired_mood(self):
        result = self._call_interoception("tired")
        assert "tired" in result.lower()

    def test_frustrated_mood(self):
        result = self._call_interoception("frustrated")
        assert "frustrated" in result.lower() or "bothering" in result.lower()

    def test_absent_mood(self):
        result = self._call_interoception("absent")
        assert "quiet" in result.lower() or "absent" in result.lower() or "here" in result.lower()

    def test_happy_mood(self):
        result = self._call_interoception("happy")
        assert "happy" in result.lower() or "good mood" in result.lower()

    def test_default_mood_engaged(self):
        """No companion_mood argument → defaults to engaged."""
        from familiar_agent.agent import _interoception

        result = _interoception(started_at=time.time(), turn_count=1)
        assert "companion" in result

    def test_result_is_sexpr_format(self):
        """Result is in S-expression format used by the rest of interoception."""
        result = self._call_interoception("happy")
        assert result.startswith("(interoception")
        assert ":private true" in result
        assert "(companion" in result


# ── Tests for _infer_companion_mood() ────────────────────────────────────────


class TestInferCompanionMood:
    """_infer_companion_mood() returns a valid mood label from LLM backend."""

    def _make_agent_with_mock_backend(self, complete_return: str):
        """Create an EmbodiedAgent with a mock backend that returns complete_return."""
        from familiar_agent.agent import EmbodiedAgent
        from familiar_agent.config import AgentConfig

        config = AgentConfig.__new__(AgentConfig)
        config.camera = MagicMock()
        config.camera.host = None
        config.mobility = MagicMock()
        config.mobility.api_key = None
        config.tts = MagicMock()
        config.tts.elevenlabs_api_key = None
        config.stt = MagicMock()
        config.stt.elevenlabs_api_key = None
        config.coding = MagicMock()
        config.coding.enabled = False
        config.max_tokens = 1024
        config.companion_name = "Kouta"

        agent = EmbodiedAgent.__new__(EmbodiedAgent)
        agent.config = config
        agent.messages = []
        agent._started_at = time.time()
        agent._turn_count = 0
        agent._me_md = ""
        agent._camera = None
        agent._mobility = None
        agent._tts = None
        agent._stt = None
        agent._mcp = None
        agent._session_input_tokens = 0
        agent._session_output_tokens = 0
        agent._last_context_tokens = 0
        agent._post_compact = False

        from familiar_agent.tools.memory import ObservationMemory, MemoryTool
        from familiar_agent.tools.tom import ToMTool
        from familiar_agent.tools.coding import CodingTool

        agent._memory = MagicMock(spec=ObservationMemory)
        agent._memory_tool = MagicMock(spec=MemoryTool)
        agent._tom_tool = MagicMock(spec=ToMTool)
        agent._coding = MagicMock(spec=CodingTool)

        from familiar_agent.exploration import ExplorationTracker

        agent._exploration = ExplorationTracker()

        mock_backend = MagicMock()
        mock_backend.complete = AsyncMock(return_value=complete_return)
        agent.backend = mock_backend

        return agent

    @pytest.mark.asyncio
    async def test_returns_engaged(self):
        agent = self._make_agent_with_mock_backend("engaged")
        result = await agent._infer_companion_mood("Let's work on this together!")
        assert result == "engaged"

    @pytest.mark.asyncio
    async def test_returns_tired(self):
        agent = self._make_agent_with_mock_backend("tired")
        result = await agent._infer_companion_mood("I'm so tired today...")
        assert result == "tired"

    @pytest.mark.asyncio
    async def test_returns_frustrated(self):
        agent = self._make_agent_with_mock_backend("frustrated")
        result = await agent._infer_companion_mood("This isn't working at all!")
        assert result == "frustrated"

    @pytest.mark.asyncio
    async def test_returns_absent(self):
        agent = self._make_agent_with_mock_backend("absent")
        result = await agent._infer_companion_mood("...")
        assert result == "absent"

    @pytest.mark.asyncio
    async def test_returns_happy(self):
        agent = self._make_agent_with_mock_backend("happy")
        result = await agent._infer_companion_mood("That worked perfectly!")
        assert result == "happy"

    @pytest.mark.asyncio
    async def test_empty_string_returns_absent(self):
        """Empty input → absent without calling backend."""
        agent = self._make_agent_with_mock_backend("happy")
        result = await agent._infer_companion_mood("")
        assert result == "absent"
        agent.backend.complete.assert_not_called()

    @pytest.mark.asyncio
    async def test_whitespace_only_returns_absent(self):
        agent = self._make_agent_with_mock_backend("happy")
        result = await agent._infer_companion_mood("   ")
        assert result == "absent"
        agent.backend.complete.assert_not_called()

    @pytest.mark.asyncio
    async def test_very_short_returns_absent(self):
        """Messages shorter than 3 chars → absent."""
        agent = self._make_agent_with_mock_backend("happy")
        result = await agent._infer_companion_mood("ok")
        assert result == "absent"

    @pytest.mark.asyncio
    async def test_invalid_backend_response_falls_back_to_engaged(self):
        """If backend returns garbage, fall back to 'engaged'."""
        agent = self._make_agent_with_mock_backend("UNKNOWN_LABEL_XYZ")
        result = await agent._infer_companion_mood("Hello there friend!")
        assert result == "engaged"

    @pytest.mark.asyncio
    async def test_label_stripped_and_lowercased(self):
        """Backend returning '  Tired  ' (with spaces/caps) is normalised."""
        agent = self._make_agent_with_mock_backend("  Tired  ")
        result = await agent._infer_companion_mood("I'm exhausted")
        assert result == "tired"


# ── Tests for frustrated → desire boost ──────────────────────────────────────


class TestFrustratedBoostsDesire:
    """When companion_mood is frustrated, worry_companion desire is boosted."""

    @pytest.mark.asyncio
    async def test_frustrated_boosts_worry_companion(self):
        """frustrated mood → desires.boost('worry_companion') called."""
        from familiar_agent.desires import DesireSystem
        from familiar_agent.agent import EmbodiedAgent

        # Lightweight agent setup
        agent = EmbodiedAgent.__new__(EmbodiedAgent)
        agent._memory = MagicMock()
        agent._memory.recall_async = AsyncMock(return_value=[])
        agent._memory.recent_feelings_async = AsyncMock(return_value=[])
        agent._memory.recall_self_model_async = AsyncMock(return_value=[])
        agent._memory.recall_curiosities_async = AsyncMock(return_value=[])
        agent._memory.save_async = AsyncMock(return_value=True)
        agent._memory.format_for_context = MagicMock(return_value="")
        agent._memory.format_feelings_for_context = MagicMock(return_value="")
        agent._memory.format_self_model_for_context = MagicMock(return_value="")
        agent._memory.format_curiosities_for_context = MagicMock(return_value="")

        mock_backend = MagicMock()
        # complete() for _infer_companion_mood → "frustrated"
        mock_backend.complete = AsyncMock(return_value="frustrated")

        from familiar_agent.backend import TurnResult

        mock_backend.stream_turn = AsyncMock(
            return_value=(TurnResult(stop_reason="end_turn", text="ok", tool_calls=[]), [])
        )
        mock_backend.make_user_message = MagicMock(
            side_effect=lambda x: {"role": "user", "content": x}
        )
        mock_backend.make_assistant_message = MagicMock(
            return_value={"role": "assistant", "content": []}
        )

        agent.backend = mock_backend
        agent.config = MagicMock()
        agent.config.max_tokens = 512
        agent.config.companion_name = "Kouta"
        agent.messages = []
        agent._started_at = time.time()
        agent._turn_count = 0
        agent._me_md = ""
        agent._camera = None
        agent._mobility = None
        agent._tts = None
        agent._stt = None
        agent._mcp = None
        agent._session_input_tokens = 0
        agent._session_output_tokens = 0
        agent._last_context_tokens = 0
        agent._post_compact = False

        from familiar_agent.tools.memory import MemoryTool
        from familiar_agent.tools.tom import ToMTool
        from familiar_agent.tools.coding import CodingTool

        agent._memory_tool = MagicMock(spec=MemoryTool)
        agent._memory_tool.get_tool_definitions = MagicMock(return_value=[])
        agent._tom_tool = MagicMock(spec=ToMTool)
        agent._tom_tool.get_tool_definitions = MagicMock(return_value=[])
        agent._coding = MagicMock(spec=CodingTool)
        agent._coding.get_tool_definitions = MagicMock(return_value=[])

        from familiar_agent.exploration import ExplorationTracker

        agent._exploration = ExplorationTracker()

        desires = MagicMock(spec=DesireSystem)
        desires.curiosity_target = None

        await agent.run(
            user_input="This is absolutely broken and I'm really frustrated!",
            desires=desires,
        )

        # desires.boost should have been called with worry_companion
        boost_calls = [
            call for call in desires.boost.call_args_list if call.args[0] == "worry_companion"
        ]
        assert len(boost_calls) >= 1, "worry_companion desire should be boosted when frustrated"
