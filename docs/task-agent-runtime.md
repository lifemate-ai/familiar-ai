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

## Migration Status

The extraction is landing as a series of small, behaviour-preserving PRs. The current
state of `develop` plus the in-flight branch `feat/runtime-hooks-and-neighbor` is:

| Area | Status | Where it lives |
| --- | --- | --- |
| Generic runtime protocols (ModelBackend, ToolProvider, RuntimeHook, TurnContext) | ✅ | `src/familiar_runtime/runtime.py`, `tools/base.py`, `models/base.py` |
| ReAct loop with event emission, timeouts, hook callbacks | ✅ | `src/familiar_runtime/react_loop.py` |
| Tool registry with profile/tag filtering | ✅ | `src/familiar_runtime/tools/registry.py` |
| Provider adapters split out of monolithic backend.py | ✅ | `src/familiar_runtime/models/{anthropic,openai_compat,kimi,glm,gemini,cli}.py` |
| Durable task store and checkpoints | ✅ | `src/familiar_runtime/tasks/` |
| Event bus + JSONL/SQLite persistence | ✅ | `src/familiar_runtime/events/` |
| Background job manager | ✅ | `src/familiar_runtime/jobs.py` |
| Generic memory store protocol | ✅ (protocol only) | `src/familiar_runtime/memory/base.py` |
| RuntimeHook protocol with `after_model_result` / `after_tool_result` | ✅ | `src/familiar_runtime/runtime.py` (see ADR 0003) |
| Capability adapters (coding, mcp, camera, mobility, voice, tom, memory) | ✅ | `src/familiar_capabilities/` |
| `familiar_neighbor` package skeleton (`NeighborProfile`, mind re-exports) | ✅ | `src/familiar_neighbor/` |
| Task-mode CLI (`familiar task ...`) | ✅ | `src/familiar_agent/main.py` |
| Task evaluation harness (deterministic, no network) | ✅ | `benchmarks/task_eval.py`, `benchmarks/task_scenarios.py` |
| Physical move of cognition modules into `familiar_neighbor.mind` | ⏳ Deferred (compat re-exports in place) | `src/familiar_agent/{appraisal,relationship,workspace,…}.py` |
| `EmbodiedAgent.run()` rewrite to thin `AgentRuntime + NeighborProfile` wrapper | ⏳ Deferred | `src/familiar_agent/agent.py` |
| Hook-based wiring of neighbour cognition into the runtime | ⏳ Deferred | n/a (planned under `feat/neighbor-hooks` follow-up) |
| Concrete `MemoryStore` adapter around `ObservationMemory` | ⏳ Deferred | n/a |
| Prompt stratification into `familiar_runtime/prompts/` and `familiar_neighbor/prompts/` | ⏳ Deferred | n/a |

The deferred items intentionally land in a later PR because they require coordinated
changes to `EmbodiedAgent.run()` (2940 lines today). The current substrate already lets
task-mode callers register hooks, run scripted scenarios, and persist task state without
touching neighbour cognition.

## Validation

Every PR in this series passes the standard guardrails:

```bash
uv run ruff check .
uv run ruff format --check .
uv run --group dev mypy src/familiar_agent src/familiar_runtime
uv run pytest -q
```

In addition, the task evaluation harness can be invoked directly:

```bash
uv run python benchmarks/task_eval.py
uv run python benchmarks/task_eval.py --scenario simple_file_read
uv run python benchmarks/task_eval.py --json reports/task_eval.json
```

The harness uses `ScriptedBackend` so it never makes network calls, making it safe to run
in CI alongside the neighbour evaluation in `benchmarks/neighbor_eval.py`.
