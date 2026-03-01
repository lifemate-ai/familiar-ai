"""Unit tests for _ui_helpers: format_action and desire_tick_prompt.

TDD: tests written to verify the extracted shared helpers work correctly
before updating tui.py / gui.py / main.py to use them.
"""

from __future__ import annotations


from familiar_agent._ui_helpers import (
    ACTION_ICONS,
    desire_tick_prompt,
    format_action,
)


# ---------------------------------------------------------------------------
# format_action tests
# ---------------------------------------------------------------------------


class TestFormatAction:
    def test_see_tool_returns_icon_and_i18n(self):
        result = format_action("see", {})
        assert "👀" in result

    def test_look_left_uses_direction_icon(self):
        result = format_action("look", {"direction": "left"})
        assert "◀️" in result

    def test_look_right_uses_direction_icon(self):
        result = format_action("look", {"direction": "right"})
        assert "▶️" in result

    def test_look_up_uses_direction_icon(self):
        result = format_action("look", {"direction": "up"})
        assert "🔼" in result

    def test_look_down_uses_direction_icon(self):
        result = format_action("look", {"direction": "down"})
        assert "🔽" in result

    def test_look_no_direction_uses_look_around_icon(self):
        result = format_action("look", {})
        assert "🔄" in result

    def test_look_with_degrees(self):
        result = format_action("look", {"direction": "left", "degrees": 90})
        assert "90" in result
        assert "°" in result

    def test_walk_with_direction_and_duration(self):
        result = format_action("walk", {"direction": "forward", "duration": 5})
        assert "🚶" in result
        # Should include duration info
        assert "5" in result

    def test_walk_with_direction_only(self):
        result = format_action("walk", {"direction": "backward"})
        assert "🚶" in result

    def test_say_truncates_long_text(self):
        long_text = "あ" * 100
        result = format_action("say", {"text": long_text})
        assert "🗣️" in result
        assert "…" in result
        # Should not include full text
        assert len(result) < len(long_text)

    def test_say_short_text_no_ellipsis(self):
        result = format_action("say", {"text": "hello"})
        assert "hello" in result
        # No ellipsis for short text
        assert "…" not in result

    def test_unknown_tool_uses_gear_icon(self):
        result = format_action("unknown_tool_xyz", {})
        assert "⚙" in result
        assert "unknown_tool_xyz" in result

    def test_remember_tool(self):
        result = format_action("remember", {})
        assert "💾" in result

    def test_recall_tool(self):
        result = format_action("recall", {})
        assert "💭" in result


class TestActionIcons:
    def test_all_required_tools_have_icons(self):
        required = {"see", "look", "walk", "say", "remember", "recall"}
        for tool in required:
            assert tool in ACTION_ICONS, f"ACTION_ICONS missing entry for '{tool}'"

    def test_icons_are_strings(self):
        for name, icon in ACTION_ICONS.items():
            assert isinstance(icon, str), f"Icon for '{name}' must be a string"
            assert len(icon) > 0, f"Icon for '{name}' must not be empty"


# ---------------------------------------------------------------------------
# desire_tick_prompt tests
# ---------------------------------------------------------------------------


class _FakeDesireSystem:
    """Minimal DesireSystem stub for testing."""

    def __init__(self, dominant: tuple[str, float] | None = None, prompt: str = "") -> None:
        self._dominant = dominant
        self._prompt = prompt

    def dominant_as_prompt(self) -> str:
        return self._prompt

    def get_dominant(self) -> tuple[str, float] | None:
        return self._dominant


class TestDesireTickPrompt:
    def test_returns_none_when_no_prompt(self):
        desires = _FakeDesireSystem(dominant=("look_around", 0.8), prompt="")
        result = desire_tick_prompt(desires, [])
        assert result is None

    def test_returns_none_when_no_dominant(self):
        desires = _FakeDesireSystem(dominant=None, prompt="周りを見たい")
        result = desire_tick_prompt(desires, [])
        assert result is None

    def test_returns_desire_name_prompt_and_none_pending(self):
        desires = _FakeDesireSystem(dominant=("look_around", 0.9), prompt="周りを見たい")
        result = desire_tick_prompt(desires, [])
        assert result is not None
        desire_name, prompt, pending = result
        assert desire_name == "look_around"
        assert prompt == "周りを見たい"
        assert pending is None

    def test_folds_pending_note_into_prompt(self):
        desires = _FakeDesireSystem(dominant=("look_around", 0.9), prompt="周りを見たい")
        result = desire_tick_prompt(desires, ["コウタだよ"])
        assert result is not None
        desire_name, prompt, pending = result
        assert "コウタだよ" in prompt
        assert "周りを見たい" in prompt
        assert pending == "コウタだよ"

    def test_uses_only_first_pending_note(self):
        desires = _FakeDesireSystem(dominant=("explore", 0.7), prompt="探索したい")
        result = desire_tick_prompt(desires, ["first", "second"])
        assert result is not None
        _, prompt, pending = result
        assert pending == "first"
        assert "first" in prompt
        # second should not appear in prompt
        assert "second" not in prompt

    def test_known_desire_names_produce_non_empty_murmur(self):
        known = ["look_around", "explore", "greet_companion", "rest"]
        for name in known:
            desires = _FakeDesireSystem(dominant=(name, 0.8), prompt="やりたいこと")
            result = desire_tick_prompt(desires, [])
            # We just verify it doesn't crash and returns something
            assert result is not None
            desire_name, prompt, _ = result
            assert desire_name == name
            assert prompt == "やりたいこと"

    def test_unknown_desire_name_does_not_crash(self):
        desires = _FakeDesireSystem(dominant=("unknown_desire_xyz", 0.5), prompt="something")
        result = desire_tick_prompt(desires, [])
        assert result is not None
        desire_name, _, _ = result
        assert desire_name == "unknown_desire_xyz"
