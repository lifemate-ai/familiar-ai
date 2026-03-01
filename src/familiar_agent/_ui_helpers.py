"""Shared UI utilities for TUI, GUI, and REPL.

This module is the single source of truth for:
  - ACTION_ICONS: icon mapping for tool calls
  - format_action(): human-readable tool-call label
  - desire_tick_prompt(): extract the current dominant desire prompt (UI-agnostic)

Keeping these here prevents duplication across tui.py, gui.py, and main.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._i18n import _t

if TYPE_CHECKING:
    from .desires import DesireSystem


# ---------------------------------------------------------------------------
# Action icons (single source of truth)
# ---------------------------------------------------------------------------

ACTION_ICONS: dict[str, str] = {
    "see": "👀",
    "look": "🔄",
    "look_left": "◀️",
    "look_right": "▶️",
    "look_up": "🔼",
    "look_down": "🔽",
    "look_around": "🔄",
    "walk": "🚶",
    "say": "🗣️",
    "remember": "💾",
    "recall": "💭",
    "listen": "🎙️",
    "search": "🔍",
}

# Tool names that have dedicated i18n labels (key: "action_{name}")
_I18N_ACTION_NAMES: frozenset[str] = frozenset({"see", "look", "walk", "say", "remember", "recall"})


def format_action(name: str, tool_input: dict) -> str:
    """Return a human-readable label for a tool call.

    Used identically by TUI, GUI, and REPL to display tool invocations.
    """
    icon = ACTION_ICONS.get(name, "⚙")

    if name == "look":
        direction = tool_input.get("direction", "")
        key = {
            "left": "look_left",
            "right": "look_right",
            "up": "look_up",
            "down": "look_down",
        }.get(direction, "look_around")
        dir_icon = ACTION_ICONS.get(key, icon)
        deg = tool_input.get("degrees", "")
        suffix = f"({deg}°)" if deg else ""
        return f"{dir_icon} {_t(key)}{suffix}"

    if name == "walk":
        direction = tool_input.get("direction", "?")
        duration = tool_input.get("duration")
        if duration:
            return f"{icon} {_t('walk_timed', direction=direction, duration=str(duration))}"
        return f"{icon} {_t('walk_dir', direction=direction)}"

    if name == "say":
        raw = str(tool_input.get("text", ""))
        preview = raw[:50]
        ellipsis = "…" if len(raw) > 50 else ""
        return f"{icon} 「{preview}{ellipsis}」"

    if name in _I18N_ACTION_NAMES:
        try:
            return _t(f"action_{name}")
        except KeyError:
            pass

    return f"{icon} {name}"


# ---------------------------------------------------------------------------
# Desire tick (UI-agnostic core)
# ---------------------------------------------------------------------------

IDLE_CHECK_INTERVAL: float = 10.0  # seconds between desire checks when idle
DESIRE_COOLDOWN: float = 90.0  # seconds after last user interaction before desires fire


def desire_tick_prompt(
    desires: DesireSystem,
    input_queue_peek: list[str],
) -> tuple[str, str, str | None] | None:
    """Return (desire_name, prompt, pending_note) or None if no desire fires.

    Args:
        desires: the DesireSystem to query.
        input_queue_peek: list of items currently in the input queue
            (caller drains it and passes the contents here so this
            function can fold any pending user note into the prompt
            without touching the queue itself).

    Returns:
        (desire_name, prompt, pending_note) if a desire is ready to fire.
        None if no dominant desire exists or prompt is empty.
    """
    prompt = desires.dominant_as_prompt()
    if not prompt:
        return None

    dominant = desires.get_dominant()
    if dominant is None:
        return None

    desire_name, _ = dominant

    pending_note: str | None = None
    if input_queue_peek:
        pending_note = input_queue_peek[0]
        prompt = f"（{pending_note}と言ってた）{prompt}"

    return desire_name, prompt, pending_note
