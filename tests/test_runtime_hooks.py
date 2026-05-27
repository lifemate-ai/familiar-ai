"""Tests for the runtime hook protocol and ReActLoop integration."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from familiar_runtime.context import ContextBlock
from familiar_runtime.models import ModelTurnResult, ToolCall
from familiar_runtime.runtime import AgentRuntime, RuntimeHookBase, TurnContext
from familiar_runtime.tools.base import ToolExecutionResult, ToolSpec
from familiar_runtime.tools.registry import ToolRegistry


class _ScriptedBackend:
    """Minimal scripted backend reused across hook tests."""

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
            {"role": "tool", "name": tool_call.name, "content": text}
            for tool_call, (text, _image) in zip(tool_calls, results)
        ]

    async def stream_turn(self, **kwargs: Any) -> tuple[ModelTurnResult, Any]:
        result = self.turns.pop(0)
        return result, {"raw": result.text}

    async def complete(self, prompt: str, max_tokens: int) -> str:  # noqa: ARG002
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

    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:  # noqa: ARG002
        return ToolExecutionResult(text=f"echo: {tool_input.get('text', '')}")


class _SlowTool:
    """Always sleeps past the loop timeout to trigger the timeout branch."""

    def specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(
                name="slow",
                description="Slow",
                input_schema={"type": "object", "properties": {}},
            )
        ]

    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:  # noqa: ARG002
        await asyncio.sleep(5)
        return ToolExecutionResult(text="never")


class _ExplodingTool:
    def specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(
                name="boom",
                description="Boom",
                input_schema={"type": "object", "properties": {}},
            )
        ]

    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:  # noqa: ARG002
        raise RuntimeError("kaboom")


class _RecordingHook(RuntimeHookBase):
    """Hook that records every callback for verification."""

    def __init__(self, name: str = "rec") -> None:
        self.name = name
        self.events: list[tuple[str, Any]] = []

    async def before_turn(self, ctx: TurnContext) -> None:
        self.events.append(("before", ctx.user_input))

    async def build_context(self, ctx: TurnContext) -> list[ContextBlock]:
        self.events.append(("build_context", ctx.profile))
        return [
            ContextBlock(
                source=self.name,
                text=f"[{self.name}] context for {ctx.user_input}",
                priority=1.0,
            )
        ]

    async def after_model_result(
        self,
        ctx: TurnContext,
        result: ModelTurnResult,
    ) -> ModelTurnResult | None:
        self.events.append(("after_model", result.stop_reason))
        return None

    async def after_tool_result(
        self,
        ctx: TurnContext,
        call: ToolCall,
        result: ToolExecutionResult,
    ) -> None:
        self.events.append(("after_tool", call.name, result.success, result.error))

    async def after_turn(self, ctx: TurnContext, final_text: str) -> None:
        self.events.append(("after_turn", final_text))


def _build_runtime(
    turns: list[ModelTurnResult],
    *,
    hooks: list[Any] | None = None,
    tool_provider: Any | None = None,
    default_tool_timeout: float = 20.0,
) -> tuple[AgentRuntime, _ScriptedBackend]:
    backend = _ScriptedBackend(turns)
    registry = ToolRegistry()
    if tool_provider is not None:
        registry.register(tool_provider)
    runtime = AgentRuntime(
        backend=backend,
        tools=registry,
        hooks=hooks or [],
    )
    return runtime, backend


@pytest.mark.asyncio
async def test_runtime_hook_base_is_a_safe_default() -> None:
    """RuntimeHookBase methods are all no-ops so concrete hooks only override what they need."""
    hook = RuntimeHookBase()
    ctx = TurnContext(user_input="hi", profile="task")
    assert await hook.before_turn(ctx) is None
    assert await hook.build_context(ctx) == []
    result = ModelTurnResult(stop_reason="end_turn", text="ok")
    assert await hook.after_model_result(ctx, result) is None
    tc = ToolCall(id="t", name="echo", input={})
    assert await hook.after_tool_result(ctx, tc, ToolExecutionResult(text="ok")) is None
    assert await hook.after_turn(ctx, "ok") is None


@pytest.mark.asyncio
async def test_hooks_run_in_order_for_simple_turn() -> None:
    runtime, _ = _build_runtime(
        turns=[ModelTurnResult(stop_reason="end_turn", text="hello back")],
        hooks=[_RecordingHook("h1"), _RecordingHook("h2")],
    )
    result = await runtime.run_turn("hello", profile="task")
    assert result.final_text == "hello back"
    h1, h2 = runtime._hooks  # type: ignore[attr-defined]
    assert h1.events[0] == ("before", "hello")
    assert h2.events[0] == ("before", "hello")
    # Both hooks must have observed every lifecycle step.
    assert ("after_model", "end_turn") in h1.events
    assert ("after_turn", "hello back") in h1.events
    assert ("after_turn", "hello back") in h2.events


@pytest.mark.asyncio
async def test_after_model_result_can_replace_result() -> None:
    """A hook returning a non-None ModelTurnResult replaces the model output."""

    class _Replacer(RuntimeHookBase):
        async def after_model_result(
            self,
            ctx: TurnContext,
            result: ModelTurnResult,
        ) -> ModelTurnResult | None:
            return ModelTurnResult(stop_reason=result.stop_reason, text=result.text + " (gated)")

    runtime, _ = _build_runtime(
        turns=[ModelTurnResult(stop_reason="end_turn", text="raw")],
        hooks=[_Replacer()],
    )
    result = await runtime.run_turn("hi")
    assert result.final_text == "raw (gated)"


@pytest.mark.asyncio
async def test_build_context_blocks_are_injected_into_system_prompt() -> None:
    captured_systems: list[str] = []

    class _SystemCapturingBackend(_ScriptedBackend):
        async def stream_turn(self, **kwargs: Any) -> tuple[ModelTurnResult, Any]:
            captured_systems.append(kwargs["system"])
            return await super().stream_turn(**kwargs)

    backend = _SystemCapturingBackend([ModelTurnResult(stop_reason="end_turn", text="ok")])
    registry = ToolRegistry()
    runtime = AgentRuntime(
        backend=backend,
        tools=registry,
        hooks=[_RecordingHook("rec")],
    )
    await runtime.run_turn("ping", profile="task", system_prompt="BASE")
    assert captured_systems
    assert "BASE" in captured_systems[0]
    assert "[rec] context for ping" in captured_systems[0]


@pytest.mark.asyncio
async def test_after_tool_result_fires_for_success_timeout_and_error() -> None:
    hook = _RecordingHook("rec")

    # success path
    runtime, _ = _build_runtime(
        turns=[
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[ToolCall(id="tc1", name="echo", input={"text": "hi"})],
            ),
            ModelTurnResult(stop_reason="end_turn", text="done"),
        ],
        hooks=[hook],
        tool_provider=_EchoTool(),
    )
    await runtime.run_turn("go")
    tool_events = [event for event in hook.events if event[0] == "after_tool"]
    assert tool_events == [("after_tool", "echo", True, None)]

    # timeout path
    hook = _RecordingHook("rec")
    backend = _ScriptedBackend(
        [
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[ToolCall(id="tc1", name="slow", input={})],
            ),
            ModelTurnResult(stop_reason="end_turn", text="finished"),
        ]
    )
    registry = ToolRegistry()
    registry.register(_SlowTool())
    runtime = AgentRuntime(backend=backend, tools=registry, hooks=[hook])
    # Use a tiny timeout via internal reach so the loop trips quickly.
    # AgentRuntime always rebuilds ReActLoop, so we patch the loop class default
    # by registering a tool name override via the loop's default_tool_timeout.
    # Simplest path: call ReActLoop directly with hooks+context for the timeout
    # branch instead of going through AgentRuntime.
    from familiar_runtime.react_loop import ReActLoop

    ctx = TurnContext(user_input="go", profile="task")
    loop = ReActLoop(
        backend=backend,
        tools=registry,
        hooks=[hook],
        default_tool_timeout=0.01,
    )
    messages: list[Any] = [backend.make_user_message("go")]
    await loop.run(
        system="sys",
        messages=messages,
        max_tokens=128,
        context=ctx,
    )
    tool_events = [event for event in hook.events if event[0] == "after_tool"]
    assert tool_events
    assert tool_events[0][1] == "slow"
    assert tool_events[0][2] is False
    assert tool_events[0][3] == "timeout"

    # error path
    hook = _RecordingHook("rec")
    backend = _ScriptedBackend(
        [
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[ToolCall(id="tc1", name="boom", input={})],
            ),
            ModelTurnResult(stop_reason="end_turn", text="done"),
        ]
    )
    registry = ToolRegistry()
    registry.register(_ExplodingTool())
    runtime = AgentRuntime(backend=backend, tools=registry, hooks=[hook])
    await runtime.run_turn("go")
    tool_events = [event for event in hook.events if event[0] == "after_tool"]
    assert tool_events
    assert tool_events[0][1] == "boom"
    assert tool_events[0][2] is False
    assert tool_events[0][3] == "kaboom"


@pytest.mark.asyncio
async def test_runtime_without_hooks_still_runs_react_loop() -> None:
    """Empty hook list must not break the loop."""
    runtime, _ = _build_runtime(
        turns=[ModelTurnResult(stop_reason="end_turn", text="ok")],
    )
    result = await runtime.run_turn("hi")
    assert result.final_text == "ok"
