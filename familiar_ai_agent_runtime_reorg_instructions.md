# familiar-ai Reorganization Instructions for Codex / Claude Code

## 0. Mission

Reorganize `lifemate-ai/familiar-ai` from an embodied companion-first application into a general-purpose agent runtime / task execution substrate, while preserving the current “neighbor who lives alongside you” behavior as one application/profile built on top of that substrate.

The key product thesis is:

> A neighbor-like AI cannot merely have a persona, memory, and home sensors. It must be able to pursue goals, manipulate tools, recover from failures, checkpoint progress, and execute real tasks over time. “Living another life next to the user” is only credible when the agent has general task competence underneath it.

So the reorganization must not delete the companion architecture. It must invert the dependency direction:

```text
current-ish shape:
    familiar-ai companion app
      ├─ ReAct loop
      ├─ memory
      ├─ model backends
      ├─ coding tools
      ├─ MCP
      ├─ camera / voice / mobility
      └─ neighbor mind modules

new shape:
    familiar-runtime  generic agent/task runtime
      ├─ model adapters
      ├─ tool/capability registry
      ├─ task/workflow engine
      ├─ event/state store
      ├─ memory interfaces
      ├─ scheduler / interrupts / checkpoints
      └─ observability/evals

    familiar-neighbor  companion application/profile
      ├─ GWT / desires / self-state / relationship / social policy
      ├─ camera / voice / mobility capabilities
      └─ neighbor-specific prompts and policies

    familiar-coder / familiar-tasker  optional task-facing profiles
      ├─ filesystem / shell / MCP / web / repo tools
      └─ task-oriented policies and evals
```

The end state should let us run familiar-ai in at least two modes:

1. **Neighbor mode**: the existing embodied companion, with eyes/voice/memory/desires/GWT.
2. **Task mode**: a general agent that can execute coding and operational tasks using tools, plans, checkpoints, and durable task state.

Neighbor mode should become a specialization of the task runtime, not a separate hard-coded loop.

---

## 1. Read this first before editing

Before making changes, inspect these files and write down a short architecture note in your own scratchpad:

- `README.md`
- `CLAUDE.md`
- `AGENTS.md`
- `docs/technical.md`
- `docs/architecture.md`
- `docs/future-model.md`
- `pyproject.toml`
- `src/familiar_agent/agent.py`
- `src/familiar_agent/backend.py`
- `src/familiar_agent/config.py`
- `src/familiar_agent/tools/coding.py`
- `src/familiar_agent/mcp_client.py`
- `src/familiar_agent/tools/memory.py`
- `src/familiar_agent/memory_worker.py`
- `src/familiar_agent/event_bus.py`
- `src/familiar_agent/workspace.py`
- `src/familiar_agent/main.py`
- `tests/test_agent_react_loop.py`
- `tests/test_mcp_client.py`
- `tests/test_memory_worker.py`
- `tests/test_context_management.py`
- `benchmarks/neighbor_eval.py`

Do not start with a broad rewrite. First characterize the current behavior with tests and a dependency map.

---

## 2. Current diagnosis

The repository already contains many ingredients of a generic task agent:

- A model backend abstraction with Anthropic, Gemini, OpenAI-compatible, Kimi, GLM, and CLI-backed models.
- A ReAct loop with tool calls, tool results, streaming output, retry-ish behavior, and interruption handling.
- Built-in coding tools: `read_file`, `edit_file`, `glob`, `grep`, and opt-in `bash`.
- MCP client support for external tool servers.
- SQLite-backed memory, embeddings, semantic recall, memory jobs, and a background worker.
- Event-bus code intended to normalize activity into events.
- Neighbor-specific cognitive layers: relationship, appraisal, social policy, desires, GWT workspace, self-state, prediction, attention schema, default mode, meta monitor.

But these pieces are currently coupled around `EmbodiedAgent` and the companion use case. The main runtime loop mixes:

- LLM backend selection.
- Prompt construction.
- Tool registration and routing.
- Memory recall.
- Relationship and social-policy updates.
- Desire regulation.
- GWT competition.
- ReAct execution.
- TTS/camera/mobility concerns.
- Post-response memory/self-model updates.
- Next-turn cache computation.
- UI callbacks.
- Shutdown behavior.

That coupling makes it hard to turn familiar-ai into a strong general task agent, because the generic task machinery is not a first-class layer. The task substrate should exist independently, and neighbor behavior should plug into it.

---

## 3. Non-negotiable invariants

Preserve these unless an explicit migration plan and tests are included:

1. Existing `familiar` CLI still works.
2. Existing TUI/GUI entry points still work.
3. Existing `.env` variables remain accepted.
4. Existing `ME.md` persona behavior remains accepted.
5. Existing memory DBs remain compatible; every schema change needs a migration.
6. Existing test commands continue to be the merge gate:

```bash
uv run ruff check .
uv run ruff format --check .
uv run --group dev mypy src/familiar_agent
uv run pytest -q
```

7. Do not weaken the coding tool security model. `bash` remains opt-in unless/until a stronger sandbox exists.
8. Do not let neighbor-specific state leak into the generic runtime API.
9. Do not let raw interoception/body metrics leak into normal user-facing text.
10. Do not perform a language rewrite before measurements show a real bottleneck.

---

## 4. Target architecture

Introduce a layered architecture. Names can be adjusted, but keep the dependency direction.

```text
src/
  familiar_runtime/
    __init__.py
    models/
      base.py
      adapters.py
      anthropic.py
      openai_compat.py
      gemini.py
      kimi.py
      glm.py
      cli.py
    tools/
      base.py
      registry.py
      results.py
      sandbox_policy.py
    tasks/
      model.py
      store.py
      planner.py
      executor.py
      checkpoint.py
      scheduler.py
      interrupts.py
    events/
      model.py
      bus.py
      store.py
    memory/
      base.py
      sqlite_store.py
      embeddings.py
      graph.py
    runtime.py
    react_loop.py
    context.py
    observability.py

  familiar_capabilities/
    coding.py
    shell.py
    filesystem.py
    mcp.py
    camera.py
    voice.py
    mobility.py

  familiar_neighbor/
    app.py
    prompts.py
    mind/
      appraisal.py
      attention_schema.py
      concern_engine.py
      default_mode.py
      desires.py
      interoception.py
      meta_monitor.py
      prediction.py
      relationship.py
      scene.py
      self_narrative.py
      self_state.py
      social_policy.py
      workspace.py
    memory_projection.py
    policy.py

  familiar_agent/
    # Compatibility package during migration.
    # Keep old imports working here by re-exporting or wrapping new modules.
```

The exact package names are negotiable, but the principle is not:

- `familiar_runtime` must not import `familiar_neighbor`.
- `familiar_runtime` may import generic interfaces only.
- `familiar_neighbor` may depend on `familiar_runtime` and register hooks/capabilities.
- `familiar_capabilities` should contain reusable tool providers.
- `familiar_agent` should eventually become a compatibility shell / CLI package, not the architecture center.

---

## 5. Core abstractions to introduce

### 5.1 Model backend protocol

Extract a clean protocol from `backend.py`.

```python
from __future__ import annotations
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

@dataclass(slots=True)
class ToolCall:
    id: str
    name: str
    input: dict[str, Any]

@dataclass(slots=True)
class ModelTurnResult:
    stop_reason: str  # "end_turn" | "tool_use" | "error"
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    raw: Any = None

class ModelBackend(Protocol):
    def make_user_message(self, content: str | list[Any]) -> dict[str, Any]: ...
    def make_assistant_message(self, result: ModelTurnResult) -> dict[str, Any]: ...
    def make_tool_results(
        self,
        tool_calls: Sequence[ToolCall],
        results: Sequence["ToolExecutionResult"],
    ) -> list[dict[str, Any]]: ...

    async def stream_turn(
        self,
        *,
        system: str | tuple[str, str],
        messages: list[Any],
        tools: list[dict[str, Any]],
        max_tokens: int,
        on_text: Callable[[str], None] | None,
    ) -> ModelTurnResult: ...

    async def complete(self, prompt: str, max_tokens: int) -> str: ...
```

Refactor existing backend classes to implement this protocol without changing behavior.

Important: preserve provider-specific message serialization and raw assistant round-tripping. Kimi/GLM reasoning content and Anthropic thinking blocks must keep working.

### 5.2 Tool/capability protocol

Create a generic tool protocol independent of neighbor embodiment.

```python
from dataclasses import dataclass, field
from typing import Any, Protocol

@dataclass(slots=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    category: str = "generic"
    risk: str = "low"  # low | medium | high
    timeout_seconds: float = 20.0
    tags: set[str] = field(default_factory=set)

    def to_anthropic_schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

@dataclass(slots=True)
class ToolExecutionResult:
    text: str
    image_b64: str | None = None
    success: bool = True
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

class ToolProvider(Protocol):
    def specs(self) -> list[ToolSpec]: ...
    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult: ...
```

Then implement `ToolRegistry`:

```python
class ToolRegistry:
    def __init__(self) -> None:
        self._providers: list[ToolProvider] = []
        self._routes: dict[str, ToolProvider] = {}
        self._specs: dict[str, ToolSpec] = {}

    def register(self, provider: ToolProvider) -> None:
        ...

    def tool_defs(self, *, profile: str | None = None, allowed_tags: set[str] | None = None) -> list[dict]:
        ...

    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:
        ...
```

Move the hard-coded routing currently in `EmbodiedAgent._execute_tool()` into this registry.

### 5.3 Event model

Promote `event_bus.py` into the generic runtime layer and make events first-class.

Minimum event schema:

```python
@dataclass(slots=True)
class AgentEvent:
    id: str
    run_id: str | None
    task_id: str | None
    turn_id: str | None
    source: str      # user | assistant | tool | model | memory | scheduler | system | sensor
    type: str        # message | tool_call | tool_result | state_update | checkpoint | error | etc.
    payload: dict[str, Any]
    timestamp: float
    salience: float = 0.5
    confidence: float = 1.0
    parent_id: str | None = None
```

The event bus must support:

- Append-only JSONL logging.
- SQLite persistence option.
- Subscription hooks.
- Replay.
- Tests for ordering and replay.

The runtime should emit events for:

- user input
- model request start/end
- tool call start/end
- tool timeout/error
- interrupts
- checkpoints
- task status transitions
- post-turn jobs

### 5.4 Task model

Add a real task substrate.

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    BLOCKED = "blocked"
    WAITING_FOR_USER = "waiting_for_user"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass(slots=True)
class Task:
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.QUEUED
    goal: str = ""
    constraints: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class TaskCheckpoint:
    id: str
    task_id: str
    summary: str
    state: dict[str, Any]
    created_at: float
```

Task runtime requirements:

- Create task.
- Start/resume task.
- Pause/block task with reason.
- Ask user for clarification only when necessary.
- Persist checkpoint after each significant tool/model step.
- Recover from interruption or process restart.
- Mark success/failure with evidence.
- Keep task execution separate from chat history.

### 5.5 Runtime hooks

The generic runtime should expose hook points so neighbor modules can participate without being hard-coded into the ReAct loop.

```python
class RuntimeHook(Protocol):
    async def before_turn(self, ctx: "TurnContext") -> None: ...
    async def build_context(self, ctx: "TurnContext") -> list["ContextBlock"]: ...
    async def after_model_result(self, ctx: "TurnContext", result: ModelTurnResult) -> None: ...
    async def after_tool_result(self, ctx: "TurnContext", call: ToolCall, result: ToolExecutionResult) -> None: ...
    async def after_turn(self, ctx: "TurnContext", final_text: str) -> None: ...
```

Neighbor mode can register hooks for:

- memory recall
- social policy
- appraisal
- desire regulation
- workspace competition
- meta-gating
- relationship updates
- self-state updates

Task mode can register hooks for:

- planning
- task checkpointing
- patch tracking
- test result interpretation
- cost/latency telemetry
- safety policy

---

## 6. Runtime flow after refactor

Target flow:

```text
AgentRuntime.run_turn(input, profile, task_id?)
  1. create TurnContext
  2. emit user/system event
  3. call hooks.before_turn
  4. collect ContextBlocks from hooks
  5. select/budget context blocks
  6. build system prompt from profile + stable runtime rules + context blocks
  7. run ReActLoop
       a. model.stream_turn
       b. if tool_use: registry.call with timeout/sandbox policy
       c. emit events
       d. append tool result messages
       e. handle interrupts
       f. checkpoint task if task_id exists
  8. run response gates
  9. emit final response event
 10. schedule post-turn jobs
 11. return final response
```

The current `EmbodiedAgent.run()` can become a wrapper around this flow.

---

## 7. Prompt/profile separation

Separate prompt content into profiles.

```text
src/familiar_runtime/prompts/
  react_core.md
  tool_rules.md
  task_mode.md

src/familiar_neighbor/prompts/
  embodied_core.md
  social_rules.md
  voice_rules.md
  perception_rules.md
```

The current giant `SYSTEM_PROMPT` should be split into stable reusable pieces:

- generic ReAct rules
- tool-use rules
- task execution rules
- coding/shell safety rules
- embodied rules
- voice/TTS rules
- neighbor/social rules
- theory-of-mind / relational rules
- game/self-check rules

Do not remove the existing behavioral instructions; split them and assemble them by profile.

---

## 8. Memory split

Split memory into generic memory and neighbor projection.

### Generic memory

Responsible for:

- event storage
- embeddings
- semantic recall
- associative links
- working memory
- task checkpoints
- tool outcome traces

### Neighbor projection

Responsible for:

- relationship state
- self-narrative
- affective memory
- social preferences
- unfinished business
- autobiographical continuity

Do not make generic task mode depend on relationship/self-state classes. Instead expose them as optional hooks in neighbor mode.

---

## 9. Coding/task capability upgrade

The current coding tools are a good seed, but task-mode needs stronger operational semantics.

Add or plan these capabilities:

1. `read_file(path, offset?, limit?)`
2. `write_file(path, content)` with safety checks
3. `edit_file(path, old_string, new_string)`
4. `multi_edit_file(path, edits[])`
5. `glob(pattern, path?)`
6. `grep(pattern, path?, glob?, output_mode?)`
7. `bash(command, timeout?)`
8. `run_tests(command?, timeout?)`
9. `git_status()`
10. `git_diff(path?)`
11. `git_apply_patch(patch)` or explicit patch tool
12. `create_task(title, description, acceptance_criteria[])`
13. `checkpoint_task(task_id, summary, state)`
14. `finish_task(task_id, evidence)`

Keep dangerous tools behind policy gates.

For `bash`, add a sandbox policy object even if the first implementation only wraps the current opt-in behavior:

```python
@dataclass(slots=True)
class SandboxPolicy:
    allow_bash: bool = False
    workdir: Path | None = None
    network: str = "inherit"  # inherit | disabled | restricted
    max_timeout_seconds: int = 120
    allowed_commands: set[str] | None = None
    denied_commands: set[str] = field(default_factory=lambda: {"rm -rf /", "shutdown", "reboot"})
```

Do not over-engineer permission UX in the first PR. Just isolate policy from execution.

---

## 10. Language decision: Python vs Rust/Go/other

Do not rewrite familiar-ai wholesale in another language now.

Keep Python for:

- LLM API integration.
- Async orchestration.
- Existing tests.
- ML/embedding ecosystem.
- Hardware libraries currently used by camera/voice/mobility.
- GUI/TUI integration.
- Fast iteration by coding agents.

The likely performance bottlenecks are not pure Python CPU at the moment. They are:

- LLM API latency and additional utility-model round trips.
- Model-specific streaming/tool-call handling.
- Embedding model loading and encoding.
- SQLite/vector scan behavior as memory grows.
- File search/grep over large repositories.
- Shell process management and cancellation.
- Always-on audio/event stream handling.
- Cross-platform subprocess quirks.

Introduce another language only as a sidecar when a measured bottleneck appears.

Preferred sidecar path:

```text
Rust sidecar: familiar-supervisor
  - JSON-RPC over stdio or Unix/TCP socket
  - safe file indexing/search
  - robust process execution with cancellation
  - streaming stdout/stderr
  - task workspace snapshots
  - optional sandbox/resource limits
  - optional event-log ingestion
```

Why Rust first:

- Strong fit for safe filesystem/process tooling.
- Good cross-platform binary distribution.
- Excellent cancellation/resource-control ecosystem.
- Can later embed ripgrep-like search without reinventing it in Python.

Go is also acceptable for process supervision/MCP-like tool serving, but Rust is preferable if file/search/sandbox safety becomes central.

Do not move cognitive modules, prompts, model adapters, or UI into Rust now.

Decision gate for starting Rust sidecar:

- `grep/glob/bash/run_tests` show measurable latency or cancellation failures in real tasks, or
- always-on event/audio processing starts dropping events, or
- repository search/indexing becomes a top latency contributor, or
- we need stronger sandbox guarantees than Python subprocess wrappers can provide.

Before adding Rust, add a benchmark proving the bottleneck.

---

## 11. PR plan

Use small PRs. Each PR should pass all validation commands and preserve user-facing behavior.

### PR 1 — Architecture doc + baseline characterization

Create:

- `docs/task-agent-runtime.md`
- `docs/adr/0001-runtime-core-extraction.md`
- `docs/adr/0002-python-first-sidecar-later.md`

Add tests that characterize current behavior without refactoring:

- `tests/test_agent_react_loop.py` additions for:
  - tool call routing still works
  - tool timeout produces a textual error
  - brief-reply mode limits tools
  - post-response pipeline is spawned, not awaited
- `tests/test_coding_tool.py` additions for:
  - `bash` absent unless enabled
  - `read_file` line numbers
  - `edit_file` rejects non-unique old string
  - `grep` content mode cap behavior

Do not move code in PR 1 except docs/tests.

### PR 2 — Model backend protocol extraction

Create `src/familiar_runtime/models/` and move/extract shared dataclasses/protocols.

Keep `src/familiar_agent/backend.py` as compatibility wrapper initially.

Acceptance:

- Existing backend tests pass.
- Existing imports still work.
- No behavior change in CLI/TUI.

### PR 3 — Tool registry and capability providers

Create:

- `src/familiar_runtime/tools/base.py`
- `src/familiar_runtime/tools/registry.py`
- `src/familiar_capabilities/coding.py`
- `src/familiar_capabilities/mcp.py`

Adapt existing `CodingTool` and `MCPClientManager` to the `ToolProvider` protocol.

Refactor `EmbodiedAgent._all_tool_defs` and `_execute_tool` to use `ToolRegistry` internally, while keeping public behavior unchanged.

Acceptance:

- Existing tool tests pass.
- MCP tool collision behavior is preserved or explicitly tested.
- `bash` opt-in behavior remains unchanged.

### PR 4 — Generic ReAct loop extraction

Create:

- `src/familiar_runtime/react_loop.py`
- `src/familiar_runtime/context.py`
- `src/familiar_runtime/runtime.py`

Move the provider-neutral loop out of `EmbodiedAgent.run()`:

- model.stream_turn
- stop_reason handling
- tool_use execution
- timeout handling
- message append
- interrupt handling
- forced final response after max iterations
- token accounting hooks

Keep neighbor-specific pre/post logic in `EmbodiedAgent` temporarily by calling the generic loop.

Acceptance:

- `EmbodiedAgent.run()` gets smaller.
- Existing agent tests pass.
- Final text behavior remains equivalent for mocked backends.

### PR 5 — Event bus promotion

Move or wrap `event_bus.py` into `familiar_runtime.events`.

Emit events from the generic runtime for:

- turn start
- model result
- tool call start
- tool result
- timeout/error
- interrupt
- turn end

Add replay tests.

Acceptance:

- Event emission is optional/configurable.
- Existing behavior does not depend on event persistence.
- No sensitive raw metrics are emitted to user-facing logs by default.

### PR 6 — Task model and checkpoint store

Create:

- `src/familiar_runtime/tasks/model.py`
- `src/familiar_runtime/tasks/store.py`
- `src/familiar_runtime/tasks/checkpoint.py`
- `migration/<timestamp>_task_runtime.py`

Store tasks and checkpoints in SQLite.

Add a minimal task CLI or internal API:

```python
await runtime.create_task(...)
await runtime.run_task(task_id)
await runtime.checkpoint_task(...)
await runtime.finish_task(...)
```

Acceptance:

- Task can be created, run, checkpointed, resumed, and finished in tests with a fake backend.
- Existing memory DB migration path works.

### PR 7 — Neighbor mode as profile/hooks

Create `familiar_neighbor` package and begin moving neighbor-specific modules there.

Do not move everything at once. Start with profile assembly:

- Neighbor system prompt assembly.
- Neighbor pre-turn hook.
- Neighbor post-turn hook.
- Neighbor tool profile tags.

Keep compatibility imports from `familiar_agent.*`.

Acceptance:

- Existing CLI/TUI/GUI keep working.
- Neighbor eval still runs.
- `EmbodiedAgent` becomes a thin wrapper around `AgentRuntime + NeighborProfile`.

### PR 8 — Task mode CLI

Add one user-facing mode:

```bash
uv run familiar task "inspect this repo and run tests"
```

or

```bash
uv run familiar --task
```

Task mode should:

- not load camera/voice/mobility by default
- load coding + MCP capabilities
- use task prompt/profile
- create a durable task record
- checkpoint after each major step
- emit final summary with files changed and tests run

Acceptance:

- Works with fake backend in tests.
- Does not require hardware dependencies.
- Does not alter neighbor mode.

### PR 9 — Evaluation expansion

Add generic task evals alongside neighbor evals.

Metrics:

- task success
- tool-call success rate
- average steps per task
- retry count
- time-to-first-useful-action
- cost/tokens per task
- checkpoint recovery success
- false interruption / annoyance rate for neighbor mode

Create:

- `benchmarks/task_eval.py`
- `benchmarks/task_scenarios.py`
- `benchmarks/reports/` ignored or generated

Acceptance:

- Eval can run without cloud API using fake backends.
- Neighbor eval remains separate.

### PR 10 — Optional Rust sidecar spike only if benchmark justifies it

Do not start this unless a benchmark shows a bottleneck.

If justified, create:

```text
crates/familiar-supervisor/
  Cargo.toml
  src/main.rs
  src/protocol.rs
  src/files.rs
  src/process.rs
```

Expose JSON-RPC methods:

- `fs.glob`
- `fs.grep`
- `fs.read`
- `fs.edit`
- `proc.run`
- `proc.cancel`
- `git.status`
- `git.diff`

Python integration:

- `src/familiar_capabilities/supervisor.py`
- fallback to Python implementation when sidecar absent

Acceptance:

- Sidecar absent: current behavior works.
- Sidecar present: tests verify same results for search/read/bash subset.
- No mandatory Rust build for normal Python package yet.

---

## 12. Detailed implementation notes

### 12.1 Keep compatibility imports

During migration, preserve old imports by re-exporting:

```python
# src/familiar_agent/backend.py
from familiar_runtime.models.adapters import *
```

or by wrapping only where necessary.

Do not break tests by moving modules without compatibility shims.

### 12.2 Avoid circular imports

Generic runtime must not import neighbor modules.

Bad:

```python
# familiar_runtime/runtime.py
from familiar_neighbor.mind.desires import DesireSystem  # forbidden
```

Good:

```python
class RuntimeHook(Protocol): ...
```

and neighbor registers hooks.

### 12.3 Context budgets

Add a generic context block model:

```python
@dataclass(slots=True)
class ContextBlock:
    source: str
    text: str
    priority: float
    stable: bool = False
    max_chars: int | None = None
```

Use this to replace ad hoc prompt concatenation.

Neighbor mode can produce context blocks from relationship, interoception, workspace, memory, etc.

Task mode can produce context blocks from task goal, plan, recent tool results, file summaries, checkpoints, etc.

### 12.4 Post-turn jobs

Generalize `_spawn_background_task` into a runtime job manager.

```python
class BackgroundJobManager:
    def spawn(self, coro: Coroutine[Any, Any, None], *, name: str) -> None: ...
    async def drain(self, timeout: float) -> None: ...
```

Reuse it for:

- memory materialization
- post-turn self updates
- next-turn cache
- task checkpoint flush
- telemetry flush

### 12.5 Interrupt handling

Keep the current ability to consume queued user interrupts while the agent is running.

Move generic logic to `familiar_runtime.tasks.interrupts` or `react_loop.py`.

Task mode should treat interrupts as:

- high-priority user message
- possible cancellation request
- possible new constraint
- possible clarification answer

Neighbor mode can still phrase it as “respond directly with say() now” when voice mode is active.

### 12.6 ReAct loop result type

The loop should return a structured result, not only final text.

```python
@dataclass(slots=True)
class RunTurnResult:
    final_text: str
    stop_reason: str
    tool_calls: list[ToolCall]
    input_tokens: int
    output_tokens: int
    events: list[str]
    task_id: str | None = None
```

Neighbor wrappers can keep returning `str` for backward compatibility.

### 12.7 Testing strategy

Use fake model backends aggressively.

Fake backend should support scripted turns:

```python
backend = ScriptedBackend([
    ModelTurnResult(stop_reason="tool_use", text="", tool_calls=[ToolCall(...)]),
    ModelTurnResult(stop_reason="end_turn", text="done"),
])
```

This makes runtime behavior testable without API calls.

### 12.8 Observability

Add lightweight per-turn telemetry:

- model name
- input/output tokens
- tool calls
- tool latency
- tool failures
- task checkpoint count
- post-turn job failures
- total turn latency

Do not expose sensitive content unless debug logging is enabled.

---

## 13. Suggested issue breakdown

Create issues or PR descriptions with these titles:

1. `docs(runtime): define generic task-agent substrate for familiar-ai`
2. `refactor(models): extract provider-neutral backend protocol`
3. `refactor(tools): introduce ToolProvider and ToolRegistry`
4. `refactor(runtime): extract generic ReAct loop from EmbodiedAgent`
5. `feat(events): emit replayable runtime events`
6. `feat(tasks): add durable task model and checkpoints`
7. `refactor(neighbor): move companion cognition behind runtime hooks`
8. `feat(task-mode): add non-embodied task execution profile`
9. `test(evals): add task execution benchmark suite`
10. `perf(supervisor): spike Rust sidecar for process/search bottlenecks` only if justified

---

## 14. Definition of done for the reorganization

The reorganization is successful when all of the following are true:

1. `familiar` still launches the existing companion experience.
2. A new task mode can run without camera/voice hardware.
3. The generic runtime has no imports from neighbor-specific modules.
4. Tool routing is handled by a registry, not hard-coded `if/elif` in the main agent.
5. Model backends implement a clear protocol.
6. Task state is durable and can resume after restart in tests.
7. Memory and event storage are reusable by both neighbor and task mode.
8. Neighbor cognition is expressed as hooks/profile layers.
9. Tests cover runtime/tool/task behavior with fake backends.
10. The code is still Python-first, with sidecar work postponed until a benchmark justifies it.

---

## 15. First concrete command sequence

Start with this sequence:

```bash
git checkout develop
git pull
git checkout -b feat/runtime-core-plan
uv sync
uv run ruff check .
uv run --group dev mypy src/familiar_agent
uv run pytest -q
```

Then create docs and baseline tests only. Do not refactor in the first commit.

Suggested first commit:

```bash
git add docs/task-agent-runtime.md docs/adr/0001-runtime-core-extraction.md docs/adr/0002-python-first-sidecar-later.md tests/test_coding_tool.py tests/test_agent_react_loop.py
uv run ruff format .
uv run ruff check .
uv run --group dev mypy src/familiar_agent
uv run pytest -q
git commit -m "docs(runtime): define generic task-agent substrate"
```

---

## 16. Extra instruction for Codex / Claude Code

Work like a careful staff engineer, not like a bulk-edit bot.

For every PR:

1. Read the relevant files first.
2. State the intended dependency direction.
3. Add or update tests before major moves.
4. Make the smallest behavior-preserving extraction possible.
5. Keep compatibility shims.
6. Run targeted tests first, then full validation.
7. Update docs and changelog when behavior changes.
8. In the final report, list:
   - files changed
   - behavior changes
   - compatibility notes
   - tests run
   - follow-up risks

Do not:

- Rename half the repository in one PR.
- Rewrite prompts while extracting runtime code.
- Introduce Rust/Go without a benchmark.
- Make `bash` enabled by default.
- Remove hardware support.
- Collapse neighbor cognition into generic task code.
- Treat “neighbor” as merely a persona prompt.

The intended shape is: general task competence first, neighbor life on top.
