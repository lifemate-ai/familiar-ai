"""Minimal generic runtime facade."""

from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from .context import ContextBlock, select_context_blocks
from .events.bus import EventBus
from .models.base import ModelBackend, ModelTurnResult, ToolCall
from .react_loop import ReActLoop, RunTurnResult
from .tools.base import ToolExecutionResult
from .tools.registry import ToolRegistry


@dataclass(slots=True)
class TurnContext:
    """Runtime state for one turn."""

    user_input: str
    profile: str
    task_id: str | None = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RetryDecision:
    """Hook-returnable directive for re-running a turn iteration.

    Reserved shape for the upcoming embodied agent thin-wrap (see PR3 in
    ``plans/familiar-ai-codex-usage-limit-3-familia-agile-castle.md``).
    A hook's ``after_model_result`` can return one of these to tell the
    ReAct loop to reject the model's reply, splice an inserted user
    message back into history, and continue the loop instead of finishing
    the turn.

    The runtime does NOT yet honour ``RetryDecision`` returns from hooks;
    this PR only pins the shape so callers can rely on it.
    """

    retry: bool = False
    inject_user_message: str | None = None


class InterruptSource(Protocol):
    """Polling shim a profile can hand the runtime to surface async user input.

    Reserved shape for the upcoming embodied agent thin-wrap (see PR3).
    The neighbour profile drains an ``asyncio.Queue`` between ReAct
    iterations so unprompted user remarks get folded into the in-flight
    turn rather than dropped on the floor.

    The runtime does NOT yet poll any ``InterruptSource``; this PR only
    pins the shape so callers can rely on it.
    """

    async def drain(self) -> list[str]:
        """Return all currently-queued user-side messages, removing them."""
        ...

    def empty(self) -> bool:
        """Return True when ``drain()`` would return an empty list."""
        ...


class RuntimeHook(Protocol):
    """Hook interface used by profiles to participate in a turn.

    Hooks are invoked in registration order at the documented points.
    All callbacks are optional in spirit: implementations may inherit from
    :class:`RuntimeHookBase` for safe no-op defaults.

    ``mid_turn_inject`` is a *reserved* hook slot (see PR3 plan): the
    runtime declares it for type-stability and the base class returns ``[]``,
    but the ReAct loop does not yet call it.  PR3 wires the call into
    :class:`ReActLoop` so profiles can inject per-iteration ``ContextBlock``
    extras (e.g. inner-voice notes, say() reminders).
    """

    async def before_turn(self, ctx: TurnContext) -> None: ...

    async def build_context(self, ctx: TurnContext) -> list[ContextBlock]: ...

    async def mid_turn_inject(
        self,
        ctx: TurnContext,
        iteration: int,
    ) -> list[ContextBlock]: ...

    async def after_model_result(
        self,
        ctx: TurnContext,
        result: ModelTurnResult,
    ) -> ModelTurnResult | None: ...

    async def after_tool_result(
        self,
        ctx: TurnContext,
        call: ToolCall,
        result: ToolExecutionResult,
    ) -> None: ...

    async def after_turn(self, ctx: TurnContext, final_text: str) -> None: ...


class RuntimeHookBase:
    """No-op base class so concrete hooks only override what they need."""

    async def before_turn(self, ctx: TurnContext) -> None:  # noqa: ARG002
        return None

    async def build_context(self, ctx: TurnContext) -> list[ContextBlock]:  # noqa: ARG002
        return []

    async def mid_turn_inject(
        self,
        ctx: TurnContext,  # noqa: ARG002
        iteration: int,  # noqa: ARG002
    ) -> list[ContextBlock]:
        return []

    async def after_model_result(
        self,
        ctx: TurnContext,  # noqa: ARG002
        result: ModelTurnResult,  # noqa: ARG002
    ) -> ModelTurnResult | None:
        return None

    async def after_tool_result(
        self,
        ctx: TurnContext,  # noqa: ARG002
        call: ToolCall,  # noqa: ARG002
        result: ToolExecutionResult,  # noqa: ARG002
    ) -> None:
        return None

    async def after_turn(self, ctx: TurnContext, final_text: str) -> None:  # noqa: ARG002
        return None


class AgentRuntime:
    """Thin generic runtime facade around hooks, context selection, and ReAct."""

    def __init__(
        self,
        *,
        backend: ModelBackend,
        tools: ToolRegistry,
        hooks: Sequence[RuntimeHook] = (),
        event_bus: EventBus | None = None,
        max_context_chars: int = 6000,
    ) -> None:
        self._backend = backend
        self._tools = tools
        self._hooks = list(hooks)
        self._event_bus = event_bus
        self._max_context_chars = max_context_chars

    async def run_turn(
        self,
        user_input: str,
        *,
        profile: str = "task",
        task_id: str | None = None,
        system_prompt: str = "",
        messages: list[Any] | None = None,
        max_tokens: int = 4096,
        interrupt_source: InterruptSource | None = None,  # noqa: ARG002
    ) -> RunTurnResult:
        # ``interrupt_source`` is a reserved parameter (see PR3 plan): the
        # runtime accepts it now so the embodied agent thin-wrap can pass
        # an ``asyncio.Queue`` adapter without breaking its call site, but
        # ReActLoop does not yet poll it.  The arg is intentionally not
        # surfaced into TurnContext until the polling is wired up.
        ctx = TurnContext(user_input=user_input, profile=profile, task_id=task_id)
        for hook in self._hooks:
            await hook.before_turn(ctx)

        blocks: list[ContextBlock] = []
        for hook in self._hooks:
            blocks.extend(await hook.build_context(ctx))
        selected = select_context_blocks(blocks, max_chars=self._max_context_chars)
        context_text = "\n\n".join(block.rendered_text() for block in selected)
        system = f"{system_prompt}\n\n{context_text}".strip()

        turn_messages = messages if messages is not None else []
        turn_messages.append(self._backend.make_user_message(user_input))
        if self._event_bus is not None:
            self._event_bus.emit_simple(
                source="user",
                type="message",
                payload={"text": user_input},
                task_id=task_id,
            )
        loop = ReActLoop(
            backend=self._backend,
            tools=self._tools,
            event_bus=self._event_bus,
            hooks=self._hooks,
        )
        result = await loop.run(
            system=system,
            messages=turn_messages,
            max_tokens=max_tokens,
            task_id=task_id,
            context=ctx,
        )
        for hook in self._hooks:
            await hook.after_turn(ctx, result.final_text)
        return result
