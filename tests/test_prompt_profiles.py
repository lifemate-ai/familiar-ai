"""Prompt profiles: a compact framework prompt for small local models.

The full profile stays byte-for-byte stable (pinned separately in
``test_prompt_assembly.py``). The compact profile keeps only the critical
operational constraints — the long-form social/cognitive guidance it drops is
carried by the deterministic mind layers (auto-ToM, social policy, meta-gate,
identity). The voice rule moves to the end: small models weight late
instructions more reliably.
"""

from __future__ import annotations

from familiar_neighbor.prompts import assemble_neighbor_system_prompt


def _full() -> str:
    return assemble_neighbor_system_prompt(max_steps=50)


def _compact() -> str:
    return assemble_neighbor_system_prompt(max_steps=50, profile="compact")


def test_default_profile_is_full():
    assert assemble_neighbor_system_prompt(max_steps=50, profile="full") == _full()


def test_unknown_profile_falls_back_to_full():
    assert assemble_neighbor_system_prompt(max_steps=50, profile="nonsense") == _full()


def test_compact_is_substantially_smaller():
    assert len(_compact()) < 0.45 * len(_full())


def test_compact_keeps_critical_constraints():
    text = _compact()
    for marker in (
        ":id no-retry-loop",
        ":id honesty",
        ":id personality-from-me",
        ":id no-tts-tags",
        ":id speak-every-reply",
        "voice-only-from-say",  # spliced generic voice rule
    ):
        assert marker in text, f"compact profile lost critical constraint {marker!r}"


def test_compact_resolves_all_placeholders():
    text = _compact()
    assert "{react_loop}" not in text
    assert "{voice_rules_generic}" not in text
    assert "{language_match}" not in text
    assert "{tool_rules}" not in text
    assert "{step_budget}" not in text
    assert "{max_steps}" not in text
    assert "50" in text  # step budget materialised


def test_compact_drops_folded_guidance():
    """Guidance now carried by deterministic mind layers must not bloat compact."""
    text = _compact()
    for absent in (
        ":id theory-of-mind",
        ":id validation-before-advice",
        ":id bid-for-connection",
        ":id window-of-tolerance",
        ":id perspective-taking",
    ):
        assert absent not in text


def test_compact_voice_rule_is_near_the_end():
    text = _compact()
    say_pos = text.index("speak-every-reply")
    assert say_pos > 0.7 * len(text)


def test_compact_body_block_matches_full_shape():
    """The hardware body-description regex in agent.py rewrites ``(body ...)``;
    both templates must open the same way so the substitution behaves alike."""
    assert "(body\n" in _compact()
    assert "(body\n" in _full()


def test_config_default_and_env(monkeypatch):
    from familiar_agent.config import AgentConfig

    monkeypatch.delenv("PROMPT_PROFILE", raising=False)
    assert AgentConfig().prompt_profile == "full"
    monkeypatch.setenv("PROMPT_PROFILE", "Compact")
    assert AgentConfig().prompt_profile == "compact"


def test_agent_stable_prompt_uses_compact_profile():
    from tests.test_agent_react_loop import _make_agent

    agent = _make_agent()
    agent.config.prompt_profile = "compact"
    stable, _variable = agent._system_prompt()
    assert ":profile compact" in stable


def test_agent_stable_prompt_defaults_to_full():
    from tests.test_agent_react_loop import _make_agent

    agent = _make_agent()
    stable, _variable = agent._system_prompt()
    assert ":profile compact" not in stable
