"""Tests for adaptive thinking and fast mode in AnthropicBackend.

Tests follow TDD: these tests are written BEFORE implementation.
All tests should FAIL until the implementation is added.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


# ── Module-level helper (not yet implemented) ──────────────────────────────


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
        self, model: str, thinking_mode: str, thinking_budget: int = 10000, fast_mode: bool = False
    ):
        from familiar_agent.backend import AnthropicBackend

        with patch("anthropic.AsyncAnthropic"):
            return AnthropicBackend(
                api_key="test-key",
                model=model,
                thinking_mode=thinking_mode,
                thinking_budget=thinking_budget,
                fast_mode=fast_mode,
            )

    def test_disabled_returns_no_thinking_key(self):
        b = self._make_backend("claude-sonnet-4-6", "disabled")
        params = b._build_thinking_params()
        assert "thinking" not in params

    def test_disabled_betas_empty(self):
        b = self._make_backend("claude-sonnet-4-6", "disabled")
        params = b._build_thinking_params()
        assert params.get("betas", []) == []

    def test_adaptive_mode_thinking_type(self):
        b = self._make_backend("claude-sonnet-4-6", "adaptive")
        params = b._build_thinking_params()
        assert params["thinking"] == {"type": "adaptive"}

    def test_adaptive_mode_betas_include_adaptive_header(self):
        b = self._make_backend("claude-sonnet-4-6", "adaptive")
        params = b._build_thinking_params()
        assert "adaptive-thinking-2026-01-28" in params["betas"]

    def test_adaptive_mode_betas_include_interleaved_header(self):
        b = self._make_backend("claude-sonnet-4-6", "adaptive")
        params = b._build_thinking_params()
        assert "interleaved-thinking-2025-05-14" in params["betas"]

    def test_extended_mode_thinking_type(self):
        b = self._make_backend("claude-sonnet-4-6", "extended", thinking_budget=5000)
        params = b._build_thinking_params()
        assert params["thinking"] == {"type": "enabled", "budget_tokens": 5000}

    def test_extended_mode_betas_include_interleaved(self):
        b = self._make_backend("claude-sonnet-4-6", "extended")
        params = b._build_thinking_params()
        assert "interleaved-thinking-2025-05-14" in params["betas"]

    def test_auto_mode_sonnet_4_becomes_adaptive(self):
        b = self._make_backend("claude-sonnet-4-6", "auto")
        params = b._build_thinking_params()
        assert params.get("thinking", {}).get("type") == "adaptive"

    def test_auto_mode_haiku_becomes_disabled(self):
        b = self._make_backend("claude-haiku-4-5-20251001", "auto")
        params = b._build_thinking_params()
        assert "thinking" not in params

    def test_fast_mode_adds_fast_mode_beta(self):
        b = self._make_backend("claude-sonnet-4-6", "disabled", fast_mode=True)
        params = b._build_thinking_params()
        assert "fast-mode-2026-02-01" in params["betas"]

    def test_adaptive_with_fast_mode_includes_both_betas(self):
        b = self._make_backend("claude-sonnet-4-6", "adaptive", fast_mode=True)
        params = b._build_thinking_params()
        betas = params["betas"]
        assert "adaptive-thinking-2026-01-28" in betas
        assert "fast-mode-2026-02-01" in betas

    def test_fast_mode_false_no_fast_mode_beta(self):
        b = self._make_backend("claude-sonnet-4-6", "adaptive", fast_mode=False)
        params = b._build_thinking_params()
        assert "fast-mode-2026-02-01" not in params.get("betas", [])


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

    def _make_backend(self, model: str, thinking_mode: str, fast_mode: bool = False):
        from familiar_agent.backend import AnthropicBackend

        with patch("anthropic.AsyncAnthropic"):
            b = AnthropicBackend(
                api_key="test-key",
                model=model,
                thinking_mode=thinking_mode,
                fast_mode=fast_mode,
            )
        return b

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

    def test_adaptive_thinking_passes_beta_header(self):
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
            assert "extra_headers" in kwargs
            assert "anthropic-beta" in kwargs["extra_headers"]
            assert "adaptive-thinking-2026-01-28" in kwargs["extra_headers"]["anthropic-beta"]

    def test_disabled_no_extra_headers(self):
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
            assert kwargs.get("extra_headers", {}) == {}

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


# ── AgentConfig env-var reading ────────────────────────────────────────────


class TestAgentConfig:
    """Verify that AgentConfig reads thinking-related env vars."""

    def test_thinking_mode_default_is_auto(self, monkeypatch):
        monkeypatch.delenv("THINKING_MODE", raising=False)
        # reimport to pick up fresh env
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

    def test_fast_mode_default_false(self, monkeypatch):
        monkeypatch.delenv("FAST_MODE", raising=False)
        import importlib
        import familiar_agent.config as cfg_mod

        importlib.reload(cfg_mod)
        from familiar_agent.config import AgentConfig

        config = AgentConfig()
        assert config.fast_mode is False

    def test_fast_mode_true(self, monkeypatch):
        monkeypatch.setenv("FAST_MODE", "true")
        import importlib
        import familiar_agent.config as cfg_mod

        importlib.reload(cfg_mod)
        from familiar_agent.config import AgentConfig

        config = AgentConfig()
        assert config.fast_mode is True

    def test_fast_mode_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("FAST_MODE", "True")
        import importlib
        import familiar_agent.config as cfg_mod

        importlib.reload(cfg_mod)
        from familiar_agent.config import AgentConfig

        config = AgentConfig()
        assert config.fast_mode is True


# ── helpers ────────────────────────────────────────────────────────────────


async def _async_gen(items):
    """Helper: async generator that yields items."""
    for item in items:
        yield item
