# ADR 0001: Extract a Generic Runtime Core Incrementally

## Status

Accepted

## Context

familiar-ai began as an embodied companion application. Its main loop now also contains the pieces
needed for a general task agent: model backends, tool calls, coding tools, MCP integration,
timeouts, interrupts, memory, and post-turn jobs.

The same loop also coordinates neighbor-specific cognition: relationship state, appraisal, social
policy, desires, workspace competition, prediction, self-state, and embodied behavior. This makes it
hard to run familiar-ai as a durable task executor without loading companion assumptions.

## Decision

Extract a generic runtime core in small behavior-preserving PRs.

The dependency direction will be:

```text
familiar_runtime  <-  familiar_neighbor  <-  familiar_agent compatibility layer
```

`familiar_runtime` will define generic model, tool, context, event, task, checkpoint, and hook
interfaces. `familiar_neighbor` will register companion prompts, hooks, and embodied capabilities on
top of that runtime. `familiar_agent` will keep existing imports and entry points working during the
migration.

The first PR will add documentation, characterization tests, the initial generic runtime package,
ToolRegistry-backed routing, durable event/task stores, and a minimal task-mode CLI. Larger neighbor
cognition moves will remain behind compatibility boundaries.

## Consequences

- Runtime extraction can proceed behind tests without changing the companion UX.
- Neighbor cognition remains a specialization, not a set of hidden dependencies inside generic task
  APIs.
- Compatibility shims are required until callers and tests move to the new packages.
- Some duplication may temporarily exist while modules are wrapped or re-exported.

## Non-Goals

- No large package rename in one PR.
- No prompt rewrite as part of runtime extraction.
- No memory schema change without migration.
- No new permission model for `bash`; preserve the current opt-in behavior until sandbox policy is
  isolated.
