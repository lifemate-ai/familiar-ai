"""Provider-neutral model backend protocol."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class ToolCall:
    """A normalized model tool-call request."""

    id: str
    name: str
    input: dict[str, Any]


@dataclass(slots=True)
class ModelTurnResult:
    """A normalized model turn result."""

    stop_reason: str
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    raw: Any = None


class ModelBackend(Protocol):
    """Protocol implemented by provider-specific model adapters."""

    def make_user_message(self, content: str | list[Any]) -> dict[str, Any]:
        """Serialize a user message for this provider."""

    def make_assistant_message(
        self,
        result: ModelTurnResult,
        raw_content: Any | None = None,
    ) -> dict[str, Any]:
        """Serialize an assistant message for this provider."""

    def make_tool_results(
        self,
        tool_calls: Sequence[ToolCall],
        results: Sequence[tuple[str, str | None]],
    ) -> list[dict[str, Any]]:
        """Serialize tool results for this provider."""

    async def stream_turn(
        self,
        *,
        system: str | tuple[str, str],
        messages: list[Any],
        tools: list[dict[str, Any]],
        max_tokens: int,
        on_text: Callable[[str], None] | None,
    ) -> tuple[ModelTurnResult, Any]:
        """Run one streaming model turn and return normalized result plus raw content."""

    async def complete(self, prompt: str, max_tokens: int) -> str:
        """Run a non-streaming utility completion."""
