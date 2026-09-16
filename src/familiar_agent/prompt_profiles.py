"""Prompt profile selection.

``full``    — the neighbour S-expression prompt (frontier models).
``compact`` — the trimmed template in ``familiar_neighbor/prompts/embodied_compact.md``
              for ~9B local models.
``auto``    — compact for local platforms (ollama, cli, local OpenAI-compatible
              URLs), full otherwise.

Set with ``PROMPT_PROFILE``.
"""

from __future__ import annotations

LOCAL_PLATFORMS = frozenset({"ollama", "cli"})


def resolve_profile(platform: str, base_url: str = "", explicit: str | None = None) -> str:
    """Return ``"full"`` or ``"compact"`` for this configuration."""
    choice = (explicit or "auto").strip().lower()
    if choice in ("full", "compact"):
        return choice
    if platform in LOCAL_PLATFORMS:
        return "compact"
    if platform == "openai" and "api.openai.com" not in (base_url or ""):
        return "compact"
    return "full"


def reflex_enabled(setting: str, profile: str) -> bool:
    """``SOCIAL_REFLEX``: on | off | auto (auto → on when the profile is compact)."""
    choice = (setting or "auto").strip().lower()
    if choice in ("1", "on", "true", "yes"):
        return True
    if choice in ("0", "off", "false", "no"):
        return False
    return profile == "compact"
