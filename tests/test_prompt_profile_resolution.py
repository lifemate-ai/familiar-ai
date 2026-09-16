"""PROMPT_PROFILE=auto and SOCIAL_REFLEX resolution."""

from __future__ import annotations

from familiar_agent.prompt_profiles import reflex_enabled, resolve_profile


def test_auto_picks_compact_for_local_platforms() -> None:
    assert resolve_profile("ollama") == "compact"
    assert resolve_profile("cli") == "compact"
    assert resolve_profile("openai", "http://localhost:11434/v1") == "compact"
    assert resolve_profile("openai", "https://api.openai.com/v1") == "full"
    assert resolve_profile("anthropic") == "full"
    assert resolve_profile("kimi", explicit="auto") == "full"


def test_explicit_profile_wins() -> None:
    assert resolve_profile("ollama", explicit="full") == "full"
    assert resolve_profile("anthropic", explicit="compact") == "compact"
    assert resolve_profile("anthropic", explicit="nonsense") == "full"


def test_reflex_enabled_follows_profile_unless_forced() -> None:
    assert reflex_enabled("auto", "compact") is True
    assert reflex_enabled("auto", "full") is False
    assert reflex_enabled("on", "full") is True
    assert reflex_enabled("off", "compact") is False
