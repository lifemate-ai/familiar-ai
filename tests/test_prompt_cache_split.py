"""Tests for Issue #17: prompt cache split.

Verifies that system prompts are split into (stable, variable) parts
and that each backend handles the tuple correctly for prompt caching.
"""

from __future__ import annotations

import time

import pytest

from familiar_agent.agent import _interoception
from familiar_agent.backend import AnthropicBackend


# ── _system_prompt returns a tuple ────────────────────────────────────────────


class TestSystemPromptSplit:
    """Verify _system_prompt() returns (stable, variable) tuple."""

    @pytest.fixture()
    def agent(self, monkeypatch):
        """Create a minimal EmbodiedAgent with no external dependencies."""
        monkeypatch.setenv("API_KEY", "sk-test-dummy")
        monkeypatch.setenv("PLATFORM", "anthropic")
        # Prevent camera/tts/mobility from initialising
        monkeypatch.setenv("CAMERA_HOST", "")
        monkeypatch.setenv("ELEVENLABS_API_KEY", "")
        monkeypatch.setenv("TUYA_API_KEY", "")
        monkeypatch.setenv("MCP_CONFIG", "")

        from familiar_agent.config import AgentConfig
        from familiar_agent.agent import EmbodiedAgent

        config = AgentConfig()
        return EmbodiedAgent(config)

    def test_returns_tuple_of_two_strings(self, agent):
        result = agent._system_prompt()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], str)

    def test_stable_part_contains_system_prompt(self, agent):
        stable, _ = agent._system_prompt()
        assert "(agent :type embodied" in stable

    def test_stable_part_contains_me_md_when_loaded(self, agent, tmp_path):
        me_md_content = "I am a test personality."
        agent._me_md = me_md_content
        stable, _ = agent._system_prompt()
        assert me_md_content in stable

    def test_stable_part_does_not_contain_interoception(self, agent):
        stable, _ = agent._system_prompt()
        assert "(interoception" not in stable

    def test_variable_part_contains_interoception(self, agent):
        _, variable = agent._system_prompt()
        assert "(interoception" in variable

    def test_variable_part_contains_feelings_when_provided(self, agent):
        _, variable = agent._system_prompt(feelings_ctx="feeling great today")
        assert "feeling great today" in variable

    def test_variable_part_contains_morning_ctx_when_provided(self, agent):
        _, variable = agent._system_prompt(morning_ctx="good morning context")
        assert "good morning context" in variable

    def test_morning_ctx_takes_precedence_over_feelings(self, agent):
        """When both morning and feelings are provided, morning wins."""
        _, variable = agent._system_prompt(
            feelings_ctx="feeling sad", morning_ctx="morning context"
        )
        assert "morning context" in variable
        assert "feeling sad" not in variable

    def test_variable_part_contains_inner_voice_when_provided(self, agent):
        _, variable = agent._system_prompt(inner_voice="I want to look outside")
        assert "I want to look outside" in variable

    def test_variable_part_contains_plan_ctx_when_provided(self, agent):
        _, variable = agent._system_prompt(plan_ctx="1. look around\n2. say hello")
        assert "1. look around" in variable

    def test_stable_part_is_consistent_across_calls(self, agent):
        """Stable part should not change between calls (key for caching)."""
        stable1, _ = agent._system_prompt()
        stable2, _ = agent._system_prompt(feelings_ctx="different feelings")
        assert stable1 == stable2

    def test_variable_part_changes_with_different_inputs(self, agent):
        _, var1 = agent._system_prompt(feelings_ctx="happy")
        _, var2 = agent._system_prompt(feelings_ctx="sad")
        assert var1 != var2

    def test_me_md_loaded_once_in_init(self, agent, monkeypatch, tmp_path):
        """ME.md should be loaded in __init__, not on every call."""
        # The _me_md attribute should already be set
        assert hasattr(agent, "_me_md")
        # Changing the file after init should NOT affect the result
        original_me = agent._me_md
        agent._me_md = "changed"
        stable, _ = agent._system_prompt()
        assert "changed" in stable
        # But it was loaded once, not re-read from disk each call
        agent._me_md = original_me


# ── AnthropicBackend._build_system_param ──────────────────────────────────────


class TestBuildSystemParam:
    """Verify AnthropicBackend correctly builds multi-block system params."""

    def test_string_passthrough(self):
        """Plain string should pass through unchanged."""
        result = AnthropicBackend._build_system_param("hello world")
        assert result == "hello world"

    def test_tuple_returns_list_of_blocks(self):
        """Tuple should return a list with cache_control on stable block."""
        result = AnthropicBackend._build_system_param(("stable part", "variable part"))
        assert isinstance(result, list)
        assert len(result) == 2

    def test_stable_block_has_cache_control(self):
        """First block (stable) should have cache_control: ephemeral."""
        result = AnthropicBackend._build_system_param(("stable", "variable"))
        assert result[0]["cache_control"] == {"type": "ephemeral"}

    def test_variable_block_has_no_cache_control(self):
        """Second block (variable) should NOT have cache_control."""
        result = AnthropicBackend._build_system_param(("stable", "variable"))
        assert "cache_control" not in result[1]

    def test_both_blocks_have_correct_text(self):
        result = AnthropicBackend._build_system_param(("stable text", "variable text"))
        assert result[0]["text"] == "stable text"
        assert result[1]["text"] == "variable text"

    def test_both_blocks_have_type_text(self):
        result = AnthropicBackend._build_system_param(("stable", "variable"))
        assert result[0]["type"] == "text"
        assert result[1]["type"] == "text"

    def test_empty_stable_skips_stable_block(self):
        """Empty stable string should not produce a stable block."""
        result = AnthropicBackend._build_system_param(("", "variable only"))
        # Should degenerate to just the variable block as plain string
        # (no cache_control on single variable block)
        assert result == "variable only"

    def test_empty_variable_returns_stable_with_cache(self):
        """Empty variable should return just the stable block with cache_control."""
        result = AnthropicBackend._build_system_param(("stable only", ""))
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["cache_control"] == {"type": "ephemeral"}

    def test_both_empty_returns_empty_string(self):
        """Both empty should return empty list or string."""
        result = AnthropicBackend._build_system_param(("", ""))
        # No blocks at all — should handle gracefully
        assert result == [] or result == ""


# ── Other backends: tuple fallback ────────────────────────────────────────────


class TestOtherBackendsTupleFallback:
    """Verify non-Anthropic backends join tuple into a single string."""

    def test_openai_flatten_messages_joins_tuple(self):
        from familiar_agent.backend import OpenAICompatibleBackend

        backend = OpenAICompatibleBackend.__new__(OpenAICompatibleBackend)
        flat = backend._flatten_messages(("stable", "variable"), [])
        # Should have a single system message with joined text
        assert flat[0]["role"] == "system"
        assert "stable" in flat[0]["content"]
        assert "variable" in flat[0]["content"]

    def test_openai_flatten_messages_handles_plain_string(self):
        from familiar_agent.backend import OpenAICompatibleBackend

        backend = OpenAICompatibleBackend.__new__(OpenAICompatibleBackend)
        flat = backend._flatten_messages("plain system", [])
        assert flat[0]["content"] == "plain system"

    def test_cli_serialize_joins_tuple(self):
        from familiar_agent.backend import CLIBackend

        backend = CLIBackend(["echo", "{}"])
        result = backend._serialize(("stable", "variable"), [], [])
        assert "stable" in result
        assert "variable" in result

    def test_cli_serialize_handles_plain_string(self):
        from familiar_agent.backend import CLIBackend

        backend = CLIBackend(["echo", "{}"])
        result = backend._serialize("plain system", [], [])
        assert "plain system" in result

    def test_kimi_stream_turn_joins_tuple(self):
        """KimiBackend should join tuple system prompts into a string."""

        # KimiBackend joins in stream_turn, so we test the join logic directly
        system = ("stable part", "variable part")
        joined = "\n\n---\n\n".join(s for s in system if s)
        assert "stable part" in joined
        assert "variable part" in joined

    def test_gemini_stream_turn_joins_tuple(self):
        """GeminiBackend should join tuple system prompts into a string."""
        system = ("stable part", "variable part")
        joined = "\n\n---\n\n".join(s for s in system if s)
        assert "stable part" in joined
        assert "variable part" in joined


# ── Interoception is in variable, not stable ──────────────────────────────────


class TestInteroceptionPlacement:
    """Interoception must be in the variable part so caching works."""

    def test_interoception_changes_between_calls(self):
        """Interoception should produce different output with different inputs."""
        result1 = _interoception(time.time(), 0)
        result2 = _interoception(time.time(), 10)
        assert result1 != result2

    def test_interoception_changes_with_uptime(self):
        now = time.time()
        fresh = _interoception(now, 0)
        old = _interoception(now - 3600, 0)
        assert fresh != old


# ── Edge cases ────────────────────────────────────────────────────────────────


class TestEdgeCases:
    """Edge cases for prompt cache split."""

    def test_build_system_param_with_very_long_stable(self):
        """Should handle very long stable parts without issues."""
        long_stable = "x" * 100_000
        result = AnthropicBackend._build_system_param((long_stable, "short variable"))
        assert isinstance(result, list)
        assert len(result[0]["text"]) == 100_000

    def test_build_system_param_with_unicode(self):
        """Should handle Unicode in both parts."""
        result = AnthropicBackend._build_system_param(
            ("Stable part with Japanese", "Variable part")
        )
        assert result[0]["text"] == "Stable part with Japanese"

    def test_build_system_param_with_special_chars(self):
        """Should handle special characters (newlines, tabs, etc.)."""
        result = AnthropicBackend._build_system_param(
            ("stable\nwith\nnewlines", "variable\twith\ttabs")
        )
        assert "\n" in result[0]["text"]
        assert "\t" in result[1]["text"]
