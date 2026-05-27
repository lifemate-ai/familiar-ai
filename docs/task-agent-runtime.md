# Task Agent Runtime

## Purpose

familiar-ai currently centers on a neighbor-like companion: embodied perception, voice,
memory, desires, relationship state, and a ReAct loop live together in
`familiar_agent.EmbodiedAgent`. The next architecture should keep that experience intact while
making the generic task machinery a first-class substrate.

The intended direction is:

```text
familiar_runtime        # generic model/tool/task/event runtime
  ^
  |
familiar_neighbor       # companion profile, cognition hooks, embodied capabilities
  ^
  |
familiar_agent          # compatibility CLI/package while migration is in progress
```

`familiar_runtime` must not import neighbor-specific modules. Neighbor behavior should plug into
runtime hooks and profiles.

## Current Baseline

The repository already has the ingredients of a task agent:

- Backend adapters in `familiar_agent.backend` with provider-specific message handling.
- A ReAct loop in `familiar_agent.agent` with streaming, tool calls, timeouts, interrupts, token
  accounting, and post-turn background work.
- Reusable coding tools in `familiar_agent.tools.coding`, with `bash` hidden unless
  `CODING_BASH=true`.
- MCP tool discovery and routing in `familiar_agent.mcp_client`.
- SQLite memory, event logging, and a memory worker.
- Neighbor cognition layers such as desires, relationship tracking, self-state, prediction,
  workspace competition, social policy, and default mode.

The coupling problem is that generic loop concerns and neighbor cognition are both orchestrated by
`EmbodiedAgent.run()`. The migration should extract the generic pieces without changing the
existing user-facing companion behavior.

## Target Runtime Shape

The generic runtime should eventually own:

- Model backend protocol and provider adapters.
- Tool provider protocol, tool registry, timeout policy, and sandbox policy.
- ReAct execution loop with structured turn results.
- Event emission, replay, and optional persistence.
- Durable task records, checkpoints, interrupts, and resume behavior.
- Context block selection and prompt/profile assembly.
- Background job management and lightweight observability.

Neighbor mode should eventually provide:

- Prompt/profile blocks for embodied and social behavior.
- Hooks for memory recall, relationship state, appraisal, desires, workspace competition,
  self-state, prediction, and post-turn adaptation.
- Camera, voice, mobility, and neighbor-specific memory projection as optional capabilities.

Task mode should eventually provide:

- Coding, filesystem, shell, MCP, and test-running capabilities.
- Task prompts, checkpoint hooks, patch/test interpretation, and task telemetry.
- No hardware dependency by default.

## Migration Principles

- Keep `familiar` CLI, TUI, GUI, `.env`, `ME.md`, memory DBs, and existing tests compatible.
- Extract protocols and registries before moving large modules.
- Keep compatibility imports in `familiar_agent` while new packages appear.
- Do not enable `bash` by default.
- Do not rewrite prompts while extracting runtime code.
- Do not move cognitive modules into the generic runtime.
- Keep Python as the main implementation until measurements justify a sidecar.

## Current PR Boundary

This PR keeps the extraction conservative but makes the first runtime layer real:

- Add architecture docs and ADRs.
- Add tests that pin current ReAct and coding-tool behavior.
- Add `familiar_runtime` protocols, ToolRegistry, event/task stores, context blocks, job manager,
  and a provider-neutral ReAct loop.
- Add `familiar_capabilities` adapters for coding and MCP.
- Route existing `EmbodiedAgent` tool calls through ToolRegistry while preserving public behavior.
- Add `familiar task ...` as the first non-embodied task-mode entry point.

Large neighbor cognition module moves remain out of scope for this PR; compatibility and behavior
preservation are the guardrails.
