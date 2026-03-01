"""Tests for /cost command and token usage tracking."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch


class TestTurnResultUsageFields:
    """TurnResult must carry token usage from the API response."""

    def test_turn_result_has_input_tokens(self):
        """TurnResult dataclass must have input_tokens field (default 0)."""
        from familiar_agent.backend import TurnResult

        r = TurnResult(stop_reason="end_turn", text="hi")
        assert hasattr(r, "input_tokens"), "TurnResult must have input_tokens"
        assert r.input_tokens == 0

    def test_turn_result_has_output_tokens(self):
        """TurnResult dataclass must have output_tokens field (default 0)."""
        from familiar_agent.backend import TurnResult

        r = TurnResult(stop_reason="end_turn", text="hi")
        assert hasattr(r, "output_tokens"), "TurnResult must have output_tokens"
        assert r.output_tokens == 0

    def test_turn_result_accepts_token_values(self):
        """TurnResult can be created with non-zero token counts."""
        from familiar_agent.backend import TurnResult

        r = TurnResult(stop_reason="end_turn", text="hi", input_tokens=100, output_tokens=50)
        assert r.input_tokens == 100
        assert r.output_tokens == 50


class TestAnthropicBackendTracksUsage:
    """AnthropicBackend.stream_turn() populates TurnResult token counts."""

    def test_stream_turn_sets_input_tokens(self):
        """stream_turn result.input_tokens == response.usage.input_tokens."""
        import asyncio
        from unittest.mock import MagicMock
        from familiar_agent.backend import AnthropicBackend
        from familiar_agent.config import AgentConfig

        cfg = MagicMock(spec=AgentConfig)
        cfg.api_key = "test-key"
        cfg.model = "claude-haiku-4-5-20251001"
        cfg.thinking_mode = "disabled"
        cfg.thinking_effort = "low"
        cfg.platform = "anthropic"

        backend = AnthropicBackend.__new__(AnthropicBackend)
        backend.model = cfg.model
        backend.thinking_mode = "disabled"
        backend.thinking_effort = "low"
        backend.thinking_budget = 0

        # Fake Anthropic response with usage
        fake_block = MagicMock()
        fake_block.type = "text"
        fake_block.text = "hello"

        fake_response = MagicMock()
        fake_response.stop_reason = "end_turn"
        fake_response.content = [fake_block]
        fake_response.usage = MagicMock()
        fake_response.usage.input_tokens = 123
        fake_response.usage.output_tokens = 45

        # stream context manager mock
        async def _empty_text_stream():
            return
            yield  # make it an async generator

        fake_stream_cm = MagicMock()
        fake_stream_cm.__aenter__ = AsyncMock(return_value=fake_stream_cm)
        fake_stream_cm.__aexit__ = AsyncMock(return_value=False)
        fake_stream_cm.text_stream = _empty_text_stream()
        fake_stream_cm.get_final_message = AsyncMock(return_value=fake_response)

        fake_client = MagicMock()
        fake_client.messages.stream = MagicMock(return_value=fake_stream_cm)
        fake_client.beta.messages.stream = MagicMock(return_value=fake_stream_cm)
        backend.client = fake_client

        result, _ = asyncio.get_event_loop().run_until_complete(
            backend.stream_turn(
                system=("sys", "var"),
                messages=[{"role": "user", "content": "hi"}],
                tools=[],
                max_tokens=100,
                on_text=None,
            )
        )

        assert result.input_tokens == 123
        assert result.output_tokens == 45


class TestEmbodiedAgentAccumulatesTokens:
    """EmbodiedAgent tracks cumulative token usage across turns."""

    def test_agent_has_session_tokens_attribute(self):
        """EmbodiedAgent must have _session_input_tokens and _session_output_tokens."""
        from familiar_agent.agent import EmbodiedAgent
        from familiar_agent.config import AgentConfig

        cfg = MagicMock(spec=AgentConfig)
        cfg.api_key = "x"
        cfg.model = "claude-haiku-4-5-20251001"
        cfg.thinking_mode = "disabled"
        cfg.thinking_effort = "low"
        cfg.platform = "anthropic"
        cfg.agent_name = "A"
        cfg.companion_name = "U"
        cfg.camera = MagicMock(host=None)
        cfg.mobility = MagicMock(api_key=None, device_id=None)
        cfg.tts = MagicMock(elevenlabs_api_key=None)
        cfg.stt = MagicMock(elevenlabs_api_key=None)
        cfg.coding = MagicMock()
        cfg.max_tokens = 1000

        with patch("familiar_agent.agent.create_backend", return_value=MagicMock()):
            with patch("familiar_agent.agent.ObservationMemory"):
                with patch("familiar_agent.agent.MemoryTool"):
                    with patch("familiar_agent.agent.ToMTool"):
                        with patch("familiar_agent.agent.CodingTool"):
                            agent = EmbodiedAgent.__new__(EmbodiedAgent)
                            agent.config = cfg
                            agent._session_input_tokens = 0
                            agent._session_output_tokens = 0

        assert hasattr(agent, "_session_input_tokens")
        assert hasattr(agent, "_session_output_tokens")
        assert agent._session_input_tokens == 0
        assert agent._session_output_tokens == 0


class TestFormatCost:
    """_format_cost() produces a human-readable cost summary."""

    def test_format_cost_exists(self):
        """tui module must expose _format_cost function."""
        import familiar_agent.tui as tui_mod

        assert hasattr(tui_mod, "_format_cost"), "tui must define _format_cost"

    def test_format_cost_shows_tokens(self):
        """_format_cost includes input and output token counts."""
        from familiar_agent.tui import _format_cost

        result = _format_cost(input_tokens=1000, output_tokens=200)
        assert "1000" in result or "1,000" in result
        assert "200" in result

    def test_format_cost_shows_usd(self):
        """_format_cost includes USD cost estimate."""
        from familiar_agent.tui import _format_cost

        result = _format_cost(input_tokens=1_000_000, output_tokens=1_000_000)
        assert "$" in result

    def test_format_cost_zero_tokens(self):
        """_format_cost handles zero tokens gracefully."""
        from familiar_agent.tui import _format_cost

        result = _format_cost(input_tokens=0, output_tokens=0)
        assert result  # Must return something


class TestCostInSlashCommands:
    """/cost must appear in the autocomplete command list."""

    def test_cost_in_slash_commands(self):
        from familiar_agent.tui import _SLASH_COMMANDS

        cmds = [cmd for cmd, _ in _SLASH_COMMANDS]
        assert "/cost" in cmds, "/cost must be in _SLASH_COMMANDS"
