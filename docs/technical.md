# Technical Background

familiar-ai is an embodied companion architecture. The goal is not prompt-only roleplay, but a closed loop where perception, memory, appraisal, relationship state, drives, and response policy update one another over time.

The current implementation keeps the original async ReAct core and extends it with deterministic state layers.

---

## Turn architecture

The main turn loop lives in `src/familiar_agent/agent.py`.

The pre-response pipeline now follows this order:

1. ingest user input and current scene/tool context
2. collect interoception (`interoception.py`)
3. read prediction state (`prediction.py`)
4. activate memory via semantic recall, associative expansion, and working memory (`tools/memory.py`)
5. update provisional relationship signals (`relationship.py`)
6. appraise low-dimensional affect (`appraisal.py`)
7. choose social policy (`social_policy.py`)
8. regulate drives (`desires.py`)
9. run workspace competition (`workspace.py`)
10. plan and execute the ReAct loop
11. gate the candidate response (`meta_monitor.py`)
12. finalize the reply
13. persist post-turn traces, memories, and mental-state snapshots

The response loop is still ReAct:

```python
for i in range(MAX_ITERATIONS):
    result, raw = await backend.stream_turn(...)
    if result.stop_reason == "end_turn":
        ...
    if result.stop_reason == "tool_use":
        ...
```

What changed is the state preparation around that loop.

---

## Mental State Bus

`src/familiar_agent/mental_state.py`

The mental-state bus is an append-only JSONL trace at:

`~/.familiar_ai/mental_state.jsonl`

It stores typed snapshots rather than raw prompt blobs:

- `InteroceptiveSignal`
- `AffectiveState`
- `SocialState`
- `DriveVector`
- `WorkingMemoryItem`
- `MentalStateSnapshot`

Snapshots are persisted for continuity and debugging, but prompt injection uses only compact summaries. Raw JSON and raw body metrics are intentionally kept out of normal prompt text.

---

## Interoception

`src/familiar_agent/interoception.py`

Interoception is provider-based:

- `NoopInteroceptionProvider`
- `RuntimeInteroceptionProvider`
- `MCPInteroceptionProvider`

`MCPInteroceptionProvider` accepts either a single JSON payload or an append-only
JSONL stream. It reads the freshest valid sample, honors `observed_at` / `timestamp`,
and drops stale payloads instead of recycling old body state.

The provider output is converted into coarse behavioral pressure:

- `need_rest`
- `caution`
- `expressivity`
- `social_receptivity`
- `frustration_bias`
- `quiet_mode`

This pressure modifies affect, social policy, and drive selection. Raw values such as heart rate or CPU usage are internal-only and must not leak into ordinary user-facing text.

---

## Appraisal

`src/familiar_agent/appraisal.py`

Appraisal is a deterministic low-dimensional update step. It integrates:

- user text
- companion mood
- relationship trust/intimacy
- recalled memory salience
- prediction error and agency error
- interoceptive pressure
- blocked drives
- unfinished business load

The affect vector includes:

- `valence`
- `arousal`
- `dominance`
- `uncertainty`
- `attachment_pull`
- `threat`
- `tenderness`
- `frustration`
- `loneliness`

`AffectiveState.as_coalition()` lets strong affective shifts compete in the global workspace.

---

## Social policy

`src/familiar_agent/social_policy.py`

Social behavior is no longer left to a single persona prompt. The social-policy layer classifies the current interaction into a small speech-act taxonomy:

- `bid_for_connection`
- `venting`
- `grief_signal`
- `fatigue_signal`
- `delight_share`
- `request_for_advice`
- `request_for_action`
- `playful_probe`
- `boundary_assertion`
- `conflict_signal`
- `repair_attempt`
- `silence_or_low_presence`
- `meta_conversation`

The engine returns a `SocialPolicyDecision` with:

- response mode
- validation vs problem-solving bias
- whether ToM should be used
- whether relational memory is relevant
- softness / directness / initiative
- memory mention permission
- explicit prohibition on raw interoception leakage

This decision is summarized into the prompt and also consumed by the meta gate.

---

## Relationship model

`src/familiar_agent/relationship.py`
`migration/2026-04-15-009_relationship_state.py`

Relationship state is now stored in SQLite inside the primary observations database.
Legacy `~/.familiar_ai/relationship.json` files are imported on first load for backward
compatibility, but SQLite is the authoritative store.

New state includes:

- trust trajectory
- intimacy trajectory
- repair history
- support preferences
- failed support patterns
- shared rituals
- sensitive topics
- permission model

Each record stores evidence plus confidence and recency metadata where applicable.

---

## Memory graph

`src/familiar_agent/tools/memory.py`
`migration/2026-04-15-008_memory_graph_runtime.py`

SQLite remains the primary memory store.

The memory layer already had:

- observations
- embeddings
- memory events/jobs
- semantic facts
- behavior policies
- revision history
- associative links

The current graph upgrade adds:

- `episodes`
- `episode_memories`
- `memory_activation`
- `unfinished_business`

Implemented APIs include:

- `create_episode`
- `append_to_episode`
- `link_memories`
- `recall_divergent`
- `refresh_working_memory`
- `get_working_memory`
- `consolidate_memories`
- `open_unfinished_business`
- `resolve_unfinished_business`

Recall is now multi-stage:

1. semantic recall
2. associative expansion over linked memories
3. episode compression

Projected semantic/policy memories still keep revision history in `memory_revisions`, so conflicting facts are not silently overwritten.

---

## Desire system 2.0

`src/familiar_agent/desires.py`

The original scalar drive system is preserved, but extended.

Legacy drives remain:

- `look_around`
- `explore`
- `greet_companion`
- `rest`
- `worry_companion`
- `share_memory`

Higher-level drives were added:

- `curiosity`
- `attachment`
- `care`
- `reflect`
- `consolidate`
- `repair`
- `play`
- `self_protect`

Selection now considers more than raw level:

- base level
- context affordance
- schedule multiplier
- social permission
- energy budget
- unfinished business bonus
- per-drive minimum interval

External drive config is supported through a pipe-delimited format inspired by `desires.sample.conf`:

`name | growth_rate_per_second | prompt_text | tags | min_interval_seconds`

---

## Heartbeat and routines

`src/familiar_agent/heartbeat.py`
`src/familiar_agent/routines.py`

Heartbeat runtime provides lightweight session-time autonomy control:

- quiet-hours state
- schedule multiplier
- morning reconstruction notes from optional `SOUL.md`, `TODO.md`, `ROUTINES.md`
- continuation protocol
- unfinished business carryover
- persisted continuation state in `~/.familiar_ai/heartbeat_state.json`

Internal continuation statuses are:

- `DONE`
- `CONTINUE:reason`
- `DEFER:reason`

Continuation depth is capped at 3. Overflow is persisted into unfinished business instead of being allowed to recurse forever.

Example operator-facing config files live at the repository root:

- `desires.sample.conf`
- `schedule.sample.conf`
- `autonomous-action.sample.sh`

---

## Meta-monitor gating

`src/familiar_agent/meta_monitor.py`

The meta monitor still records step-level metacognitive traces, but now also performs deterministic response gating.

Current checks include:

- validation-before-advice violations
- boundary overreach
- contradiction risk
- raw interoception leakage
- emotional mismatch after distress / repair messages

This gate is intentionally lightweight and synchronous. It is a guardrail layer, not another generative planner.

---

## Why this architecture

The guiding idea is simple:

- prompt text can express a personality
- closed-loop state lets that personality become consistent over time

The system now preserves a stronger separation between:

- hidden numeric/internal state
- compact prompt summaries
- user-facing language

That separation matters for both safety and realism. For example, interoception should change behavior, but the agent should not blurt out raw internal metrics.

---

## Related modules still in use

The upgrade preserves and reuses the strongest existing components:

- `workspace.py` for coalition competition
- `self_state.py` for latent bodily carryover
- `self_narrative.py` for autobiographical continuity
- `prediction.py` for surprise and agency error
- `concern_engine.py` for unfinished salience
- `attention_schema.py` for recent focus traces
- `default_mode.py` for idle recall / consolidation
- `tools/tom.py` for explicit Theory of Mind calls

The architecture is still lightweight, local-first, and async-first. SQLite remains the authoritative store.
