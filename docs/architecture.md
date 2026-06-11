# familiar-ai Architecture — Neighbor Intelligence Stack

This document maps familiar-ai's cognitive architecture to the Neighbor Intelligence Stack (NIS) design framework.

## Design Philosophy

Neighbor-like behavior emerges not from response quality alone, but from:
- **Temporal continuity** — the agent lives in time, not just in chat turns
- **Relational memory** — it remembers who you are, not just what you said
- **Intervention restraint** — knowing when to stay silent is as important as knowing what to say

## Layer Mapping

### Layer A: Event Ingestion → `familiar_runtime.events` + legacy `event_bus.py`

Runtime/task execution now uses `familiar_runtime.events.AgentEvent`:

```
AgentEvent(id, run_id, task_id, turn_id, source, type, payload, timestamp,
           salience, confidence, parent_id)
```

This supports JSONL logging, SQLite persistence, subscriptions, and replay for task/runtime
activity.

Neighbor intelligence still has the legacy canonical `Event` shape available in
`src/familiar_agent/event_bus.py`:

```
Event(source, entity, payload, timestamp, salience, confidence, affect)
```

Sources: text, vision, audio, bio, device, system, memory, action.
JSONL append-only logging with replay support remains available.

### Layer B: State Tracker → `self_state.py` + `scene.py` + `prediction.py`

**self_state.py** — 6-dimensional latent state vector:
- arousal, fatigue, social_pull, sensor_confidence, unresolved_tension, focus_stability
- Updated per-turn from workspace broadcast
- Exponential settling toward baseline

**scene.py** — Entity-level world model:
- Tracks what/who is present via LLM entity extraction
- Emits appeared/disappeared events
- Feeds prediction error computation

**prediction.py** — Free-energy principle prediction engine:
- Tracks P(entity) via exponential moving average
- Computes external_surprise and agency_error
- High prediction error lowers workspace ignition threshold

### Layer C: Memory System → `tools/memory.py` + `relationship.py`

**Episodic memory** — SQLite + multilingual-e5-small embeddings:
- Observations (what I saw), feelings (what I felt), conversations
- Semantic search with keyword fallback
- Importance decay, near-duplicate detection, supersession

**Semantic memory** — Derived from episodic:
- Semantic facts (general truths, self-model)
- Behavior policies (action tendencies with confidence tracking)

**Relational memory** — `relationship.py`:
- Companion tendencies (recurring patterns)
- Preferences (likes/dislikes)
- Boundaries (things to avoid)
- Session/conversation counting, days-together tracking
- Support preferences and failed support patterns feed back into social
  policy decisions (learned validate-first, advice aversion)

**Person model** — `familiar_neighbor/mind/person_model.py`:
- ToM inferences accumulate per person (states + confidence + chosen policy)
- Surfaced as an accumulated-impressions prompt block (7-day staleness cutoff)
- Written deterministically: flagged turns run the ToM inference themselves

**Working memory** — Recent context + workspace coalitions

### Layer D: Intervention Engine → `concern_engine.py` + `desires.py` + `intervention_policy.py` + `workspace.py`

**concern_engine.py** — Active unresolved concerns with decay:
- Categories: general, agency, companion, curiosity, affect
- Intensity decay (6%/turn + 1.5% leak)
- Cooldown (won't repeat same concern within 2 turns)
- Soothing (positive signals reduce concern intensity)

**desires.py** — Autonomous motivation system:
- 6 drives: look_around, explore, greet_companion, rest, worry_companion, share_memory
- Circadian modulation (night suppresses exploration)
- Drive suppression (high rest suppresses active drives)
- Decay on satisfaction

**intervention_policy.py** — Annoyance guard:
- Cooldown (minimum 2min between autonomous interventions)
- Rate limiting (max 10/hour)
- Uncertainty-based silence (high uncertainty → observe more)
- Night suppression
- Companion presence check

**workspace.py** — Global Workspace Theory (GWT):
- Coalitions from all subsystems compete for broadcast
- Score = activation × (0.4×urgency + 0.3×novelty + 0.3)
- Ignition threshold modulated by prediction error
- Winner's context injected into LLM prompt

**Commitments / proactive reminders** — `familiar_runtime/commitments` + idle-loop wiring:
- Due-time promises (reminders, appointments, follow-ups) with priority and snooze
- Fire self-initiated turns from REPL/TUI/GUI idle loops, independent of desires
- Quiet hours pass urgent-only; escalating backoff goes quiet after 3 reminders
- Passive surface every turn + `[Today's agenda]` on the first turn of the day

**Delegated background tasks** — `tools/delegation.py`:
- `delegate_task` spawns an independent non-embodied task-mode `AgentRuntime`
  (same construction as `familiar task`, minus MCP) in a background asyncio task
- Conversation continues unblocked; at most 2 delegated tasks run at once
- Completion/failure creates a *due* follow-up commitment, so the proactive
  reminder machinery delivers the report even after the companion stepped away
- `check_delegated_tasks` lists running and recent results

### Layer E: Expression → `agent.py` ReAct loop + `tools/tts.py`

**ReAct loop** — Up to 50 iterations per turn:
- LLM generates text or tool calls
- TAPE planning (lightweight, heuristic-based replanning)
- Mood persistence (emotional inertia, ~2.3min half-life)
- Auto-say: if model writes text but never called say(), speak aloud

**Deferred post-response pipeline** — Background after response:
- Memory save, self-model update, curiosity detection
- Scene tracking, concern updates, self-state updates
- Pre-compute next turn's plan + workspace context (cached)

## Additional Cognitive Modules

### Attention Schema (`attention_schema.py`)
Graziano's Attention Schema Theory — models the agent's own attention process.
Detects focus shifts and generates self-reports.

### Default Mode Network (`default_mode.py`)
Activates when workspace is idle. Spontaneously recalls memories and finds near-duplicates for consolidation.

### Meta Monitor (`meta_monitor.py`)
Higher-Order Theory (HOT) — tracks what workspace source won, what action was taken, and confidence. Detects narrative-behavior inconsistency.

### TAPE Planning (`tape.py`)
Adaptive planning inspired by arxiv:2602.19633.
Plan generation before loop + heuristic replanning on blocked observations.

## Performance Optimizations

1. **Embedding query cache** — LRU cache (128 entries) on _EmbeddingModel prevents redundant encode calls
2. **Heuristic TAPE replanning** — Keyword-based blocked detection replaces 2 LLM calls per tool use
3. **Optional coherence check** — Disabled by default (FAMILIAR_COHERENCE_CHECK=1 to enable)
4. **Lazy MCP initialization** — Background async startup, tools become available as servers connect

## Generic Runtime Layer

In parallel with the neighbour stack, the repository now hosts a generic agent runtime
that the same neighbour code is migrating onto. Documented in detail in
`docs/task-agent-runtime.md`; in shape:

```
familiar_runtime/          # provider-neutral substrate
├── models/                # ModelBackend protocol + provider adapters
├── tools/                 # ToolProvider/ToolRegistry + LegacyToolProvider
├── tasks/                 # Task model, SQLiteTaskStore, checkpoints
├── events/                # AgentEvent, EventBus, EventStore
├── memory/                # MemoryStore protocol (adapter pending)
├── react_loop.py          # Generic ReAct loop with hook callbacks
├── runtime.py             # AgentRuntime + RuntimeHook + RuntimeHookBase
├── context.py             # ContextBlock + budgeted selection
└── jobs.py                # BackgroundJobManager

familiar_capabilities/     # ToolProvider adapters around legacy tools
├── coding.py, mcp.py
├── camera.py, mobility.py, voice.py, tom.py, memory.py

familiar_neighbor/         # companion profile boundary
├── app.py (NeighborProfile)
├── prompts.py
└── mind/                  # compatibility re-exports of cognition modules
```

Hooks register with `AgentRuntime` and participate in five lifecycle points:
`before_turn`, `build_context`, `after_model_result` (may rewrite the model output),
`after_tool_result` (fires for success / timeout / exception), and `after_turn`. See
`docs/adr/0003-runtime-hook-protocol.md` for the rationale.

## Future: Chronos-Neighbor Model

The long-term vision is to replace the transcript-centric LLM core with event/state-centric temporal relational models. See `docs/future-model.md` for the staged transition plan.
