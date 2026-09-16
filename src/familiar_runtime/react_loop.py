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
    from .context import ContextBlock
    from .runtime import InterruptSource, RuntimeHook, TurnContext

logger = logging.getLogger(__name__)


def _with_extra_system(
    system: str | tuple[str, str],
    extra: str,
) -> str | tuple[str, str]:
    """Append ``extra`` to a system prompt, preserving the (stable, variable) split.

    ``mid_turn_inject`` blocks are spliced into the *variable* half of a cached
    tuple prompt so the stable prefix keeps its cache_control eligibility.
    """
    if isinstance(system, tuple):
        stable, variable = system
        merged = f"{variable}\n\n{extra}" if variable else extra
        return (stable, merged)
    return f"{system}\n\n{extra}" if system else extra


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
        interrupt_source: "InterruptSource | None" = None,
        on_action: Callable[[str, dict], None] | None = None,
        on_image: Callable[[str], None] | None = None,
        on_tool_result: Callable[[str, dict, str], None] | None = None,
    ) -> RunTurnResult:
        from .runtime import RetryDecision  # local import avoids circular import

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
            # Surface any async user input queued since the last model call so
            # an unprompted remark gets folded into the in-flight turn instead
            # of being dropped.
            if interrupt_source is not None and not interrupt_source.empty():
                drained = await interrupt_source.drain()
                if drained:
                    joined = " / ".join(drained)
                    # A hook may reshape the spliced interrupt line (e.g. add a
                    # respond-with-say directive); first non-None wins.
                    formatted: str | None = None
                    if context is not None:
                        for hook in self._hooks:
                            formatted = await hook.format_interrupt_message(context, drained)
                            if formatted is not None:
                                break
                    messages.append(
                        self._backend.make_user_message(
                            formatted or f"[User interrupted]: {joined}"
                        )
                    )
                    emit("user", "interrupt", {"count": len(drained), "text": joined})

            # Let hooks inject per-iteration context (inner-voice notes, gentle
            # reminders). Blocks are spliced into this iteration's system prompt
            # so message-role alternation stays valid after tool results.
            iter_system = system
            if context is not None and self._hooks:
                extra_blocks: list[ContextBlock] = []
                for hook in self._hooks:
                    extra_blocks.extend(await hook.mid_turn_inject(context, iteration))
                if extra_blocks:
                    rendered = "\n\n".join(block.rendered_text() for block in extra_blocks)
                    iter_system = _with_extra_system(system, rendered)
                # Hooks may also append explicit user messages (e.g. a say()
                # reminder that must read as conversational pressure, not as
                # system framing).
                for hook in self._hooks:
                    for user_message in await hook.mid_turn_user_messages(context, iteration):
                        messages.append(self._backend.make_user_message(user_message))
                        emit("system", "mid_turn_message", {"text": user_message[:200]})

            emit("model", "model_request_start", {"iteration": iteration + 1})
            result, raw_content = await self._backend.stream_turn(
                system=iter_system,
                messages=messages,
                tools=self._tools.tool_defs(),
                max_tokens=max_tokens,
                on_text=on_text,
            )
            # Allow hooks to inspect or replace the raw model result. The
            # first hook to return a non-None ``ModelTurnResult`` wins, and
            # subsequent hooks observe the replacement. A hook may instead
            # return a ``RetryDecision`` to reject the reply and re-run the
            # loop with an injected correction message.
            retry_directive: RetryDecision | None = None
            if context is not None:
                for hook in self._hooks:
                    outcome = await hook.after_model_result(context, result)
                    if isinstance(outcome, RetryDecision):
                        retry_directive = outcome
                    elif outcome is not None:
                        result = outcome
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

            if retry_directive is not None and retry_directive.retry:
                # Keep the rejected reply in history for context, then splice the
                # correction and continue the loop instead of finishing the turn.
                messages.append(self._backend.make_assistant_message(result, raw_content))
                if retry_directive.inject_user_message:
                    messages.append(
                        self._backend.make_user_message(retry_directive.inject_user_message)
                    )
                emit(
                    "system",
                    "retry",
                    {"iteration": iteration + 1, "stop_reason": result.stop_reason},
                )
                continue

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
                # Announce every call first (order preserved), then execute
                # them CONCURRENTLY — a multi-tool iteration costs the slowest
                # tool, not the sum. Result events, hook replacement and
                # message assembly stay sequential in the model's order, so
                # every order-dependent semantic (replan splicing, streak
                # bookkeeping, tool_results layout) is unchanged.
                for tool_call in result.tool_calls:
                    all_tool_calls.append(tool_call)
                    emit(
                        "tool",
                        "tool_call",
                        {"name": tool_call.name, "input": tool_call.input},
                    )
                    if on_action is not None:
                        on_action(tool_call.name, tool_call.input)

                async def _execute(tool_call: ToolCall) -> tuple[str, ToolExecutionResult]:
                    """Run one tool; classify the outcome for exact event parity."""
                    timeout = self._tool_timeouts.get(tool_call.name, self._default_tool_timeout)
                    try:
                        return (
                            "ok",
                            await asyncio.wait_for(
                                self._tools.call(tool_call.name, tool_call.input),
                                timeout=timeout,
                            ),
                        )
                    except asyncio.TimeoutError:
                        return (
                            "timeout",
                            ToolExecutionResult(
                                text=f"Tool timeout: {tool_call.name} exceeded {timeout:.1f}s.",
                                success=False,
                                error="timeout",
                            ),
                        )
                    except Exception as exc:  # noqa: BLE001
                        return (
                            "exception",
                            ToolExecutionResult(
                                text=f"Tool error: {exc}", success=False, error=str(exc)
                            ),
                        )

                if len(result.tool_calls) == 1:
                    executed = [await _execute(result.tool_calls[0])]
                else:
                    executed = list(
                        await asyncio.gather(*(_execute(tc) for tc in result.tool_calls))
                    )

                collected: list[tuple[str, str | None]] = []
                for tool_call, (exec_outcome, tool_result) in zip(result.tool_calls, executed):
                    if exec_outcome == "timeout":
                        emit(
                            "tool",
                            "tool_timeout",
                            {
                                "name": tool_call.name,
                                "timeout": self._tool_timeouts.get(
                                    tool_call.name, self._default_tool_timeout
                                ),
                            },
                        )
                    elif exec_outcome == "exception":
                        emit(
                            "tool",
                            "tool_error",
                            {"name": tool_call.name, "error": tool_result.error},
                        )
                    else:
                        emit(
                            "tool",
                            "tool_result",
                            {
                                "name": tool_call.name,
                                "success": tool_result.success,
                                "error": tool_result.error,
                            },
                        )

                    # Hooks may replace the result (e.g. splice an adaptive
                    # replan into the text); the first non-None return wins
                    # and later hooks observe the replacement.
                    if context is not None:
                        for hook in self._hooks:
                            replaced = await hook.after_tool_result(context, tool_call, tool_result)
                            if replaced is not None:
                                tool_result = replaced

                    collected.append((tool_result.text, tool_result.image_b64))
                    if tool_result.image_b64 and on_image is not None:
                        on_image(tool_result.image_b64)
                    if on_tool_result is not None:
                        on_tool_result(tool_call.name, tool_call.input, tool_result.text)

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
