"""Tests for Phase 5 two-tier scene backend.

TDD: written before implementation.
Covers create_scene_backend() factory and agent wiring.
"""

from __future__ import annotations

import os
from unittest.mock import patch


from familiar_agent.backend import create_scene_backend
from familiar_agent.config import AgentConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _config_with_scene(
    platform: str = "",
    api_key: str = "",
    model: str = "",
) -> AgentConfig:
    """Build an AgentConfig with scene backend settings injected."""
    config = AgentConfig.__new__(AgentConfig)
    # Minimal required fields
    config.api_key = "main-key"
    config.platform = "anthropic"
    config.model = "claude-haiku-4-5-20251001"
    config.utility_platform = ""
    config.utility_api_key = ""
    config.utility_model = ""
    config.scene_platform = platform
    config.scene_api_key = api_key
    config.scene_model = model
    return config


# ---------------------------------------------------------------------------
# Tests: create_scene_backend()
# ---------------------------------------------------------------------------


def test_create_scene_backend_returns_none_when_not_configured():
    """Returns None when SCENE_PLATFORM / scene_api_key are not set."""
    config = _config_with_scene()
    result = create_scene_backend(config)
    assert result is None


def test_create_scene_backend_returns_none_when_platform_set_but_no_key():
    """Returns None when platform is set but api_key is empty."""
    config = _config_with_scene(platform="anthropic", api_key="")
    result = create_scene_backend(config)
    assert result is None


def test_create_scene_backend_returns_none_when_key_set_but_no_platform():
    """Returns None when api_key is set but platform is empty."""
    config = _config_with_scene(platform="", api_key="sk-test")
    result = create_scene_backend(config)
    assert result is None


def test_create_scene_backend_anthropic():
    """Creates an AnthropicBackend when platform='anthropic'."""
    from familiar_agent.backend import AnthropicBackend

    config = _config_with_scene(platform="anthropic", api_key="sk-test")
    result = create_scene_backend(config)
    assert isinstance(result, AnthropicBackend)


def test_create_scene_backend_anthropic_default_model():
    """Default model for anthropic scene backend is haiku (cheap/fast)."""
    config = _config_with_scene(platform="anthropic", api_key="sk-test", model="")
    result = create_scene_backend(config)
    assert result is not None
    assert "haiku" in result.model.lower()


def test_create_scene_backend_anthropic_custom_model():
    """Custom model is respected when provided."""
    config = _config_with_scene(platform="anthropic", api_key="sk-test", model="claude-sonnet-4-6")
    result = create_scene_backend(config)
    assert result is not None
    assert result.model == "claude-sonnet-4-6"


def test_create_scene_backend_openai():
    """Creates an OpenAICompatibleBackend when platform='openai'."""
    from familiar_agent.backend import OpenAICompatibleBackend

    config = _config_with_scene(platform="openai", api_key="sk-test")
    result = create_scene_backend(config)
    assert isinstance(result, OpenAICompatibleBackend)


def test_create_scene_backend_gemini():
    """Creates a GeminiBackend when platform='gemini'."""
    from familiar_agent.backend import GeminiBackend

    config = _config_with_scene(platform="gemini", api_key="gm-test")
    result = create_scene_backend(config)
    assert isinstance(result, GeminiBackend)


def test_create_scene_backend_unknown_platform_returns_none():
    """Unknown platform name returns None (with a warning)."""
    config = _config_with_scene(platform="nonexistent", api_key="sk-test")
    result = create_scene_backend(config)
    assert result is None


# ---------------------------------------------------------------------------
# Tests: AgentConfig scene fields
# ---------------------------------------------------------------------------


def test_agent_config_scene_platform_defaults_to_empty():
    """AgentConfig.scene_platform defaults to '' (no scene backend)."""
    with patch.dict(os.environ, {}, clear=False):
        # Remove SCENE_PLATFORM if present
        env = {k: v for k, v in os.environ.items() if k != "SCENE_PLATFORM"}
        with patch.dict(os.environ, env, clear=True):
            config = AgentConfig()
    assert config.scene_platform == ""


def test_agent_config_scene_platform_from_env():
    """SCENE_PLATFORM env var is picked up by AgentConfig."""
    with patch.dict(os.environ, {"SCENE_PLATFORM": "gemini", "SCENE_API_KEY": "gm-key"}):
        config = AgentConfig()
    assert config.scene_platform == "gemini"
    assert config.scene_api_key == "gm-key"
