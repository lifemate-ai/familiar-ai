"""LLM backend abstraction — re-exports provider adapters from familiar_runtime.models.

The provider implementations live in :mod:`familiar_runtime.models`.  This module
keeps the historical ``familiar_agent.backend`` import surface (used widely by
tests and other callers) and hosts the configuration-driven factory functions.
"""

from __future__ import annotations

import logging
import os
import shlex
from typing import TYPE_CHECKING

from familiar_runtime.models import (
    _ADAPTIVE_THINKING_MODELS,
    _build_tools_system,
    _parse_tool_calls_from_text,
    _supports_adaptive_thinking,
    _TOOL_CALL_RE,
    _TOOLS_PROMPT_HEADER,
    AnthropicBackend,
    CLIBackend,
    GeminiBackend,
    GLMBackend,
    KimiBackend,
    ModelTurnResult,
    OpenAICompatibleBackend,
    ToolCall,
)

if TYPE_CHECKING:
    from .config import AgentConfig

# Legacy alias used widely across tests and post-PR-167 code.
TurnResult = ModelTurnResult

logger = logging.getLogger(__name__)

__all__ = [
    # protocol / dataclass aliases
    "ModelTurnResult",
    "TurnResult",
    "ToolCall",
    # provider adapters
    "AnthropicBackend",
    "OpenAICompatibleBackend",
    "KimiBackend",
    "GLMBackend",
    "GeminiBackend",
    "CLIBackend",
    # helpers exposed for legacy callers / tests
    "_ADAPTIVE_THINKING_MODELS",
    "_TOOL_CALL_RE",
    "_TOOLS_PROMPT_HEADER",
    "_build_tools_system",
    "_parse_tool_calls_from_text",
    "_supports_adaptive_thinking",
    # factories
    "create_backend",
    "create_utility_backend",
    "create_inner_backend",
    "create_scene_backend",
]


def create_backend(
    config: AgentConfig,
) -> (
    AnthropicBackend
    | OpenAICompatibleBackend
    | KimiBackend
    | GLMBackend
    | GeminiBackend
    | CLIBackend
):
    """Factory: pick backend based on PLATFORM env var / config.

    Supported values for PLATFORM:
      anthropic  — Anthropic Claude (default)
      gemini     — Google Gemini via native google-genai SDK
      openai     — OpenAI API (or compatible via BASE_URL)
      kimi       — Moonshot AI Kimi K2.5 (api.moonshot.ai/v1)
      glm        — Z.AI GLM API (api.z.ai/api/paas/v4); set ZAI_API_KEY
      cli        — any CLI LLM tool via stdin/stdout (MODEL = the command)
                   e.g. MODEL="claude -p"  or  MODEL="ollama run gemma3:27b"
    """
    if config.platform == "gemini":
        model = config.model or "gemini-2.5-flash"
        logger.info("Using Gemini backend: %s", model)
        return GeminiBackend(api_key=config.api_key, model=model)
    if config.platform == "openai":
        model = config.model or "gpt-4o-mini"
        base_url = config.base_url
        if not os.environ.get("BASE_URL"):
            base_url = "https://api.openai.com/v1"
        is_real_openai = "api.openai.com" in base_url
        tools_mode = (
            config.tools_mode
            if os.environ.get("TOOLS_MODE")
            else ("native" if is_real_openai else "prompt")
        )
        logger.info(
            "Using OpenAI backend: %s @ %s (tools=%s)",
            model,
            base_url,
            tools_mode,
        )
        return OpenAICompatibleBackend(
            api_key=config.api_key,
            model=model,
            base_url=base_url,
            tools_mode=tools_mode,
        )
    if config.platform == "kimi":
        model = config.model or "kimi-k2.5"
        logger.info("Using Kimi backend: %s", model)
        return KimiBackend(api_key=config.api_key, model=model)
    if config.platform == "glm":
        model = config.model or "glm-4.6v"
        logger.info("Using GLM backend: %s", model)
        return GLMBackend(api_key=config.api_key, model=model)
    if config.platform == "cli":
        raw_cmd = config.model.strip() if config.model else "claude -p {}"
        cmd = shlex.split(raw_cmd)
        logger.info("Using CLI backend: %s", " ".join(cmd))
        return CLIBackend(cmd)
    model = config.model or "claude-haiku-4-5-20251001"
    logger.info("Using Anthropic backend: %s", model)
    return AnthropicBackend(
        api_key=config.api_key,
        model=model,
        thinking_mode=config.thinking_mode,
        thinking_budget=config.thinking_budget,
        thinking_effort=config.thinking_effort,
    )


def create_utility_backend(
    config: AgentConfig,
) -> AnthropicBackend | OpenAICompatibleBackend | KimiBackend | GLMBackend | GeminiBackend | None:
    """Create a separate backend for utility LLM calls (summaries, emotion, etc.).

    Returns None if UTILITY_PLATFORM is not configured — caller should
    fall back to the main conversation backend.
    """
    if not config.utility_platform or not config.utility_api_key:
        return None

    platform = config.utility_platform
    api_key = config.utility_api_key
    model = config.utility_model

    if platform == "anthropic":
        model = model or "claude-haiku-4-5-20251001"
        logger.info("Using Anthropic utility backend: %s", model)
        return AnthropicBackend(api_key=api_key, model=model, thinking_mode="disabled")
    if platform == "gemini":
        model = model or "gemini-2.5-flash"
        logger.info("Using Gemini utility backend: %s", model)
        return GeminiBackend(api_key=api_key, model=model)
    if platform == "kimi":
        model = model or "kimi-k2.5"
        logger.info("Using Kimi utility backend: %s", model)
        return KimiBackend(api_key=api_key, model=model)
    if platform == "glm":
        model = model or "glm-4.6v"
        logger.info("Using GLM utility backend: %s", model)
        return GLMBackend(api_key=api_key, model=model)
    if platform == "openai":
        model = model or "gpt-4o-mini"
        logger.info("Using OpenAI utility backend: %s", model)
        return OpenAICompatibleBackend(
            api_key=api_key, model=model, base_url="https://api.openai.com/v1"
        )

    logger.warning("Unknown UTILITY_PLATFORM: %s, falling back to main backend", platform)
    return None


def create_inner_backend(
    config: AgentConfig,
) -> AnthropicBackend | OpenAICompatibleBackend | KimiBackend | GLMBackend | GeminiBackend | None:
    """Create a separate backend for inner-loop micro-thoughts.

    One short completion per crystallized idle thought — the natural fit is a
    small LOCAL model, so unlike the utility factory the openai path honors
    INNER_BASE_URL (default: local Ollama) and needs no API key. Returns None
    when INNER_PLATFORM is unset; the agent then falls back to the utility
    backend only if it is separate from the main model (cost philosophy:
    idle cycles must never burn main-model calls).
    """
    if not config.inner_platform:
        return None

    platform = config.inner_platform
    api_key = config.inner_api_key
    model = config.inner_model

    if platform == "openai":
        if not model:
            logger.warning("INNER_PLATFORM=openai needs INNER_MODEL; micro-thoughts disabled")
            return None
        base_url = config.inner_base_url or "http://localhost:11434/v1"
        logger.info("Using OpenAI-compatible inner backend: %s @ %s", model, base_url)
        return OpenAICompatibleBackend(
            api_key=api_key or "local",
            model=model,
            base_url=base_url,
            tools_mode="prompt",
        )
    if not api_key:
        logger.warning("INNER_PLATFORM=%s needs INNER_API_KEY; micro-thoughts disabled", platform)
        return None
    if platform == "anthropic":
        model = model or "claude-haiku-4-5-20251001"
        logger.info("Using Anthropic inner backend: %s", model)
        return AnthropicBackend(api_key=api_key, model=model, thinking_mode="disabled")
    if platform == "gemini":
        model = model or "gemini-2.5-flash"
        logger.info("Using Gemini inner backend: %s", model)
        return GeminiBackend(api_key=api_key, model=model)
    if platform == "kimi":
        model = model or "kimi-k2.5"
        logger.info("Using Kimi inner backend: %s", model)
        return KimiBackend(api_key=api_key, model=model)
    if platform == "glm":
        model = model or "glm-4.6v"
        logger.info("Using GLM inner backend: %s", model)
        return GLMBackend(api_key=api_key, model=model)

    logger.warning("Unknown INNER_PLATFORM: %s; micro-thoughts disabled", platform)
    return None


def create_scene_backend(
    config: AgentConfig,
) -> AnthropicBackend | OpenAICompatibleBackend | KimiBackend | GLMBackend | GeminiBackend | None:
    """Create a separate backend for scene entity extraction (cheap/local model).

    Returns None if SCENE_PLATFORM is not configured — caller should fall back
    to the utility backend or main backend.
    """
    if not config.scene_platform or not config.scene_api_key:
        return None

    platform = config.scene_platform
    api_key = config.scene_api_key
    model = config.scene_model

    if platform == "anthropic":
        model = model or "claude-haiku-4-5-20251001"
        logger.info("Using Anthropic scene backend: %s", model)
        return AnthropicBackend(api_key=api_key, model=model, thinking_mode="disabled")
    if platform == "gemini":
        model = model or "gemini-2.5-flash"
        logger.info("Using Gemini scene backend: %s", model)
        return GeminiBackend(api_key=api_key, model=model)
    if platform == "kimi":
        model = model or "kimi-k2.5"
        logger.info("Using Kimi scene backend: %s", model)
        return KimiBackend(api_key=api_key, model=model)
    if platform == "glm":
        model = model or "glm-4.6v"
        logger.info("Using GLM scene backend: %s", model)
        return GLMBackend(api_key=api_key, model=model)
    if platform == "openai":
        model = model or "gpt-4o-mini"
        logger.info("Using OpenAI scene backend: %s", model)
        return OpenAICompatibleBackend(
            api_key=api_key, model=model, base_url="https://api.openai.com/v1"
        )

    logger.warning("Unknown SCENE_PLATFORM: %s, falling back", platform)
    return None
