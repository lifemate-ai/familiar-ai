"""Tests for the generic tool registry."""

from __future__ import annotations

from typing import Any

import pytest

from familiar_runtime.tools.base import ToolExecutionResult, ToolSpec
from familiar_runtime.tools.registry import ToolRegistry


class _Provider:
    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.text = text
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(
                name=self.name,
                description=f"{self.name} tool",
                input_schema={"type": "object", "properties": {}},
                category="test",
            )
        ]

    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:
        self.calls.append((name, tool_input))
        return ToolExecutionResult(text=self.text)


@pytest.mark.asyncio
async def test_first_registered_provider_wins_name_collision() -> None:
    first = _Provider("same", "first")
    second = _Provider("same", "second")
    registry = ToolRegistry()
    registry.register(first)
    registry.register(second)

    result = await registry.call("same", {"x": 1})

    assert result.text == "first"
    assert first.calls == [("same", {"x": 1})]
    assert second.calls == []


@pytest.mark.asyncio
async def test_fallback_provider_handles_dynamic_unknown_tools() -> None:
    fallback = _Provider("declared", "fallback")
    registry = ToolRegistry()
    registry.register_fallback(fallback)

    result = await registry.call("dynamic_tool", {"ok": True})

    assert result.text == "fallback"
    assert fallback.calls == [("dynamic_tool", {"ok": True})]


def test_tool_defs_filters_by_allowed_tags() -> None:
    registry = ToolRegistry()
    spec = ToolSpec(
        name="task_tool",
        description="Task tool",
        input_schema={"type": "object", "properties": {}},
        tags={"task"},
    )

    class _Tagged:
        def specs(self) -> list[ToolSpec]:
            return [spec]

        async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:
            return ToolExecutionResult(text="ok")

    registry.register(_Tagged())

    assert [tool["name"] for tool in registry.tool_defs(allowed_tags={"task"})] == ["task_tool"]
    assert registry.tool_defs(allowed_tags={"neighbor"}) == []
