"""Minimal generic runtime facade."""

from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from .context import ContextBlock, select_context_blocks
from .events.bus import EventBus
from .models.base import ModelBackend
from .react_loop import ReActLoop, RunTurnResult
from .tools.registry import ToolRegistry


class RuntimeHook(Protocol):
    """Hook interface used by profiles to participate in a turn."""

    async def before_turn(self, ctx: "TurnContext") -> None: ...

    async def build_context(self, ctx: "TurnContext") -> list[ContextBlock]: ...

    async def after_turn(self, ctx: "TurnContext", final_text: str) -> None: ...


@dataclass(slots=True)
class TurnContext:
    """Runtime state for one turn."""

    user_input: str
    profile: str
    task_id: str | None = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


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
    ) -> RunTurnResult:
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
        loop = ReActLoop(backend=self._backend, tools=self._tools, event_bus=self._event_bus)
        result = await loop.run(
            system=system,
            messages=turn_messages,
            max_tokens=max_tokens,
            task_id=task_id,
        )
        for hook in self._hooks:
            await hook.after_turn(ctx, result.final_text)
        return result
