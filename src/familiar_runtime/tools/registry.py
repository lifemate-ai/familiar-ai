"""Tool registry with deterministic routing and optional fallback."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .base import ToolExecutionResult, ToolProvider, ToolSpec


class ToolRegistry:
    """Register tool providers and route calls by tool name."""

    def __init__(self) -> None:
        self._providers: list[ToolProvider] = []
        self._routes: dict[str, ToolProvider] = {}
        self._specs: dict[str, ToolSpec] = {}
        self._fallback: ToolProvider | None = None

    def register(self, provider: ToolProvider) -> None:
        """Register a provider.

        The first provider for a name wins. This preserves existing MCP collision behavior where
        earlier tool definitions keep priority.
        """
        self._providers.append(provider)
        for spec in provider.specs():
            if spec.name in self._routes:
                continue
            self._routes[spec.name] = provider
            self._specs[spec.name] = spec

    def register_fallback(self, provider: ToolProvider) -> None:
        """Register a provider for unknown names, used for dynamic MCP tools."""
        self._fallback = provider

    def has_tool(self, name: str) -> bool:
        """Return whether a non-fallback route exists for a name."""
        return name in self._routes

    def specs(
        self,
        *,
        profile: str | None = None,
        allowed_tags: set[str] | None = None,
    ) -> list[ToolSpec]:
        """Return specs, optionally filtered by profile/tag."""
        specs = list(self._specs.values())
        if profile is not None:
            specs = [
                spec
                for spec in specs
                if not spec.tags or profile in spec.tags or "all" in spec.tags
            ]
        if allowed_tags is not None:
            specs = [spec for spec in specs if spec.tags & allowed_tags]
        return [replace(spec, tags=set(spec.tags)) for spec in specs]

    def tool_defs(
        self,
        *,
        profile: str | None = None,
        allowed_tags: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Return backend-compatible tool definitions."""
        return [
            spec.to_anthropic_schema()
            for spec in self.specs(profile=profile, allowed_tags=allowed_tags)
        ]

    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:
        """Route a call to its provider."""
        provider = self._routes.get(name) or self._fallback
        if provider is None:
            return ToolExecutionResult(
                text=f"Tool '{name}' not available (check configuration).",
                success=False,
                error="tool_not_available",
            )
        return await provider.call(name, tool_input)
