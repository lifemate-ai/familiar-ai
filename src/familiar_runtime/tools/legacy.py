"""Compatibility helpers for existing familiar_agent tool objects."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from .base import ToolExecutionResult, ToolSpec

BeforeToolCall = Callable[[str, dict[str, Any]], None | Awaitable[None]]


class LegacyToolProvider:
    """Adapt existing get_tool_definitions()/call() objects to ToolProvider."""

    def __init__(
        self,
        tool: Any,
        *,
        names: set[str] | None = None,
        category: str = "generic",
        tags: set[str] | None = None,
        before_call: BeforeToolCall | None = None,
    ) -> None:
        self._tool = tool
        self._names = names
        self._category = category
        self._tags = tags or set()
        self._before_call = before_call

    def specs(self) -> list[ToolSpec]:
        defs: list[dict[str, Any]] = []
        get_defs = getattr(self._tool, "get_tool_definitions", None)
        if callable(get_defs):
            try:
                defs = list(get_defs())
            except Exception:
                defs = []
        if not defs and self._names:
            defs = [
                {
                    "name": name,
                    "description": "",
                    "input_schema": {"type": "object", "properties": {}},
                }
                for name in sorted(self._names)
            ]
        if self._names is not None:
            defs = [definition for definition in defs if definition.get("name") in self._names]

        specs: list[ToolSpec] = []
        for definition in defs:
            input_schema = definition.get("input_schema")
            if not isinstance(input_schema, dict):
                input_schema = {"type": "object", "properties": {}}
            specs.append(
                ToolSpec(
                    name=str(definition["name"]),
                    description=str(definition.get("description", "")),
                    input_schema=dict(input_schema),
                    category=self._category,
                    tags=set(self._tags),
                    backend_schema=dict(definition),
                )
            )
        return specs

    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:
        if self._before_call is not None:
            maybe_awaitable = self._before_call(name, tool_input)
            if inspect.isawaitable(maybe_awaitable):
                await maybe_awaitable

        text, image = await self._tool.call(name, tool_input)
        return ToolExecutionResult(text=str(text), image_b64=image)
