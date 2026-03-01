"""Tests for the TUI slash-command autocomplete candidates function.

The _slash_candidates function is the core of the autocomplete feature. It
receives a TargetState (the current text + cursor position in the Input widget)
and returns a list of DropdownItems that should appear in the dropdown.

Key invariants:
1. Returns empty list when text does NOT start with "/"
2. Returns all commands when text is exactly "/"
3. Filters by prefix when text is e.g. "/t" → only "/transcribe"
4. Each DropdownItem.value MUST equal the command name (so completion inserts
   only the command, not the description)
5. cursor_position is respected (text is sliced to cursor)
"""

from __future__ import annotations

from textual_autocomplete import TargetState

from familiar_agent.tui import _SLASH_COMMANDS, _slash_candidates


def _state(text: str, cursor: int | None = None) -> TargetState:
    """Build a TargetState with cursor defaulting to end-of-text."""
    return TargetState(text=text, cursor_position=len(text) if cursor is None else cursor)


# ── no-op cases ────────────────────────────────────────────────────────────────


def test_empty_input_returns_nothing() -> None:
    assert _slash_candidates(_state("")) == []


def test_plain_text_returns_nothing() -> None:
    assert _slash_candidates(_state("hello")) == []


def test_non_slash_prefix_returns_nothing() -> None:
    assert _slash_candidates(_state("clear")) == []
    assert _slash_candidates(_state(" /clear")) == []


# ── slash triggers ────────────────────────────────────────────────────────────


def test_bare_slash_returns_all_commands() -> None:
    items = _slash_candidates(_state("/"))
    cmd_values = [item.value for item in items]
    expected = [cmd for cmd, _desc in _SLASH_COMMANDS]
    assert cmd_values == expected


def test_slash_transcribe_prefix_filters() -> None:
    items = _slash_candidates(_state("/t"))
    assert len(items) == 1
    assert items[0].value == "/transcribe"


def test_slash_clear_prefix_filters() -> None:
    items = _slash_candidates(_state("/cl"))
    assert len(items) == 1
    assert items[0].value == "/clear"


def test_slash_quit_prefix_filters() -> None:
    items = _slash_candidates(_state("/q"))
    assert len(items) == 1
    assert items[0].value == "/quit"


def test_full_command_name_still_shows_dropdown() -> None:
    """Typing the full command name should still return that command."""
    items = _slash_candidates(_state("/transcribe"))
    assert len(items) == 1
    assert items[0].value == "/transcribe"


def test_unknown_command_returns_nothing() -> None:
    items = _slash_candidates(_state("/unknown"))
    assert items == []


# ── completion value correctness (CRITICAL) ───────────────────────────────────


def test_completion_value_is_only_command_not_description() -> None:
    """DropdownItem.value must be the bare command (e.g. '/clear'), not the
    description text.  This ensures that selecting from the dropdown inserts
    only the command into the input widget."""
    items = _slash_candidates(_state("/"))
    for item in items:
        # value must be a known command
        assert item.value in {cmd for cmd, _desc in _SLASH_COMMANDS}, (
            f"Expected value to be a command name, got {item.value!r}"
        )
        # value must NOT contain any description text
        all_descs = {desc for _cmd, desc in _SLASH_COMMANDS}
        for desc in all_descs:
            assert desc not in item.value, (
                f"Description {desc!r} leaked into completion value {item.value!r}"
            )


def test_each_command_has_correct_value() -> None:
    """Each returned item's .value matches exactly the command it represents."""
    for cmd, _desc in _SLASH_COMMANDS:
        items = _slash_candidates(_state(cmd))
        assert len(items) == 1, f"Expected 1 item for {cmd!r}, got {len(items)}"
        assert items[0].value == cmd, f"item.value={items[0].value!r} != {cmd!r}"


# ── cursor-position awareness ─────────────────────────────────────────────────


def test_cursor_at_start_does_not_trigger_slash() -> None:
    """Text='/transcribe' but cursor at 0 → no '/' before cursor → no matches."""
    # cursor_position=0 means the text before cursor is "", which doesn't start
    # with "/", so the function should return empty.
    items = _slash_candidates(_state("/transcribe", cursor=0))
    assert items == []


def test_cursor_mid_slash_command() -> None:
    """Text='/transcribe' with cursor at 2 ('/t') → only /transcribe matches."""
    items = _slash_candidates(_state("/transcribe", cursor=2))
    assert len(items) == 1
    assert items[0].value == "/transcribe"
