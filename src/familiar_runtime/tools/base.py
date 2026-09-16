"""Generic tool protocol and result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class ToolSpec:
    """Provider-neutral description of a callable tool."""

    name: str
    description: str
    input_schema: dict[str, Any]
    category: str = "generic"
    risk: str = "low"
    timeout_seconds: float = 20.0
    tags: set[str] = field(default_factory=set)
    backend_schema: dict[str, Any] | None = None

    def to_anthropic_schema(self) -> dict[str, Any]:
        """Return the schema shape currently consumed by familiar-ai backends."""
        if self.backend_schema is not None:
            return dict(self.backend_schema)
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


@dataclass(slots=True)
class ToolExecutionResult:
    """Normalized output from a tool invocation."""

    text: str
    image_b64: str | None = None
    success: bool = True
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ToolProvider(Protocol):
    """A source of one or more runtime tools."""

    def specs(self) -> list[ToolSpec]:
        """Return tool specs exposed by this provider."""

    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:
        """Execute a tool by name."""
