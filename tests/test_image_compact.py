"""Tests for image microcompact in AnthropicBackend.

Feature: compact_images() strips base64 image data from old tool results,
keeping only the last `keep_last` images (human-like forgetting).

Inspired by Claude Code's Dk() microcompact function:
  KEEP_LAST=3, images replaced with [image cleared]
"""

from __future__ import annotations

import copy

import pytest

from familiar_agent.backend import AnthropicBackend


def _tool_result_msg(tool_use_id: str, text: str, image_b64: str | None = None) -> dict:
    """Build a flattened tool-result user message like make_tool_results() produces."""
    content_items: list[dict] = [{"type": "text", "text": text}]
    if image_b64:
        content_items.append(
            {
                "type": "image",
                "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64},
            }
        )
    return {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": content_items,
            }
        ],
    }


def _user_msg(text: str) -> dict:
    return {"role": "user", "content": text}


def _assistant_msg(text: str) -> dict:
    return {"role": "assistant", "content": [{"type": "text", "text": text}]}


# ── Unit tests for compact_images() ──────────────────────────────────────────


class TestCompactImagesNoImages:
    def test_no_images_returns_same_messages(self):
        """Messages without images are returned unchanged."""
        messages = [_user_msg("hi"), _assistant_msg("hello")]
        result = AnthropicBackend.compact_images(messages, keep_last=3)
        assert result == messages

    def test_text_only_tool_results_unchanged(self):
        """Tool results with only text (no image) are not modified."""
        messages = [_tool_result_msg("tc1", "I looked around")]
        result = AnthropicBackend.compact_images(messages, keep_last=3)
        assert result == messages


class TestCompactImagesBelowThreshold:
    def test_fewer_images_than_keep_last_unchanged(self):
        """2 images with keep_last=3 → nothing cleared."""
        messages = [
            _tool_result_msg("tc1", "saw a cat", "BASE64_IMG_1"),
            _tool_result_msg("tc2", "saw a dog", "BASE64_IMG_2"),
        ]
        result = AnthropicBackend.compact_images(messages, keep_last=3)
        # Images preserved
        assert result[0]["content"][0]["content"][1]["type"] == "image"
        assert result[1]["content"][0]["content"][1]["type"] == "image"

    def test_exactly_keep_last_images_unchanged(self):
        """Exactly 3 images with keep_last=3 → nothing cleared."""
        messages = [
            _tool_result_msg("tc1", "saw a cat", "IMG1"),
            _tool_result_msg("tc2", "saw a dog", "IMG2"),
            _tool_result_msg("tc3", "saw a bird", "IMG3"),
        ]
        result = AnthropicBackend.compact_images(messages, keep_last=3)
        for i, msg in enumerate(result):
            img_items = [
                s
                for s in msg["content"][0]["content"]
                if isinstance(s, dict) and s.get("type") == "image"
            ]
            assert len(img_items) == 1, f"Image at index {i} should be preserved"


class TestCompactImagesClearsOld:
    def test_one_extra_image_clears_oldest(self):
        """4 images, keep_last=3 → oldest 1 cleared."""
        messages = [
            _tool_result_msg("tc1", "saw a cat", "OLD_IMG"),
            _tool_result_msg("tc2", "saw a dog", "IMG2"),
            _tool_result_msg("tc3", "saw a bird", "IMG3"),
            _tool_result_msg("tc4", "saw a fish", "IMG4"),
        ]
        result = AnthropicBackend.compact_images(messages, keep_last=3)

        # First message: image should be cleared
        cleared_content = result[0]["content"][0]["content"]
        assert not any(s.get("type") == "image" for s in cleared_content if isinstance(s, dict))
        cleared_texts = [s["text"] for s in cleared_content if s.get("type") == "text"]
        assert "[image cleared]" in cleared_texts

        # Last 3 messages: images preserved
        for msg in result[1:]:
            img_items = [
                s
                for s in msg["content"][0]["content"]
                if isinstance(s, dict) and s.get("type") == "image"
            ]
            assert len(img_items) == 1

    def test_two_extra_images_clears_two_oldest(self):
        """5 images, keep_last=3 → oldest 2 cleared."""
        messages = [
            _tool_result_msg("tc1", "old1", "OLD1"),
            _tool_result_msg("tc2", "old2", "OLD2"),
            _tool_result_msg("tc3", "keep1", "KEEP1"),
            _tool_result_msg("tc4", "keep2", "KEEP2"),
            _tool_result_msg("tc5", "keep3", "KEEP3"),
        ]
        result = AnthropicBackend.compact_images(messages, keep_last=3)

        # First 2: cleared
        for msg in result[:2]:
            content = msg["content"][0]["content"]
            assert not any(s.get("type") == "image" for s in content if isinstance(s, dict))
            texts = [s["text"] for s in content if isinstance(s, dict) and s.get("type") == "text"]
            assert "[image cleared]" in texts

        # Last 3: preserved
        for msg in result[2:]:
            content = msg["content"][0]["content"]
            img_items = [s for s in content if isinstance(s, dict) and s.get("type") == "image"]
            assert len(img_items) == 1

    def test_text_description_preserved_after_clear(self):
        """Text description in the tool result is preserved when image is cleared."""
        messages = [
            _tool_result_msg("tc1", "I saw a sleeping cat on the couch", "IMG_DATA"),
            _tool_result_msg("tc2", "img2", "IMG2"),
            _tool_result_msg("tc3", "img3", "IMG3"),
            _tool_result_msg("tc4", "img4", "IMG4"),
        ]
        result = AnthropicBackend.compact_images(messages, keep_last=3)

        # The text describing the image should still be there
        content = result[0]["content"][0]["content"]
        texts = [s["text"] for s in content if isinstance(s, dict) and s.get("type") == "text"]
        assert "I saw a sleeping cat on the couch" in texts


class TestCompactImagesImmutability:
    def test_original_messages_not_mutated(self):
        """compact_images() does a deep copy — original messages unchanged."""
        messages = [
            _tool_result_msg("tc1", "img1", "IMG_DATA_1"),
            _tool_result_msg("tc2", "img2", "IMG_DATA_2"),
            _tool_result_msg("tc3", "img3", "IMG_DATA_3"),
            _tool_result_msg("tc4", "img4", "IMG_DATA_4"),
        ]
        original = copy.deepcopy(messages)
        AnthropicBackend.compact_images(messages, keep_last=3)
        assert messages == original

    def test_returns_new_list(self):
        """compact_images() returns a new list object."""
        messages = [
            _tool_result_msg("tc1", "img1", "IMG1"),
            _tool_result_msg("tc2", "img2", "IMG2"),
            _tool_result_msg("tc3", "img3", "IMG3"),
            _tool_result_msg("tc4", "img4", "IMG4"),
        ]
        result = AnthropicBackend.compact_images(messages, keep_last=3)
        assert result is not messages


class TestCompactImagesEdgeCases:
    def test_keep_last_zero_clears_all(self):
        """keep_last=0 → all images cleared."""
        messages = [
            _tool_result_msg("tc1", "img1", "IMG1"),
            _tool_result_msg("tc2", "img2", "IMG2"),
        ]
        result = AnthropicBackend.compact_images(messages, keep_last=0)
        for msg in result:
            content = msg["content"][0]["content"]
            assert not any(s.get("type") == "image" for s in content if isinstance(s, dict))

    def test_mixed_with_without_images(self):
        """Messages mix tool results with and without images."""
        messages = [
            _tool_result_msg("tc1", "text only"),  # no image
            _tool_result_msg("tc2", "saw a cat", "IMG1"),
            _tool_result_msg("tc3", "text only 2"),  # no image
            _tool_result_msg("tc4", "saw a dog", "IMG2"),
            _tool_result_msg("tc5", "saw a fish", "IMG3"),
            _tool_result_msg("tc6", "saw a bird", "IMG4"),
        ]
        result = AnthropicBackend.compact_images(messages, keep_last=3)

        # Only tc2 (index 1) should have its image cleared
        def has_image(msg):
            content = msg["content"][0]["content"]
            return any(isinstance(s, dict) and s.get("type") == "image" for s in content)

        assert not has_image(result[1])  # tc2 cleared
        assert has_image(result[3])  # tc4 kept
        assert has_image(result[4])  # tc5 kept
        assert has_image(result[5])  # tc6 kept

    def test_non_tool_result_messages_ignored(self):
        """Non-tool-result messages (user text, assistant) are not touched."""
        messages = [
            _user_msg("hello"),
            _assistant_msg("hi there"),
            _tool_result_msg("tc1", "saw a cat", "IMG1"),
            _tool_result_msg("tc2", "saw a dog", "IMG2"),
            _tool_result_msg("tc3", "saw a bird", "IMG3"),
            _tool_result_msg("tc4", "saw a fish", "IMG4"),
        ]
        result = AnthropicBackend.compact_images(messages, keep_last=3)
        # User and assistant messages unchanged
        assert result[0] == _user_msg("hello")
        assert result[1] == _assistant_msg("hi there")


class TestCompactImagesAppliedInStreamTurn:
    """compact_images() is actually called inside stream_turn()."""

    @pytest.mark.asyncio
    async def test_stream_turn_compacts_old_images(self):
        """stream_turn passes compacted messages (old images removed) to the API."""
        from unittest.mock import AsyncMock, MagicMock
        from unittest.mock import patch

        from familiar_agent.backend import AnthropicBackend

        with patch("anthropic.AsyncAnthropic"):
            backend = AnthropicBackend.__new__(AnthropicBackend)
            backend.client = MagicMock()
            backend.model = "claude-haiku-4-5-20251001"  # simple: no thinking
            backend.thinking_mode = "disabled"
            backend.thinking_budget = 10000
            backend.thinking_effort = "high"

        block = MagicMock()
        block.type = "text"
        block.text = "done"
        final_message = MagicMock()
        final_message.stop_reason = "end_turn"
        final_message.content = [block]

        stream_cm = MagicMock()
        stream_cm.__aenter__ = AsyncMock(return_value=stream_cm)
        stream_cm.__aexit__ = AsyncMock(return_value=False)

        async def _text_stream():
            yield "done"

        stream_cm.text_stream = _text_stream()
        stream_cm.get_final_message = AsyncMock(return_value=final_message)

        captured_messages: list = []

        def capture(**kwargs):
            captured_messages.extend(kwargs.get("messages", []))
            return stream_cm

        backend.client.messages.stream = MagicMock(side_effect=capture)

        # Build messages with 4 tool results containing images (keep_last=3 → first cleared)
        tool_msgs = []
        for i in range(4):
            tool_msgs.append(_tool_result_msg(f"tc{i}", f"image {i}", f"BASE64_{i}"))

        await backend.stream_turn(
            system="sys",
            messages=tool_msgs,
            tools=[],
            max_tokens=512,
            on_text=None,
        )

        # The first tool result should have had its image cleared
        first_msg = captured_messages[0]
        content = first_msg["content"][0]["content"]
        assert not any(isinstance(s, dict) and s.get("type") == "image" for s in content)
