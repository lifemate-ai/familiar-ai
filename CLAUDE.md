# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

familiar-ai is an embodied companion agent. It combines:

- a provider-neutral ReAct tool loop
- local SQLite memory
- prediction / workspace / self-state cognition layers
- explicit relationship, appraisal, social policy, and drive (desire) regulation
- optional camera, mobility, TTS, STT, GUI, and MCP integrations

The codebase is backend-agnostic. Anthropic is supported, but it is one of several
provider adapters — not the only runtime path.

## Commands

```bash
# Run the app (CLI entry point — defined in pyproject [project.scripts])
uv run familiar

# Discover ONVIF/Tapo cameras on the LAN
uv run familiar-discover-cameras

# Body daemon (separate process; see "Body daemon" below)
uv run familiard

# Desktop GUI launchers (TUI stays the default — never change `familiar`'s default surface)
./run-gui.sh   # run-gui.bat on Windows

# Tests (pytest-asyncio; ~1500 tests, no pytest.ini — config lives in pyproject)
uv run pytest -q
uv run pytest -q tests/test_runtime_hooks.py            # one file
uv run pytest -q tests/test_runtime_hooks.py::test_name # one test
uv run pytest -q -k "interrupt"                          # by keyword

# Lint / format / types — the full pre-merge gate
uv run ruff check .
uv run ruff format --check .
uv run --group dev mypy src/familiar_agent src/familiar_runtime src/familiar_capabilities src/familiar_neighbor
```

Optional extras are installed by default via `[tool.uv] default-groups`
(`dev`, `gui`, `camera`, `voice`). `torch` resolves to the CPU wheel index.

## Architecture: four packages, one app

The repo is mid-migration from a single `familiar_agent` monolith toward a
**generic runtime substrate + a persona profile**. Four packages under `src/`:

| Package | Role | Depends on |
|---|---|---|
| `familiar_runtime` | Generic, persona-free substrate: ReAct loop, runtime facade, LLM model adapters (`models/`), tool registry, memory/events/tasks stores, generic prompt fragments | nothing in-repo |
| `familiar_capabilities` | Thin `ToolProvider` adapters wrapping `familiar_agent` tools so the runtime can register them (camera, coding, mcp, memory, mobility, tom, voice) | runtime, agent tools |
| `familiar_neighbor` | The "neighbor" persona on the substrate: `NeighborProfile` (`app.py`), `EmbodiedAgentHook` (`embodied_hook.py`), and all cognition under `mind/` | runtime |
| `familiar_agent` | The legacy/main application: `EmbodiedAgent` turn loop, GUI/TUI, CLI entry, concrete tool implementations, config/setup/backend factories | all of the above |

**Dependency direction is one-way:** `runtime` knows nothing about personas;
`neighbor` and `capabilities` build on `runtime`; `agent` ties everything together.

### The shim pattern (read before editing cognition modules)

Cognition modules were physically moved into `familiar_neighbor/mind/`, but the
old `familiar_agent.<name>` import paths are preserved as **3-line shims**:

```python
"""Compatibility shim — implementation moved to familiar_neighbor.mind.scene."""
from familiar_neighbor.mind.scene import *  # noqa: F401, F403
```

This applies to `scene.py`, `appraisal.py`, `mental_state.py`, `desires.py`,
`prediction.py`, `relationship.py`, `social_policy.py`, and others. **Edit the real
implementation in `familiar_neighbor/mind/`, not the shim.** The shims exist so the
large body of tests and callers importing `familiar_agent.X` keep working — do not
delete them without migrating every caller. `familiar_agent/backend.py` is a similar
re-export surface: provider adapters live in `familiar_runtime/models/`, while
`backend.py` keeps the historical import path plus the config-driven factory
functions (`create_utility_backend`, `create_scene_backend`).

### Runtime substrate: hooks, loop, and the in-progress migration

`familiar_runtime/runtime.py` exposes `AgentRuntime.run_turn(...)`, which drives
`familiar_runtime/react_loop.py`'s `ReActLoop`. Behavior is customized through the
**`RuntimeHook` Protocol** (with a no-op `RuntimeHookBase`). Three hook shapes are
wired and live:

- `mid_turn_inject(ctx, iteration) -> list[ContextBlock]` — injected into the
  per-iteration **system prompt** (not as a user message — appending a user message
  after a tool_result would break role alternation).
- `InterruptSource` (`drain()` / `empty()`) — polled each loop iteration; non-empty
  drains are injected as a user message.
- `RetryDecision` returned from `after_model_result` — appends the assistant turn,
  injects `inject_user_message`, and continues the loop instead of finalizing.

`ReActLoop.run(...)` has a **public signature that must be preserved**. The system
prompt is `str | tuple[str, str]`, where the tuple is `(stable, variable)` — the
Anthropic adapter's `cache_control` depends on this shape. Use `_with_extra_system`
to append to the variable half.

**Thin-wrap (landed):** `EmbodiedAgent.run()` now drives the substrate
`ReActLoop` directly. The four historical inline behaviours ride
`EmbodiedAgentHook` lifecycle methods — coherence retry (`after_model_result` →
`RetryDecision`), TAPE replan (`after_tool_result` result replacement), say()
reminders (`mid_turn_user_messages`), and the embodied interrupt line
(`format_interrupt_message`) — with the `PreparedTurn` carried in
`ctx.metadata["prep"]`. Two adapters in `agent.py` bridge the seams:
`_TurnToolAdapter` (per-turn tool defs + `_execute_tool` routing, so MCP
late-start and the `_tool_timeout_seconds` patch seam stay intact) and
`_InterruptQueueSource` (armed only after the first model call so pre-turn
input is not double-included). Finalisation (meta-gate repair, continuation
status, auto-say, `commit_after_end_turn`) and the forced final response on
max-iterations remain in `run()`. The `run()` public signature is unchanged
and must stay that way.

**Inner loop (live, dark by default).** `familiar_agent/inner_loop.py` drives a
sub-verbal idle workspace between turns; gated by `FAMILIAR_INNER_LOOP`
(default OFF, interval `FAMILIAR_INNER_LOOP_INTERVAL`). `agent._compete_once(cheap=...)`
is the shared workspace-cycle seam — `cheap=True` skips embedding-backed sources
(memory recall + DMN wander) for zero-LLM idle cycles; `_gather_workspace_context`
is a thin wrapper over it. The tick feeds `TrainOfThought`; a sustained salient
focus escalates by **boosting a drive** (`_INNER_SOURCE_TO_DRIVE`, streak+salience
gate, per-source cooldown) consumed by the UI-owned idle chain — the tick never
calls `run()` (no turn lock exists; single-flight is UI-owned). `bind_desires()`
late-binds the UI's DesireSystem; the loop lazy-starts in `prepare_turn`.
Micro-thoughts: a crystallized focus may be verbalized by a dedicated small
model (`INNER_PLATFORM`/`INNER_MODEL`/`INNER_BASE_URL`, local-friendly; falls
back to the utility backend only when separate from main — idle cycles never
burn main-model calls). The monologue re-competes as a `monologue` coalition
with TTL-faded salience; recurrence sources (`train_of_thought`/`monologue`)
never re-crystallize (feedback-loop guard). Cadence is body-modulated
(interoceptive energy scales the tick interval, clamped
`FAMILIAR_INNER_MIN_INTERVAL` (default 5 s) – 120 s). **Dense recurrence**
(`FAMILIAR_INNER_DENSE`, default OFF): idle winners also update the attention
schema (`note_focus`, batched persistence) and re-enter broadcast listeners
(self-state with deferred saves flushed at turn boundaries, plus a drive-nudge
accumulator flushed once per full cycle). Listener REGISTRATION is gated on
the flag — not just the tick call — because listeners fire on the turn path too.

**Body daemon (familiard, separate process, dark by default).**
`familiar_agent/familiard.py` (`uv run familiard`) owns interoception sampling
(payload consumed via the existing `MCPInteroceptionProvider` path), wake
scheduling (due commitments / desire pressure / schedule bands → Unix-socket
wake events), and offline self-state decay (only while no cortex is connected).
**Read-only toward cortex state**: never writes `desires.json`, opens
`commitments.db` in SQLite read-only URI mode, never opens `observations.db`.
Cortex side: `familiar_agent/wake.py` (`WakeListener`, `wait_input_or_wake`) —
gated by `FAMILIAR_DAEMON` (default OFF); a wake only accelerates the idle poll,
every behavioral gate re-checks in the cortex. Daemon config:
`~/.familiar_ai/familiard.conf` + `FAMILIARD_*` env. A contract-identical
**Rust port** lives in `familiard-rs/` (`cargo build --release && cargo test`
there; CI: `.github/workflows/rust.yml`) — keep the two implementations'
payload shape, socket protocol, config keys and probe SQL in lockstep.

### Turn flow (conceptual)

ingest input → interoception → prediction state → activate memory / working memory /
open episodes → relationship evidence → appraise affect → social policy → drive
regulation → workspace competition → ReAct loop → meta-gate response → persist
traces + mental-state snapshot.

### Secretary layer: commitments and proactive reminders

`familiar_runtime/commitments/` is the persona-neutral secretary core: a
`Commitment` (reminder/appointment/promise/followup/task) carries an optional
due time, priority (0-3), and snooze state in a dedicated `commitments.db`
(self-init schema + idempotent `ALTER` migration in `_ensure_columns`, NOT the
`migration/` runner). `CommitmentTool` (`familiar_agent/tools/commitments.py`)
exposes add/list/complete/snooze; due + upcoming items surface passively into
every turn's continuity context, and a `[Today's agenda]` block joins the
first-turn morning reconstruction.

**Proactive reminders** make due commitments fire self-initiated turns from the
three idle loops (REPL `main.py`, TUI `_reminder_tick`, GUI `_process_queue`).
Invariants to preserve when touching these loops:

- The reminder branch sits **before** the `auto_desire` guard — the
  `proactive_reminders` toggle (`FAMILIAR_PROACTIVE_REMINDERS`, default ON) is
  independent of `auto_desire`.
- Idle precedence is user input > reminder > desire > idle
  (`decide_idle_action` in `_ui_helpers.py` is the tested reference
  implementation; the loops inline it).
- `mark_reminded` is called **before** the turn runs, so a mid-turn snooze
  cadence reset survives and error turns still burn a capped slot. Cadence:
  escalating backoff (600s × {1,3}) capped at 3 reminders, then quiet; quiet
  hours (23-7) pass only priority>=2.
- **Self-authored routines** (`routine_store.py`, `~/.familiar_ai/routines.json`;
  tools `routine_commit`/`routine_review`/`routine_drop`) fire by materializing
  commitments inside `should_fire_commitment_reminder` (pass `routine_store=`) —
  one firing path, all the gates above apply unchanged. Guardrails live in the
  STORE (agent interval floor 600s, cap 12, seed rows operator-owned), never in
  the tool wrapper. Autonomous moments are framed by
  `SocialPolicyEngine.decide_autonomous_move()` (a separate axis from the
  reactive `decide()`): quiet hours → private reflection / stay silent, dominant
  desire → act, neither → quietly prepare; the directive is appended to the
  desire turn's `inner_voice` in `prepare_turn`.
- `repl()`'s finally block calls `os._exit(0)` — tests touching it must patch
  `familiar_agent.main.os._exit` or pytest dies silently.

### Social accumulation: person model and learned policy

- `familiar_neighbor/mind/person_model.py` persists ToM inferences per person
  (`person_inferences` table, migration 010). The ToM tool writes back
  successful structured inferences; the accumulated `[Person model]` block is
  injected next to the relationship context. Person keys are canonicalized to
  the companion name (case-insensitive) — keep writes keyed consistently or
  rows silently stop surfacing.
- `SocialPolicyEngine.decide()` consumes `failed_support_patterns` /
  `support_preferences` from the RelationshipTracker (wired in
  `embodied_hook.prepare_turn` via `relationship_learning_inputs`): distress
  acts surface the relational memory and soften; explicit advice requests force
  ToM on with gentler delivery. Defaults keep historical decisions byte-stable.
- **Social event ledger** (`familiar_neighbor/mind/social_events.py`,
  `social_events` table, migration 013): one append-only relational timeline.
  `RelationshipTracker`, `SQLiteCommitmentStore`, `IdentityCore` and
  `PersonModelTracker` each carry a duck-typed `event_log` (default None →
  byte-stable); `agent._init_social_events()` attaches the single
  `SocialEventLog`. Emission is best-effort (never raises); kinds are the
  closed `SOCIAL_EVENT_KINDS` frozenset; retention is bounded (every 100
  appends: drop rows older than `retention_days`=180, cap at `max_rows`=20000).
  Read-only tool: `social_timeline`.
- **Narrative arcs + daybook** (`familiar_neighbor/mind/narrative.py`,
  `narrative_arcs` table, migration 014; `~/.familiar_ai/daybook.jsonl`): the
  plot layer of selfhood. `NarrativeStore` holds at most 7 active arcs (an 8th
  demotes the lowest-importance one to `dormant`); active arcs render as a
  `[Life arcs]` block in the STABLE prompt half next to the experience lessons
  (cached per session, invalidated only by the agent's own `arc_commit` /
  `arc_close`; empty → `""`, byte-stable). `Daybook.append_today` merges one
  record per day, written at session end after the self-narrative
  (`_write_today_daybook`). Arc changes mirror onto the ledger as
  `arc_updated`. Tools: `arc_commit` / `arc_review` / `arc_close` /
  `self_summary` (`build_self_summary`: arcs + latest daybook + narrative).

### Identity layer: values, boundaries, and self-commitments

`familiar_neighbor/mind/identity.py`'s `IdentityCore` makes identity
**load-bearing state**, not prompt text. Assertions (`identity_assertions`
table, migration 011) carry a `kind` (value / boundary / self_commitment), a
first-person `statement`, `non_negotiable`, `confidence`, and a `checker_id`.

- **Checkers are code, persona patterns are data.** A fixed library
  (`agreement_with_request` / `forbidden_phrase` / `keyword_pair` /
  `topic_relevance`) is keyed by `checker_id`; per-assertion regex patterns
  live in `checker_params` (seed/row data), never in engine code. Patterns are
  length-capped and adjacent-quantifier-rejected at compile time (ReDoS guard);
  a bad pattern disables that row, never crashes.
- **The loop** (all in `embodied_hook` + `agent.py`, getattr-guarded so a
  missing/empty `IdentityCore` is byte-stable): `assess()` in `prepare_turn`
  feeds `AppraisalContext.identity_threat` → `AffectiveState.identity_dissonance`
  and the `MentalStateSnapshot.identity` reading; `as_coalition()` competes in
  the workspace (urgent only when something held is at stake). A boundary
  violation in the **final-reply channel** gets a two-tier veto: an in-loop
  `[IDENTITY]` `RetryDecision` re-ask (model refuses in its own words), then a
  `gate_response` `repair_text` backstop. Violations boost the boost-only
  `identity_coherence` drive → a self-initiated reflection turn →
  `resolve_reflection()` relieves the dissonance. Like the coherence gate, this
  guards `end_turn` text, not text already spoken via the `say` tool mid-turn.
- **Self-authorship**: `identity_commit` / `identity_review` tools let the agent
  name its own values. Agent-authored rows can **never** be non-negotiable or
  carry a hard-veto checker — enforced at both the tool and the store layer
  (`upsert_identity_assertion` only lets a `source="seed"` caller write the
  enforcement-critical fields on update). A background honor-check
  (`_maybe_update_identity`) nudges *value* conviction with revision-audited
  evidence.
- **Anchor + pre-action check + consent** (selfhood/sociality Phase 3):
  `IdentityCore.evaluate_action(action_kind, text) -> ActionVerdict` grades a
  *proposed* action with the same checker library (`override` = non-negotiable
  boundary at stake, `deny` = negotiable boundary/value, `allow` otherwise; the
  safer alternative is the row's `repair_text` or statement) and emits
  `action_evaluated` without touching `assess()`/gate state. `IdentityAnchorTool`
  (`who_am_i` / `evaluate_action` / `consent_record`, `IdentityAnchorCapability`)
  renders held rows + active arcs; `RelationshipTracker.record_consent` /
  `consents()` keep per-person consent next to the permission model and add a
  `(consents: …)` line to the relationship context only when one exists.
- **Seeding**: persona content loads from `~/.familiar_ai/identity_seed.json`
  (insert-if-missing by key; `FAMILIAR_AI_IDENTITY_SEED` override;
  `identity.sample.json` is the shipped template). The generic repo carries no
  persona strings — identity lives in the seed/config, not the code.

### Self-model and reality layers (mostly dark by default)

These modules live in `familiar_neighbor/mind/` and are wired through
`embodied_hook.py` / `agent.py`. All are getattr-guarded: an absent or
disabled layer must leave prompts and decisions byte-stable.

- **Consciousness profile** (`consciousness.py`, `FAMILIAR_CONSCIOUSNESS_PROFILE`,
  default OFF): six graded dimensions computed in `_build_mental_snapshot`,
  clamped to [0,1]. **Instrumentation only** — it lands in diagnostics and
  `mental_state.jsonl`, never in the prompt.
- **Reality monitor** (`reality.py`, `FAMILIAR_REALITY_GATE`, default OFF): a
  perception-claim gate. A final reply asserting a fresh observation without a
  present-turn `see()` gets one `[REALITY]` `RetryDecision` re-ask. Pattern
  library is fixed and ReDoS-guarded; it is deliberately conservative (false
  negatives over false positives).
- **Voice gate** (`FAMILIAR_VOICE_GATE`): one in-loop re-ask when a
  conversational turn ends without `say()`. Independent of `auto_say`; aimed at
  small local models.
- **Sleep consolidation**: `should_run_sleep_consolidation()` in
  `_ui_helpers.py` gates `consolidate_memories_async(threshold=0.97)` from the
  TUI/GUI idle paths; once-per-night via `consolidation_state.json`.
- **Self-narrative** (`self_narrative.py`, `~/.familiar_ai/self_narrative.jsonl`):
  one first-person sentence per session, appended post-turn.
- **Concern engine** (`concern_engine.py`, `~/.familiar_ai/active_concerns.json`):
  at most 5 active concerns, decayed every turn, surfaced above a threshold
  with a 2-turn cooldown after prompting.
- **Default-mode wander** (`default_mode.py`): spontaneous memory wandering
  in the inner loop's non-cheap cycles; near-duplicate hits (>0.85) fold.
- **Deferral detector** (`deferral.py`): fixed JA/EN "talk later" patterns
  that become unfinished business; no env gate.
- **Meta-monitor** (`meta_monitor.py`): session-scoped HOT layer recording the
  winning coalition per step and inconsistencies vs. the self-narrative; sync,
  no LLM; only the distilled summary persists (`meta_state.json`).
- **Attention schema** (`attention_schema.py`, `attention_state.json`):
  focus-history self-model; `context_for_prompt()` yields the compact block.
- **Auto-ToM** (`embodied_hook._should_auto_tom` / `_run_auto_tom_background`):
  deterministic cooldown, runs ToM in a background task (<12s) and persists
  structured inferences to the person model.
- **Compact prompt profile** (`PROMPT_PROFILE=compact`, `config.py`): trimmed
  framework for gemma-class local models; long social guidance is dropped
  because the deterministic layers carry it. `<think>` blocks from local
  models are scrubbed in `familiar_runtime/models/openai_compat.py`.

## Persistence

Primary stores under `~/.familiar_ai/`:

- `observations.db` — observations, embeddings, semantic facts, behavior policies,
  revisions, episodes + membership, memory activation, unfinished business,
  relationship state, memory graph, person inferences, identity assertions,
  experience lessons (self-authored standing context, migration 012),
  social events (append-only relational timeline, migration 013),
  narrative arcs (bounded life storylines, migration 014)
- `commitments.db` — secretary commitments (self-init schema, outside the
  `migration/` runner)
- `mental_state.jsonl` — append-only mental-state snapshots
- `daybook.jsonl` — one merged record per day (events, boundary moments, open
  loops, private reflections, next actions); written at session end
- `heartbeat_state.json` — continuation / carryover status
- `consolidation_state.json` — sleep-consolidation once-per-night marker
- `desires.json` — drive levels
- `self_state.json` — latent bodily carryover
- `identity_state.json` — identity dissonance ledger (decay + reflection relief)
- `self_narrative.jsonl` / `active_concerns.json` — self-narrative diary and concern engine state
- `identity_seed.json` — persona identity seed (operator-supplied; insert-if-missing)
- `attention_state.json` — attention-schema focus history (survives restarts)
- `meta_state.json` — previous session's distilled metacognitive summary (the raw
  MetaMonitor step window is deliberately session-scoped and never persisted)
- `relationship.json` — legacy; imported once if present, then SQLite is authoritative

**Every schema change must add a timestamped migration under `migration/`**
(e.g. `2026-04-15-008_memory_graph_runtime.py`) with migration test coverage.
SQLite stays the primary storage.

## Development rules

- Python 3.10+, async-first style
- Prefer deterministic, typed dataclasses over giant prompt blobs
- Do not leak raw interoception / body metrics into user-facing text
- Keep compatibility for existing memory DBs (migrations, not breaking changes)
- When adding a tool, wire all three: implementation (`familiar_agent/tools/` or a
  capability), agent registration / routing, and tests
- When changing social behavior, prefer appraisal / social-policy / meta-gate logic
  first; only extend prompt instructions when state logic is insufficient
- Prompt changes that must stay byte-stable are pinned by SHA-256 in
  `tests/test_prompt_assembly.py` — update the pin only when output legitimately changes

## Git workflow

- Work from `develop`; cut a feature branch before changes; open focused PRs into `develop`
- Conventional Commits in English, e.g. `feat(runtime): wire interrupt polling into ReActLoop`
- Run the full lint / format / mypy / pytest gate green before opening a PR
- Push only the current branch explicitly; never force-push; merging is the user's decision
