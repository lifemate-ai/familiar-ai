"""Tests for the runtime hook protocol and ReActLoop integration."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from familiar_runtime.context import ContextBlock
from familiar_runtime.models import ModelTurnResult, ToolCall
from familiar_runtime.runtime import (
    AgentRuntime,
    InterruptSource,
    RetryDecision,
    RuntimeHookBase,
    TurnContext,
)
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
    assert await hook.mid_turn_inject(ctx, 0) == []
    result = ModelTurnResult(stop_reason="end_turn", text="ok")
    assert await hook.after_model_result(ctx, result) is None
    tc = ToolCall(id="t", name="echo", input={})
    assert await hook.after_tool_result(ctx, tc, ToolExecutionResult(text="ok")) is None
    assert await hook.after_turn(ctx, "ok") is None


def test_retry_decision_defaults_to_noop() -> None:
    """RetryDecision is the reserved shape PR3 will start honouring."""
    decision = RetryDecision()
    assert decision.retry is False
    assert decision.inject_user_message is None


def test_retry_decision_carries_injected_message() -> None:
    decision = RetryDecision(retry=True, inject_user_message="please be brief")
    assert decision.retry is True
    assert decision.inject_user_message == "please be brief"


@pytest.mark.asyncio
async def test_interrupt_source_protocol_acceptable_shape() -> None:
    """A trivial Queue-backed source satisfies the reserved InterruptSource shape."""

    class _ListSource:
        def __init__(self, items: list[str]) -> None:
            self._items = list(items)

        async def drain(self) -> list[str]:
            out = self._items
            self._items = []
            return out

        def empty(self) -> bool:
            return not self._items

    source: InterruptSource = _ListSource(["one", "two"])
    assert not source.empty()
    drained = await source.drain()
    assert drained == ["one", "two"]
    assert source.empty()


@pytest.mark.asyncio
async def test_empty_interrupt_source_is_not_drained() -> None:
    """An empty source is checked via empty() and never drained."""

    class _StubSource:
        async def drain(self) -> list[str]:
            raise AssertionError("empty() guards the drain; drain must not run")

        def empty(self) -> bool:
            return True

    runtime, _ = _build_runtime(
        turns=[ModelTurnResult(stop_reason="end_turn", text="ack")],
    )
    result = await runtime.run_turn("hi", interrupt_source=_StubSource())
    assert result.final_text == "ack"


@pytest.mark.asyncio
async def test_interrupt_source_drains_into_messages() -> None:
    """A non-empty source is drained and folded into the turn as a user message."""

    class _OneShotSource:
        def __init__(self, items: list[str]) -> None:
            self._items = list(items)

        async def drain(self) -> list[str]:
            out = self._items
            self._items = []
            return out

        def empty(self) -> bool:
            return not self._items

    backend = _ScriptedBackend([ModelTurnResult(stop_reason="end_turn", text="done")])
    registry = ToolRegistry()
    runtime = AgentRuntime(backend=backend, tools=registry, hooks=[])
    messages: list[Any] = []
    result = await runtime.run_turn(
        "go",
        messages=messages,
        interrupt_source=_OneShotSource(["hey wait", "look here"]),
    )
    assert result.final_text == "done"
    injected = [
        m
        for m in messages
        if m.get("role") == "user" and "[User interrupted]" in str(m.get("content"))
    ]
    assert injected
    assert "hey wait / look here" in str(injected[0]["content"])


@pytest.mark.asyncio
async def test_mid_turn_inject_called_each_iteration() -> None:
    """ReActLoop calls mid_turn_inject once per model iteration."""

    class _Counter(RuntimeHookBase):
        def __init__(self) -> None:
            self.iterations: list[int] = []

        async def mid_turn_inject(
            self,
            ctx: TurnContext,
            iteration: int,
        ) -> list[ContextBlock]:
            self.iterations.append(iteration)
            return []

    counter = _Counter()
    runtime, _ = _build_runtime(
        turns=[
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[ToolCall(id="tc1", name="echo", input={"text": "x"})],
            ),
            ModelTurnResult(stop_reason="end_turn", text="ok"),
        ],
        hooks=[counter],
        tool_provider=_EchoTool(),
    )
    await runtime.run_turn("ping")
    # Two model iterations (one tool_use, one end_turn) → two injections.
    assert counter.iterations == [0, 1]


@pytest.mark.asyncio
async def test_mid_turn_inject_blocks_injected_into_system() -> None:
    """Blocks returned from mid_turn_inject are spliced into the iteration system."""
    captured_systems: list[Any] = []

    class _SystemCapturingBackend(_ScriptedBackend):
        async def stream_turn(self, **kwargs: Any) -> tuple[ModelTurnResult, Any]:
            captured_systems.append(kwargs["system"])
            return await super().stream_turn(**kwargs)

    class _Injector(RuntimeHookBase):
        async def mid_turn_inject(
            self,
            ctx: TurnContext,
            iteration: int,
        ) -> list[ContextBlock]:
            return [ContextBlock(source="inner", text="[inner] keep it short", priority=1.0)]

    backend = _SystemCapturingBackend([ModelTurnResult(stop_reason="end_turn", text="ok")])
    registry = ToolRegistry()
    runtime = AgentRuntime(backend=backend, tools=registry, hooks=[_Injector()])
    await runtime.run_turn("ping", system_prompt="BASE")
    assert captured_systems
    assert "[inner] keep it short" in str(captured_systems[0])


@pytest.mark.asyncio
async def test_after_model_result_retry_decision_continues_loop() -> None:
    """A RetryDecision from after_model_result rejects the reply and re-runs the loop."""

    class _CoherenceGate(RuntimeHookBase):
        def __init__(self) -> None:
            self.seen = 0

        async def after_model_result(
            self,
            ctx: TurnContext,
            result: ModelTurnResult,
        ) -> ModelTurnResult | RetryDecision | None:
            self.seen += 1
            if self.seen == 1:
                return RetryDecision(
                    retry=True,
                    inject_user_message="[SELF-CHECK] fix the contradiction.",
                )
            return None

    gate = _CoherenceGate()
    backend = _ScriptedBackend(
        [
            ModelTurnResult(stop_reason="end_turn", text="bad answer"),
            ModelTurnResult(stop_reason="end_turn", text="good answer"),
        ]
    )
    registry = ToolRegistry()
    runtime = AgentRuntime(backend=backend, tools=registry, hooks=[gate])
    messages: list[Any] = []
    result = await runtime.run_turn("hi", messages=messages)
    assert result.final_text == "good answer"
    assert gate.seen == 2
    injected = [
        m for m in messages if m.get("role") == "user" and "[SELF-CHECK]" in str(m.get("content"))
    ]
    assert injected


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


# ---------------------------------------------------------------------------
# Thin-wrap substrate extensions: result replacement, user-message injection,
# interrupt formatting, tuple system prompts, and observer callbacks.
# ---------------------------------------------------------------------------


class _ImageTool:
    def specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(
                name="snap",
                description="Snap",
                input_schema={"type": "object", "properties": {}},
            )
        ]

    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:  # noqa: ARG002
        return ToolExecutionResult(text="a photo", image_b64="IMGB64")


class _ReplanHook(RuntimeHookBase):
    """Mimics TAPE replan: splices a replan note into the tool result."""

    async def after_tool_result(
        self,
        ctx: TurnContext,  # noqa: ARG002
        call: ToolCall,  # noqa: ARG002
        result: ToolExecutionResult,
    ) -> ToolExecutionResult | None:
        return ToolExecutionResult(
            text=f"{result.text}\n\n[ADAPTIVE REPLAN] new plan",
            image_b64=result.image_b64,
            success=result.success,
            error=result.error,
        )


@pytest.mark.asyncio
async def test_after_tool_result_replacement_reaches_history() -> None:
    backend = _ScriptedBackend(
        [
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[ToolCall(id="tc1", name="echo", input={"text": "hi"})],
            ),
            ModelTurnResult(stop_reason="end_turn", text="done"),
        ]
    )
    registry = ToolRegistry()
    registry.register(_EchoTool())
    runtime = AgentRuntime(backend=backend, tools=registry, hooks=[_ReplanHook()])
    messages: list[Any] = []
    await runtime.run_turn("go", messages=messages)
    flat: list[Any] = []
    for m in messages:
        flat.extend(m if isinstance(m, list) else [m])
    tool_messages = [m for m in flat if isinstance(m, dict) and m.get("role") == "tool"]
    assert tool_messages
    assert "[ADAPTIVE REPLAN] new plan" in tool_messages[0]["content"]


class _SayReminderHook(RuntimeHookBase):
    """Injects a user message before the second model call."""

    async def mid_turn_user_messages(
        self,
        ctx: TurnContext,  # noqa: ARG002
        iteration: int,
    ) -> list[str]:
        if iteration == 1:
            return ["REMINDER: call say() now."]
        return []


@pytest.mark.asyncio
async def test_mid_turn_user_messages_appended_to_history() -> None:
    backend = _ScriptedBackend(
        [
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[ToolCall(id="tc1", name="echo", input={})],
            ),
            ModelTurnResult(stop_reason="end_turn", text="done"),
        ]
    )
    registry = ToolRegistry()
    registry.register(_EchoTool())
    runtime = AgentRuntime(backend=backend, tools=registry, hooks=[_SayReminderHook()])
    messages: list[Any] = []
    await runtime.run_turn("go", messages=messages)
    user_texts = [
        m["content"]
        for m in messages
        if isinstance(m, dict) and m.get("role") == "user" and isinstance(m.get("content"), str)
    ]
    assert "REMINDER: call say() now." in user_texts


class _ListInterrupts:
    def __init__(self, items: list[str]) -> None:
        self._items = list(items)

    async def drain(self) -> list[str]:
        items, self._items = self._items, []
        return items

    def empty(self) -> bool:
        return not self._items


class _InterruptFormatHook(RuntimeHookBase):
    async def format_interrupt_message(
        self,
        ctx: TurnContext,  # noqa: ARG002
        interrupts: list[str],
    ) -> str | None:
        return f"[User interrupted x{len(interrupts)}]: {interrupts[0]}. Respond with say() now."


@pytest.mark.asyncio
async def test_interrupt_format_hook_overrides_default() -> None:
    backend = _ScriptedBackend([ModelTurnResult(stop_reason="end_turn", text="ok")])
    runtime = AgentRuntime(backend=backend, tools=ToolRegistry(), hooks=[_InterruptFormatHook()])
    messages: list[Any] = []
    await runtime.run_turn(
        "go", messages=messages, interrupt_source=_ListInterrupts(["まだ起きてる？"])
    )
    user_texts = [
        m["content"]
        for m in messages
        if isinstance(m, dict) and m.get("role") == "user" and isinstance(m.get("content"), str)
    ]
    assert any(t.startswith("[User interrupted x1]") and "say() now" in t for t in user_texts)


@pytest.mark.asyncio
async def test_interrupt_default_format_without_hook() -> None:
    backend = _ScriptedBackend([ModelTurnResult(stop_reason="end_turn", text="ok")])
    runtime = AgentRuntime(backend=backend, tools=ToolRegistry(), hooks=[RuntimeHookBase()])
    messages: list[Any] = []
    await runtime.run_turn("go", messages=messages, interrupt_source=_ListInterrupts(["hello"]))
    user_texts = [
        m["content"]
        for m in messages
        if isinstance(m, dict) and m.get("role") == "user" and isinstance(m.get("content"), str)
    ]
    assert any(t.startswith("[User interrupted]:") for t in user_texts)


class _SystemRecordingBackend(_ScriptedBackend):
    def __init__(self, turns: list[ModelTurnResult]) -> None:
        super().__init__(turns)
        self.systems: list[Any] = []

    async def stream_turn(self, **kwargs: Any) -> tuple[ModelTurnResult, Any]:
        self.systems.append(kwargs.get("system"))
        return await super().stream_turn(**kwargs)


@pytest.mark.asyncio
async def test_run_turn_accepts_tuple_system_prompt() -> None:
    """The (stable, variable) split must survive run_turn so the Anthropic
    adapter's cache_control on the stable half stays effective."""
    backend = _SystemRecordingBackend([ModelTurnResult(stop_reason="end_turn", text="ok")])
    hook = _RecordingHook("ctx")
    runtime = AgentRuntime(backend=backend, tools=ToolRegistry(), hooks=[hook])
    await runtime.run_turn("go", system_prompt=("STABLE-CORE", "variable bits"))
    system = backend.systems[0]
    assert isinstance(system, tuple)
    stable, variable = system
    assert stable == "STABLE-CORE"
    assert "variable bits" in variable
    assert "[ctx] context for go" in variable  # build_context lands in the variable half
    assert "STABLE-CORE" not in variable


@pytest.mark.asyncio
async def test_observer_callbacks_fire() -> None:
    backend = _ScriptedBackend(
        [
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[ToolCall(id="tc1", name="snap", input={"x": 1})],
            ),
            ModelTurnResult(stop_reason="end_turn", text="done"),
        ]
    )
    registry = ToolRegistry()
    registry.register(_ImageTool())
    runtime = AgentRuntime(backend=backend, tools=registry)
    actions: list[tuple[str, dict]] = []
    images: list[str] = []
    tool_results: list[tuple[str, dict, str]] = []
    await runtime.run_turn(
        "go",
        on_action=lambda name, tool_input: actions.append((name, tool_input)),
        on_image=images.append,
        on_tool_result=lambda name, tool_input, text: tool_results.append((name, tool_input, text)),
    )
    assert actions == [("snap", {"x": 1})]
    assert images == ["IMGB64"]
    assert tool_results == [("snap", {"x": 1}, "a photo")]


@pytest.mark.asyncio
async def test_on_tool_result_fires_on_tool_error() -> None:
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
    runtime = AgentRuntime(backend=backend, tools=registry)
    tool_results: list[tuple[str, dict, str]] = []
    await runtime.run_turn(
        "go",
        on_tool_result=lambda name, tool_input, text: tool_results.append((name, tool_input, text)),
    )
    assert len(tool_results) == 1
    assert tool_results[0][0] == "boom"
    assert "Tool error" in tool_results[0][2]
