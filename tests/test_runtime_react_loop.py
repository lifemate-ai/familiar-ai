"""Tests for the generic ReAct loop."""

from __future__ import annotations

from typing import Any

import pytest

from familiar_runtime.events import EventBus
from familiar_runtime.models import ModelTurnResult, ToolCall
from familiar_runtime.react_loop import ReActLoop
from familiar_runtime.tools.base import ToolExecutionResult, ToolSpec
from familiar_runtime.tools.registry import ToolRegistry


class _ScriptedBackend:
    def __init__(self, turns: list[ModelTurnResult]) -> None:
        self.turns = list(turns)

    def make_user_message(self, content: str | list[Any]) -> dict[str, Any]:
        return {"role": "user", "content": content}

    def make_assistant_message(
        self,
        result: ModelTurnResult,
        raw_content: Any | None = None,
    ) -> dict[str, Any]:
        return {"role": "assistant", "content": result.text, "raw": raw_content}

    def make_tool_results(
        self,
        tool_calls: list[ToolCall],
        results: list[tuple[str, str | None]],
    ) -> list[dict[str, Any]]:
        return [
            {
                "role": "tool",
                "name": tool_call.name,
                "content": text,
                "image": image,
            }
            for tool_call, (text, image) in zip(tool_calls, results)
        ]

    async def stream_turn(self, **kwargs):
        result = self.turns.pop(0)
        return result, {"raw": result.text}

    async def complete(self, prompt: str, max_tokens: int) -> str:
        return ""


class _EchoTool:
    def specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(
                name="echo",
                description="Echo",
                input_schema={"type": "object", "properties": {}},
            )
        ]

    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:
        return ToolExecutionResult(text=f"echo: {tool_input['text']}")


@pytest.mark.asyncio
async def test_react_loop_executes_tool_and_returns_final_text() -> None:
    backend = _ScriptedBackend(
        [
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[ToolCall(id="tc1", name="echo", input={"text": "hi"})],
                input_tokens=10,
                output_tokens=2,
            ),
            ModelTurnResult(
                stop_reason="end_turn",
                text="done",
                input_tokens=11,
                output_tokens=3,
            ),
        ]
    )
    registry = ToolRegistry()
    registry.register(_EchoTool())
    bus = EventBus()
    seen: list[str] = []
    bus.subscribe(lambda event: seen.append(event.type))
    messages: list[Any] = []

    result = await ReActLoop(backend=backend, tools=registry, event_bus=bus).run(
        system="sys",
        messages=messages,
        max_tokens=100,
    )

    assert result.final_text == "done"
    assert result.input_tokens == 21
    assert result.output_tokens == 5
    assert [call.name for call in result.tool_calls] == ["echo"]
    flat_messages = []
    for message in messages:
        if isinstance(message, list):
            flat_messages.extend(message)
        else:
            flat_messages.append(message)
    assert any(message.get("role") == "tool" for message in flat_messages)
    assert "tool_call" in seen
    assert "tool_result" in seen
