"""Tests for thinking parameter handling in AnthropicBackend.

Feature: When thinking is enabled, stream_turn adds the appropriate thinking
parameters to the API request.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_backend(thinking_mode: str = "adaptive", model: str = "claude-sonnet-4-6"):
    from familiar_agent.backend import AnthropicBackend

    with patch("anthropic.AsyncAnthropic"):
        b = AnthropicBackend.__new__(AnthropicBackend)
        b.client = MagicMock()
        b.model = model
        b.thinking_mode = thinking_mode
        b.thinking_budget = 10000
        b.thinking_effort = "high"
        return b


def _make_stream_response(stop_reason: str = "end_turn"):
    """Return a mock that mimics the anthropic streaming context manager."""
    block = MagicMock()
    block.type = "text"
    block.text = "hello"

    final_message = MagicMock()
    final_message.stop_reason = stop_reason
    final_message.content = [block]

    stream_cm = MagicMock()
    stream_cm.__aenter__ = AsyncMock(return_value=stream_cm)
    stream_cm.__aexit__ = AsyncMock(return_value=False)
    stream_cm.text_stream = _async_iter(["hello"])
    stream_cm.get_final_message = AsyncMock(return_value=final_message)
    return stream_cm


async def _async_iter(items):
    for item in items:
        yield item


# ── Thinking parameter tests ──────────────────────────────────────────────────


class TestThinkingParams:
    """thinking parameter is added to API call when thinking is enabled."""

    @pytest.mark.asyncio
    async def test_adaptive_mode_adds_thinking(self):
        """adaptive thinking → thinking param added."""
        backend = _make_backend(thinking_mode="adaptive")
        captured: dict = {}

        def capture_kwargs(**kwargs):
            captured.update(kwargs)
            return _make_stream_response()

        backend.client.messages.stream = MagicMock(side_effect=capture_kwargs)

        await backend.stream_turn(
            system="sys",
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            max_tokens=1024,
            on_text=None,
        )

        assert "thinking" in captured

    @pytest.mark.asyncio
    async def test_extended_mode_adds_thinking(self):
        """extended thinking → thinking param added."""
        backend = _make_backend(thinking_mode="extended")
        captured: dict = {}

        def capture_kwargs(**kwargs):
            captured.update(kwargs)
            return _make_stream_response()

        backend.client.messages.stream = MagicMock(side_effect=capture_kwargs)

        await backend.stream_turn(
            system="sys",
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            max_tokens=16000,
            on_text=None,
        )

        assert "thinking" in captured

    @pytest.mark.asyncio
    async def test_disabled_mode_no_thinking(self):
        """thinking disabled → thinking param NOT added."""
        backend = _make_backend(thinking_mode="disabled")
        captured: dict = {}

        def capture_kwargs(**kwargs):
            captured.update(kwargs)
            return _make_stream_response()

        backend.client.messages.stream = MagicMock(side_effect=capture_kwargs)

        await backend.stream_turn(
            system="sys",
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            max_tokens=1024,
            on_text=None,
        )

        assert "thinking" not in captured

    @pytest.mark.asyncio
    async def test_auto_mode_sonnet4_adds_thinking(self):
        """auto + sonnet-4 → adaptive → thinking added."""
        backend = _make_backend(thinking_mode="auto", model="claude-sonnet-4-6")
        captured: dict = {}

        def capture_kwargs(**kwargs):
            captured.update(kwargs)
            return _make_stream_response()

        backend.client.messages.stream = MagicMock(side_effect=capture_kwargs)

        await backend.stream_turn(
            system="sys",
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            max_tokens=1024,
            on_text=None,
        )

        assert "thinking" in captured

    @pytest.mark.asyncio
    async def test_auto_mode_haiku_no_thinking(self):
        """auto + haiku → disabled → thinking NOT added."""
        backend = _make_backend(thinking_mode="auto", model="claude-haiku-4-5-20251001")
        captured: dict = {}

        def capture_kwargs(**kwargs):
            captured.update(kwargs)
            return _make_stream_response()

        backend.client.messages.stream = MagicMock(side_effect=capture_kwargs)

        await backend.stream_turn(
            system="sys",
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            max_tokens=1024,
            on_text=None,
        )

        assert "thinking" not in captured

    @pytest.mark.asyncio
    async def test_no_extra_body_added(self):
        """No extra_body is injected (context_management not yet public)."""
        backend = _make_backend(thinking_mode="adaptive")
        captured: dict = {}

        def capture_kwargs(**kwargs):
            captured.update(kwargs)
            return _make_stream_response()

        backend.client.messages.stream = MagicMock(side_effect=capture_kwargs)

        await backend.stream_turn(
            system="sys",
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            max_tokens=1024,
            on_text=None,
        )

        assert "extra_body" not in captured
