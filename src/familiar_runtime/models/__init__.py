"""Model backend interfaces and provider adapters for the generic runtime."""

from ._shared import (
    _ADAPTIVE_THINKING_MODELS,
    _build_tools_system,
    _parse_tool_calls_from_text,
    _supports_adaptive_thinking,
    _TOOL_CALL_RE,
    _TOOLS_PROMPT_HEADER,
)
from .anthropic import AnthropicBackend
from .base import ModelBackend, ModelTurnResult, ToolCall
from .cli import CLIBackend
from .gemini import GeminiBackend
from .glm import GLMBackend
from .kimi import KimiBackend
from .openai_compat import OpenAICompatibleBackend

__all__ = [
    # protocol + dataclasses
    "ModelBackend",
    "ModelTurnResult",
    "ToolCall",
    # providers
    "AnthropicBackend",
    "OpenAICompatibleBackend",
    "KimiBackend",
    "GLMBackend",
    "GeminiBackend",
    "CLIBackend",
    # private helpers re-exported for legacy tests
    "_ADAPTIVE_THINKING_MODELS",
    "_TOOL_CALL_RE",
    "_TOOLS_PROMPT_HEADER",
    "_build_tools_system",
    "_parse_tool_calls_from_text",
    "_supports_adaptive_thinking",
]
