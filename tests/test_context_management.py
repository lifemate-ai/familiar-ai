"""Tests for context_management / thinking token cleanup in AnthropicBackend.

Feature: When thinking is enabled, stream_turn adds context_management to the API request
so the server removes old ThinkingBlocks from the message history (like CC's tengu_marble_anvil).
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


# ── Feature 1: context_management ────────────────────────────────────────────


class TestContextManagementAdded:
    """context_management is added to API call when thinking is enabled."""

    @pytest.mark.asyncio
    async def test_adaptive_mode_adds_context_management(self):
        """adaptive thinking → context_management added."""
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

        assert "extra_body" in captured
        assert "context_management" in captured["extra_body"]
        assert captured["extra_body"]["context_management"] == {
            "edits": [{"type": "clear_thinking_20251015", "keep": "all"}]
        }

    @pytest.mark.asyncio
    async def test_extended_mode_adds_context_management(self):
        """extended thinking → context_management added."""
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

        assert "extra_body" in captured
        assert "context_management" in captured["extra_body"]
        assert (
            captured["extra_body"]["context_management"]["edits"][0]["type"]
            == "clear_thinking_20251015"
        )

    @pytest.mark.asyncio
    async def test_disabled_mode_no_context_management(self):
        """thinking disabled → context_management NOT added."""
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

        assert "context_management" not in captured.get("extra_body", {})

    @pytest.mark.asyncio
    async def test_auto_mode_sonnet4_adds_context_management(self):
        """auto + sonnet-4 → adaptive → context_management added."""
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

        assert "extra_body" in captured
        assert "context_management" in captured["extra_body"]

    @pytest.mark.asyncio
    async def test_auto_mode_haiku_no_context_management(self):
        """auto + haiku → disabled → context_management NOT added."""
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

        assert "context_management" not in captured.get("extra_body", {})

    @pytest.mark.asyncio
    async def test_context_management_edit_keep_all(self):
        """The edit has keep='all' (preserve latest thinking per turn)."""
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

        edit = captured["extra_body"]["context_management"]["edits"][0]
        assert edit["keep"] == "all"
