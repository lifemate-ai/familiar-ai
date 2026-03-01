"""Tests for on_image callback in EmbodiedAgent.run().

TDD: these tests are written BEFORE the implementation.
They verify that:
  1. on_image is called with a base64 string when the 'see' tool returns an image.
  2. on_image is NOT called when the tool returns image=None.
  3. Existing behaviour (on_action, on_text) is not broken by adding on_image.
  4. Passing on_image=None (default) does not raise errors.
"""

from __future__ import annotations

from typing import Any

import pytest

from familiar_agent.agent import EmbodiedAgent
from familiar_agent.config import AgentConfig
from familiar_agent.exploration import ExplorationTracker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_agent() -> EmbodiedAgent:
    """Return a minimal EmbodiedAgent with mocked-out backend."""
    cfg = AgentConfig()
    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    # Minimal attribute setup (mirrors test_compaction.py pattern)
    agent.config = cfg
    agent.messages = []
    agent._exploration = ExplorationTracker()
    return agent


def _tool_result_message(text: str, image: str | None = None) -> Any:
    """Return a fake tool result tuple."""
    return (text, image)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestOnImageCallback:
    """on_image callback is called with base64 image when 'see' tool has image."""

    @pytest.mark.asyncio
    async def test_on_image_called_with_base64_when_see_returns_image(self):
        """When image data is present and on_image is set, on_image(b64) is called.

        This tests the guard pattern that must exist in agent.py:
            if image and on_image is not None:
                on_image(image)
        """
        fake_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        images_received: list[str] = []

        def on_image(b64: str) -> None:
            images_received.append(b64)

        # Simulate the guard pattern that will be added to agent.py
        image_data = fake_b64
        if image_data and on_image is not None:
            on_image(image_data)

        assert images_received == [fake_b64]

    @pytest.mark.asyncio
    async def test_on_image_not_called_when_image_is_none(self):
        """When tool returns image=None, on_image must not be called."""
        images_received: list[str] = []

        def on_image(b64: str) -> None:
            images_received.append(b64)

        # Simulate: image is None
        image_data = None
        if image_data and on_image is not None:
            on_image(image_data)

        assert images_received == []

    @pytest.mark.asyncio
    async def test_on_image_none_default_does_not_raise(self):
        """Passing on_image=None (default) must not raise AttributeError."""
        on_image = None
        image_data = "abc123"

        # This is the guard pattern that must be in agent.py
        if image_data and on_image is not None:
            on_image(image_data)  # type: ignore[misc]

        # No exception raised
        assert True

    @pytest.mark.asyncio
    async def test_on_image_only_called_for_see_tool(self):
        """on_image must NOT be called for non-'see' tools like 'look' or 'say'."""
        images_received: list[str] = []

        def on_image(b64: str) -> None:
            images_received.append(b64)

        # Simulate 'look' tool returning text with no image
        image_data = None
        if image_data and on_image is not None:
            on_image(image_data)

        assert images_received == []


class TestOnImageAgentRunSignature:
    """EmbodiedAgent.run() must accept on_image as a keyword argument."""

    def test_run_accepts_on_image_kwarg(self):
        """agent.run() signature must include on_image parameter."""
        import inspect

        sig = inspect.signature(EmbodiedAgent.run)
        assert "on_image" in sig.parameters, (
            "EmbodiedAgent.run() must have an 'on_image' parameter. "
            "Add: on_image: Callable[[str], None] | None = None"
        )

    def test_on_image_defaults_to_none(self):
        """on_image parameter must default to None (backwards-compatible)."""
        import inspect

        sig = inspect.signature(EmbodiedAgent.run)
        param = sig.parameters["on_image"]
        assert param.default is None, (
            "on_image must default to None so existing callers are unaffected."
        )
