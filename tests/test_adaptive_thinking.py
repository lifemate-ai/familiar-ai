"""Tests for adaptive thinking and fast mode in AnthropicBackend.

Based on official Anthropic docs (https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking):
- adaptive thinking: NO beta header needed (GA feature on Opus/Sonnet 4.6)
- adaptive mode automatically enables interleaved thinking
- extended mode on Sonnet 4.6 needs interleaved-thinking-2025-05-14 for interleaved support
- effort parameter via output_config (adaptive mode only)
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


# ── _supports_adaptive_thinking() ─────────────────────────────────────────


class TestSupportsAdaptiveThinking:
    """_supports_adaptive_thinking() — model detection."""

    def test_sonnet_4_6_is_supported(self):
        from familiar_agent.backend import _supports_adaptive_thinking

        assert _supports_adaptive_thinking("claude-sonnet-4-6") is True

    def test_sonnet_4_partial_name(self):
        from familiar_agent.backend import _supports_adaptive_thinking

        assert _supports_adaptive_thinking("claude-sonnet-4-5-20251022") is True

    def test_opus_4_6_is_supported(self):
        from familiar_agent.backend import _supports_adaptive_thinking

        assert _supports_adaptive_thinking("claude-opus-4-6") is True

    def test_opus_4_partial_name(self):
        from familiar_agent.backend import _supports_adaptive_thinking

        assert _supports_adaptive_thinking("claude-opus-4") is True

    def test_haiku_not_supported(self):
        from familiar_agent.backend import _supports_adaptive_thinking

        assert _supports_adaptive_thinking("claude-haiku-4-5-20251001") is False

    def test_sonnet_3_5_not_supported(self):
        from familiar_agent.backend import _supports_adaptive_thinking

        assert _supports_adaptive_thinking("claude-3-5-sonnet-20241022") is False

    def test_empty_string_not_supported(self):
        from familiar_agent.backend import _supports_adaptive_thinking

        assert _supports_adaptive_thinking("") is False


# ── _build_thinking_params() ───────────────────────────────────────────────


class TestBuildThinkingParams:
    """AnthropicBackend._build_thinking_params()"""

    def _make_backend(
        self,
        model: str,
        thinking_mode: str,
        thinking_budget: int = 10000,
        thinking_effort: str = "high",
    ):
        from familiar_agent.backend import AnthropicBackend

        with patch("anthropic.AsyncAnthropic"):
            return AnthropicBackend(
                api_key="test-key",
                model=model,
                thinking_mode=thinking_mode,
                thinking_budget=thinking_budget,
                thinking_effort=thinking_effort,
            )

    def test_disabled_returns_empty_dict(self):
        b = self._make_backend("claude-sonnet-4-6", "disabled")
        params = b._build_thinking_params()
        assert params == {}

    def test_adaptive_mode_thinking_type(self):
        b = self._make_backend("claude-sonnet-4-6", "adaptive")
        params = b._build_thinking_params()
        assert params["thinking"] == {"type": "adaptive"}

    def test_adaptive_mode_no_beta_header_needed(self):
        """Adaptive thinking is GA — no anthropic-beta header required."""
        b = self._make_backend("claude-sonnet-4-6", "adaptive")
        params = b._build_thinking_params()
        assert "betas" not in params

    def test_adaptive_mode_default_effort_no_output_config(self):
        """Default effort 'high' should NOT add output_config (it's the default)."""
        b = self._make_backend("claude-sonnet-4-6", "adaptive", thinking_effort="high")
        params = b._build_thinking_params()
        assert "output_config" not in params

    def test_adaptive_mode_medium_effort_adds_output_config(self):
        b = self._make_backend("claude-sonnet-4-6", "adaptive", thinking_effort="medium")
        params = b._build_thinking_params()
        assert params["output_config"] == {"effort": "medium"}

    def test_adaptive_mode_low_effort(self):
        b = self._make_backend("claude-sonnet-4-6", "adaptive", thinking_effort="low")
        params = b._build_thinking_params()
        assert params["output_config"] == {"effort": "low"}

    def test_adaptive_mode_max_effort(self):
        b = self._make_backend("claude-opus-4-6", "adaptive", thinking_effort="max")
        params = b._build_thinking_params()
        assert params["output_config"] == {"effort": "max"}

    def test_extended_mode_thinking_type(self):
        b = self._make_backend("claude-sonnet-4-6", "extended", thinking_budget=5000)
        params = b._build_thinking_params()
        assert params["thinking"] == {"type": "enabled", "budget_tokens": 5000}

    def test_extended_mode_sonnet4_includes_interleaved_beta(self):
        """Interleaved thinking beta is needed for manual mode on Sonnet 4.6."""
        b = self._make_backend("claude-sonnet-4-6", "extended")
        params = b._build_thinking_params()
        assert "interleaved-thinking-2025-05-14" in params.get("betas", [])

    def test_extended_mode_opus4_no_interleaved_beta(self):
        """Opus 4.6 extended mode does NOT support interleaved thinking."""
        b = self._make_backend("claude-opus-4-6", "extended")
        params = b._build_thinking_params()
        assert "betas" not in params

    def test_auto_mode_sonnet_4_becomes_adaptive(self):
        b = self._make_backend("claude-sonnet-4-6", "auto")
        params = b._build_thinking_params()
        assert params.get("thinking", {}).get("type") == "adaptive"

    def test_auto_mode_haiku_becomes_disabled(self):
        b = self._make_backend("claude-haiku-4-5-20251001", "auto")
        params = b._build_thinking_params()
        assert "thinking" not in params


# ── stream_turn integration (mocked) ──────────────────────────────────────


class TestStreamTurnThinkingIntegration:
    """Verify that stream_turn passes thinking params and headers to API."""

    def _make_stream_mock(self, content_blocks: list):
        """Build a mock stream context manager."""
        mock_stream = AsyncMock()
        mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_stream.__aexit__ = AsyncMock(return_value=False)

        # text_stream yields nothing (thinking blocks are auto-filtered by SDK)
        mock_stream.text_stream = _async_gen([])

        mock_response = MagicMock()
        mock_response.content = content_blocks
        mock_response.stop_reason = "end_turn"
        mock_stream.get_final_message = AsyncMock(return_value=mock_response)
        return mock_stream

    def _text_block(self, text: str):
        block = MagicMock()
        block.type = "text"
        block.text = text
        return block

    def _thinking_block(self):
        block = MagicMock()
        block.type = "thinking"
        # ThinkingBlock has no .text attribute
        del block.text
        return block

    def _make_backend(self, model: str, thinking_mode: str, thinking_effort: str = "high"):
        from familiar_agent.backend import AnthropicBackend

        with patch("anthropic.AsyncAnthropic"):
            return AnthropicBackend(
                api_key="test-key",
                model=model,
                thinking_mode=thinking_mode,
                thinking_effort=thinking_effort,
            )

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_adaptive_thinking_passes_thinking_kwarg(self):
        backend = self._make_backend("claude-sonnet-4-6", "adaptive")
        mock_stream = self._make_stream_mock([self._text_block("hello")])

        with patch.object(backend.client.messages, "stream", return_value=mock_stream) as mock_call:
            self._run(
                backend.stream_turn(
                    system="sys",
                    messages=[],
                    tools=[],
                    max_tokens=1000,
                    on_text=None,
                )
            )
            _, kwargs = mock_call.call_args
            assert "thinking" in kwargs
            assert kwargs["thinking"]["type"] == "adaptive"

    def test_adaptive_thinking_no_beta_header(self):
        """GA feature — no anthropic-beta header should be sent."""
        backend = self._make_backend("claude-sonnet-4-6", "adaptive")
        mock_stream = self._make_stream_mock([self._text_block("hello")])

        with patch.object(backend.client.messages, "stream", return_value=mock_stream) as mock_call:
            self._run(
                backend.stream_turn(
                    system="sys",
                    messages=[],
                    tools=[],
                    max_tokens=1000,
                    on_text=None,
                )
            )
            _, kwargs = mock_call.call_args
            assert "extra_headers" not in kwargs

    def test_disabled_no_thinking_kwarg(self):
        backend = self._make_backend("claude-haiku-4-5-20251001", "disabled")
        mock_stream = self._make_stream_mock([self._text_block("hello")])

        with patch.object(backend.client.messages, "stream", return_value=mock_stream) as mock_call:
            self._run(
                backend.stream_turn(
                    system="sys",
                    messages=[],
                    tools=[],
                    max_tokens=1000,
                    on_text=None,
                )
            )
            _, kwargs = mock_call.call_args
            assert "thinking" not in kwargs
            assert "extra_headers" not in kwargs

    def test_thinking_blocks_excluded_from_text(self):
        """ThinkingBlocks in response.content must NOT appear in TurnResult.text."""
        backend = self._make_backend("claude-sonnet-4-6", "adaptive")
        content = [self._thinking_block(), self._text_block("real answer")]
        mock_stream = self._make_stream_mock(content)

        with patch.object(backend.client.messages, "stream", return_value=mock_stream):
            result, raw = self._run(
                backend.stream_turn(
                    system="sys",
                    messages=[],
                    tools=[],
                    max_tokens=1000,
                    on_text=None,
                )
            )
        assert result.text == "real answer"

    def test_thinking_blocks_present_in_raw_content(self):
        """raw_content must include ThinkingBlocks for multi-turn round-trip."""
        backend = self._make_backend("claude-sonnet-4-6", "adaptive")
        thinking = self._thinking_block()
        text = self._text_block("answer")
        content = [thinking, text]
        mock_stream = self._make_stream_mock(content)

        with patch.object(backend.client.messages, "stream", return_value=mock_stream):
            _, raw = self._run(
                backend.stream_turn(
                    system="sys",
                    messages=[],
                    tools=[],
                    max_tokens=1000,
                    on_text=None,
                )
            )
        # raw_content must include both blocks (ThinkingBlock + TextBlock)
        assert len(raw) == 2

    def test_effort_medium_passes_output_config(self):
        backend = self._make_backend("claude-sonnet-4-6", "adaptive", thinking_effort="medium")
        mock_stream = self._make_stream_mock([self._text_block("hello")])

        with patch.object(backend.client.messages, "stream", return_value=mock_stream) as mock_call:
            self._run(
                backend.stream_turn(
                    system="sys",
                    messages=[],
                    tools=[],
                    max_tokens=1000,
                    on_text=None,
                )
            )
            _, kwargs = mock_call.call_args
            assert kwargs.get("output_config") == {"effort": "medium"}


# ── AgentConfig env-var reading ────────────────────────────────────────────


class TestAgentConfig:
    """Verify that AgentConfig reads thinking-related env vars."""

    def test_thinking_mode_default_is_auto(self, monkeypatch):
        monkeypatch.delenv("THINKING_MODE", raising=False)
        import importlib

        import familiar_agent.config as cfg_mod

        importlib.reload(cfg_mod)
        from familiar_agent.config import AgentConfig

        config = AgentConfig()
        assert config.thinking_mode == "auto"

    def test_thinking_mode_env_adaptive(self, monkeypatch):
        monkeypatch.setenv("THINKING_MODE", "adaptive")
        import importlib

        import familiar_agent.config as cfg_mod

        importlib.reload(cfg_mod)
        from familiar_agent.config import AgentConfig

        config = AgentConfig()
        assert config.thinking_mode == "adaptive"

    def test_thinking_budget_default(self, monkeypatch):
        monkeypatch.delenv("THINKING_BUDGET_TOKENS", raising=False)
        import importlib

        import familiar_agent.config as cfg_mod

        importlib.reload(cfg_mod)
        from familiar_agent.config import AgentConfig

        config = AgentConfig()
        assert config.thinking_budget == 10000

    def test_thinking_budget_custom(self, monkeypatch):
        monkeypatch.setenv("THINKING_BUDGET_TOKENS", "5000")
        import importlib

        import familiar_agent.config as cfg_mod

        importlib.reload(cfg_mod)
        from familiar_agent.config import AgentConfig

        config = AgentConfig()
        assert config.thinking_budget == 5000

    def test_thinking_effort_default_high(self, monkeypatch):
        monkeypatch.delenv("THINKING_EFFORT", raising=False)
        import importlib

        import familiar_agent.config as cfg_mod

        importlib.reload(cfg_mod)
        from familiar_agent.config import AgentConfig

        config = AgentConfig()
        assert config.thinking_effort == "high"

    def test_thinking_effort_medium(self, monkeypatch):
        monkeypatch.setenv("THINKING_EFFORT", "medium")
        import importlib

        import familiar_agent.config as cfg_mod

        importlib.reload(cfg_mod)
        from familiar_agent.config import AgentConfig

        config = AgentConfig()
        assert config.thinking_effort == "medium"

    def test_thinking_effort_low(self, monkeypatch):
        monkeypatch.setenv("THINKING_EFFORT", "low")
        import importlib

        import familiar_agent.config as cfg_mod

        importlib.reload(cfg_mod)
        from familiar_agent.config import AgentConfig

        config = AgentConfig()
        assert config.thinking_effort == "low"


# ── helpers ────────────────────────────────────────────────────────────────


async def _async_gen(items):
    """Helper: async generator that yields items."""
    for item in items:
        yield item
