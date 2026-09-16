# ADR 0003: Expand RuntimeHook with after_model_result and after_tool_result

## Status

Accepted

## Context

ADR 0001 introduced `familiar_runtime` and a small `RuntimeHook` protocol with three
callbacks: `before_turn`, `build_context`, `after_turn`. That surface is enough to inject
context blocks and observe completed turns, but it can not express two patterns that the
neighbor profile already relies on inside `familiar_agent.EmbodiedAgent.run()`:

1. **Response gating** — the meta-monitor inspects every model turn and may rewrite the
   text before it reaches the user. The original protocol had no insertion point between
   `stream_turn` and the next loop iteration.
2. **Tool-result side effects** — relationship updates, post-tool memory writes, and
   observability hooks need to observe every tool invocation, including timeout / exception
   paths. The original protocol exposed only the final assistant text.

Without these callbacks, neighbor cognition is forced to stay co-located with the ReAct
loop, which blocks ADR 0001's goal of running the runtime substrate without neighbor
imports.

## Decision

Expand `RuntimeHook` with two new optional callbacks and provide a `RuntimeHookBase`
no-op default class so concrete hooks only override what they need:

```python
class RuntimeHook(Protocol):
    async def before_turn(self, ctx: TurnContext) -> None: ...
    async def build_context(self, ctx: TurnContext) -> list[ContextBlock]: ...

    # NEW: called by ReActLoop immediately after each backend.stream_turn.
    # First hook to return a non-None value replaces the model result; later
    # hooks observe the replacement.
    async def after_model_result(
        self,
        ctx: TurnContext,
        result: ModelTurnResult,
    ) -> ModelTurnResult | None: ...

    # NEW: called after every tool invocation, including the timeout and
    # exception branches. The loop synthesises a failed ToolExecutionResult
    # so hook state stays consistent regardless of why a call failed.
    async def after_tool_result(
        self,
        ctx: TurnContext,
        call: ToolCall,
        result: ToolExecutionResult,
    ) -> None: ...

    async def after_turn(self, ctx: TurnContext, final_text: str) -> None: ...
```

`AgentRuntime` threads its hook sequence and the per-turn `TurnContext` into
`ReActLoop.run()` so the new callbacks fire at the documented points. `ReActLoop` accepts
the hooks/context as optional parameters; when omitted (current task-mode CLI), the loop
behaves exactly as before.

## Consequences

- Meta-monitor / response-gating logic can now be implemented as a `RuntimeHook` instead
  of being inlined in `EmbodiedAgent`, which unblocks the rest of the neighbour-hook
  migration.
- Memory-recall and relationship hooks can observe every tool call, including failures,
  without having to wrap the registry or the loop themselves.
- A new no-op base class keeps the protocol open to extension; future callbacks can be
  added by overriding `RuntimeHookBase` rather than touching every hook implementation.
- `ReActLoop.run()` gains an optional `context` parameter; existing callers stay
  compatible because hook callbacks are skipped when `context is None`.

## Alternatives Considered

- **Bus-only design (no return value on `after_model_result`).** Rejected because the
  neighbor profile genuinely needs to *rewrite* model output (e.g. softening a meta-monitor
  rejection), not just observe it. A bus-only design would have forced a second public
  rewrite API later.
- **Per-loop callback registration instead of a hook list.** Rejected because the same
  hook instance must observe `before_turn`, `build_context`, `after_model_result`,
  `after_tool_result`, and `after_turn` together; otherwise stateful hooks (drives,
  workspace coalitions) would have to maintain duplicate identity across registrations.

## Non-Goals

- The hook protocol does not (yet) expose tool-call timeouts as configurable per-hook.
  That remains a `ReActLoop` constructor argument.
- The hook protocol does not surface mid-streaming token callbacks. `on_text` stays a
  loop-level parameter for now.
