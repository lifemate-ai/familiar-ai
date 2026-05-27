"""Provider-neutral ReAct loop for task-oriented runtimes."""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .events.bus import EventBus
from .models.base import ModelBackend, ToolCall
from .tools.base import ToolExecutionResult
from .tools.registry import ToolRegistry

if TYPE_CHECKING:
    from .runtime import RuntimeHook, TurnContext

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RunTurnResult:
    """Structured result from a generic runtime turn."""

    final_text: str
    stop_reason: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    events: list[str] = field(default_factory=list)
    task_id: str | None = None


class ReActLoop:
    """Generic model/tool loop independent of neighbor cognition."""

    def __init__(
        self,
        *,
        backend: ModelBackend,
        tools: ToolRegistry,
        max_iterations: int = 50,
        default_tool_timeout: float = 20.0,
        tool_timeouts: dict[str, float] | None = None,
        event_bus: EventBus | None = None,
        hooks: Sequence["RuntimeHook"] = (),
    ) -> None:
        self._backend = backend
        self._tools = tools
        self._max_iterations = max_iterations
        self._default_tool_timeout = default_tool_timeout
        self._tool_timeouts = tool_timeouts or {}
        self._event_bus = event_bus
        self._hooks = list(hooks)

    async def run(
        self,
        *,
        system: str | tuple[str, str],
        messages: list[Any],
        max_tokens: int,
        on_text: Callable[[str], None] | None = None,
        run_id: str | None = None,
        task_id: str | None = None,
        turn_id: str | None = None,
        context: "TurnContext | None" = None,
    ) -> RunTurnResult:
        run_id = run_id or f"run_{uuid.uuid4().hex}"
        turn_id = turn_id or f"turn_{uuid.uuid4().hex}"
        event_ids: list[str] = []
        all_tool_calls: list[ToolCall] = []
        input_tokens = 0
        output_tokens = 0

        def emit(source: str, type: str, payload: dict[str, Any]) -> None:
            if self._event_bus is None:
                return
            event = self._event_bus.emit_simple(
                source=source,
                type=type,
                payload=payload,
                run_id=run_id,
                task_id=task_id,
                turn_id=turn_id,
            )
            event_ids.append(event.id)

        emit("system", "turn_start", {})

        for iteration in range(self._max_iterations):
            emit("model", "model_request_start", {"iteration": iteration + 1})
            result, raw_content = await self._backend.stream_turn(
                system=system,
                messages=messages,
                tools=self._tools.tool_defs(),
                max_tokens=max_tokens,
                on_text=on_text,
            )
            # Allow hooks to inspect or replace the raw model result. The
            # first hook to return a non-None value wins, and subsequent
            # hooks observe the replacement.
            if context is not None:
                for hook in self._hooks:
                    replacement = await hook.after_model_result(context, result)
                    if replacement is not None:
                        result = replacement
            input_tokens += result.input_tokens
            output_tokens += result.output_tokens
            emit(
                "model",
                "model_result",
                {
                    "stop_reason": result.stop_reason,
                    "tool_calls": [tool_call.name for tool_call in result.tool_calls],
                },
            )

            if result.stop_reason == "end_turn":
                messages.append(self._backend.make_assistant_message(result, raw_content))
                final_text = result.text or "(no response)"
                emit("assistant", "message", {"text": final_text})
                emit("system", "turn_end", {"stop_reason": "end_turn"})
                return RunTurnResult(
                    final_text=final_text,
                    stop_reason="end_turn",
                    tool_calls=all_tool_calls,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    events=event_ids,
                    task_id=task_id,
                )

            if result.stop_reason == "tool_use":
                collected: list[tuple[str, str | None]] = []
                for tool_call in result.tool_calls:
                    all_tool_calls.append(tool_call)
                    emit(
                        "tool",
                        "tool_call",
                        {"name": tool_call.name, "input": tool_call.input},
                    )
                    timeout = self._tool_timeouts.get(tool_call.name, self._default_tool_timeout)
                    try:
                        tool_result = await asyncio.wait_for(
                            self._tools.call(tool_call.name, tool_call.input),
                            timeout=timeout,
                        )
                    except asyncio.TimeoutError:
                        text = f"Tool timeout: {tool_call.name} exceeded {timeout:.1f}s."
                        collected.append((text, None))
                        emit(
                            "tool",
                            "tool_timeout",
                            {"name": tool_call.name, "timeout": timeout},
                        )
                        if context is not None and self._hooks:
                            timeout_result = ToolExecutionResult(
                                text=text, success=False, error="timeout"
                            )
                            for hook in self._hooks:
                                await hook.after_tool_result(context, tool_call, timeout_result)
                        continue
                    except Exception as exc:  # noqa: BLE001
                        text = f"Tool error: {exc}"
                        collected.append((text, None))
                        emit("tool", "tool_error", {"name": tool_call.name, "error": str(exc)})
                        if context is not None and self._hooks:
                            error_result = ToolExecutionResult(
                                text=text, success=False, error=str(exc)
                            )
                            for hook in self._hooks:
                                await hook.after_tool_result(context, tool_call, error_result)
                        continue

                    collected.append((tool_result.text, tool_result.image_b64))
                    emit(
                        "tool",
                        "tool_result",
                        {
                            "name": tool_call.name,
                            "success": tool_result.success,
                            "error": tool_result.error,
                        },
                    )
                    if context is not None:
                        for hook in self._hooks:
                            await hook.after_tool_result(context, tool_call, tool_result)

                messages.append(self._backend.make_assistant_message(result, raw_content))
                messages.append(self._backend.make_tool_results(result.tool_calls, collected))
                continue

            logger.warning("Unexpected stop_reason: %s", result.stop_reason)
            break

        emit("system", "turn_end", {"stop_reason": "max_iterations"})
        return RunTurnResult(
            final_text="(max iterations reached)",
            stop_reason="max_iterations",
            tool_calls=all_tool_calls,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            events=event_ids,
            task_id=task_id,
        )
