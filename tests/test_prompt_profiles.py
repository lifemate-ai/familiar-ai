"""Tests for prompt profile selection and the compact prompt."""

from __future__ import annotations

from unittest.mock import MagicMock

from familiar_agent.prompt_profiles import compact_prompt, resolve_profile


def test_resolve_profile_auto_picks_compact_for_local_platforms(monkeypatch) -> None:
    monkeypatch.delenv("PROMPT_PROFILE", raising=False)
    assert resolve_profile("ollama") == "compact"
    assert resolve_profile("cli") == "compact"
    assert resolve_profile("openai", "http://localhost:11434/v1") == "compact"
    assert resolve_profile("openai", "https://api.openai.com/v1") == "full"
    assert resolve_profile("anthropic") == "full"
    assert resolve_profile("gemini") == "full"


def test_resolve_profile_explicit_overrides(monkeypatch) -> None:
    monkeypatch.setenv("PROMPT_PROFILE", "full")
    assert resolve_profile("ollama") == "full"
    monkeypatch.setenv("PROMPT_PROFILE", "compact")
    assert resolve_profile("anthropic") == "compact"
    assert resolve_profile("anthropic", explicit="full") == "full"


def test_compact_prompt_embeds_body_and_is_short() -> None:
    text = compact_prompt("- 目：see()\n- 足：なし")
    assert "- 目：see()" in text and "- 足：なし" in text
    assert "say()" in text
    # Roughly 1/5 of the S-expression prompt; small models need headroom for memory context.
    assert len(text) < 2500


def test_agent_system_prompt_uses_compact_profile() -> None:
    from familiar_agent.agent import SYSTEM_PROMPT, EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._me_md = "# ME\n関西弁で話す。"
    agent._prompt_profile = "compact"
    agent._camera = None
    agent._mobility = None
    agent._started_at = 0.0
    agent._turn_count = 0
    agent._self_state = None
    agent._relationship = MagicMock(context_for_prompt=MagicMock(return_value=""))
    agent._exploration = MagicMock(context_for_prompt=MagicMock(return_value=""))
    agent._scene = None
    agent._mood = "neutral"
    agent._mood_intensity = 0.0
    agent._mood_set_at = 0.0
    stable, variable = agent._system_prompt()
    assert stable.startswith("# ME")
    assert "(constraint" not in stable  # S-expression rules are gone
    assert "Neck: fixed" in stable and "Legs: none" in stable
    assert "(interoception" in variable
    assert len(stable) < len(SYSTEM_PROMPT) / 3
