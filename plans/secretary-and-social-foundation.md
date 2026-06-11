# familiar-ai foundation work — secretary capability + social feedback loops

## Goal (user-set)

> Make the foundation behave more human-like and socially capable, and add
> task-execution agent capability — especially secretary-like behavior.

## Baseline analysis

### What already existed
- **Sociality (`familiar_neighbor/mind/`)**: appraisal (PAD affect) / social_policy
  (17 speech acts × 13 response modes) / relationship (trust/intimacy +
  tendencies/boundaries/rituals) / meta_monitor (response gate) / workspace (GWT
  competition) / tom (ToM tool) / scene (world model). Rich, but a **one-way flow**
  (input → appraise → decide → output).
- **Tasks**: `familiar_runtime/tasks/` (Task + checkpoints, own `runtime_tasks.db`,
  self-init schema). Task-mode CLI only.
- **Unfinished threads**: `ConcernEngine` (affective topics, auto-decay, JSON) and
  `unfinished_business` (memory DB, up to 3 surfaced per turn).

### Gaps
1. **No secretary core**: nothing held due-dated, prioritized commitments and
   *proactively* spoke up when they came due. Tasks have no due/priority and never
   reach the prompt.
2. **The social learning loop never closed**: `relationship.failed_support_patterns`
   was recorded but `social_policy.decide()` never consulted it.
3. **No accumulated person model**: ToM re-inferred from scratch every call.

## Approach

- Secretary capability lives in the **persona-neutral substrate** →
  `familiar_runtime/commitments/` (own self-init DB, following the `tasks/` pattern).
- Sociality work is **wiring inside the existing mind/ layer** (deterministic logic
  first; avoid growing the prompt).
- Each phase ships PR-sized with the full gate green. TDD (RED → GREEN).

---

## Phase 1 — Commitment store (secretary core) ✅

`src/familiar_runtime/commitments/`: `Commitment`
(reminder/appointment/promise/followup/task; due_at, priority 0-3, snooze, person)
+ `SQLiteCommitmentStore` (list_due / list_upcoming / list_open, due+priority
ordering, snooze). 9 tests.

## Phase 2 — Tool + capability + wiring + surface ✅

`CommitmentTool` (add/list/complete/snooze; relative-minutes and ISO due times) +
`CommitmentCapability`; constructed and registered in `agent.py`; due + upcoming
items surface into the turn continuity context in `embodied_hook.py`. 13 tests.

## Phase 3 — Proactive reminders ✅

User-locked decisions: independent toggle (`FAMILIAR_PROACTIVE_REMINDERS`, default
ON) / quiet hours pass only priority>=2 / escalating backoff (base 600s × {1,3})
capped at 3 reminders, then quiet while still surfacing passively.

- model: `last_reminded_at` / `reminder_count` / `due_for_reminder()` (backoff+cap)
- store: idempotent `_ensure_columns()` ALTER migration / `list_due_for_reminder` /
  `mark_reminded` (targeted UPDATE) / snooze resets the cadence
- config: `AgentConfig.proactive_reminders` + settings schema (advanced/bool)
- i18n: `reminder_impulse` (en/ja; other locales fall back to en); instructs the
  model to call complete/snooze after delivering
- `_ui_helpers`: `should_fire_commitment_reminder` (pure gate:
  running/pending/idle-gap/quiet-priority) / `commitment_reminder_prompt` /
  `decide_idle_action` (reference implementation of the idle precedence)
- wired into all three idle loops (REPL / TUI `_reminder_tick` / GUI) — each
  **before** the `auto_desire` guard
- tests +33 (store cadence, legacy-DB migration, all gate branches, config
  independence, per-loop wiring integration, mark-before-run pinned)

**Multi-agent adversarial review (4 dimensions × verification) → 10 confirmed
findings, all fixed:**
- `mark_reminded` moved **before** the turn (a mid-turn snooze cadence reset
  survives; error turns still burn a capped slot → flapping backends self-limit)
- TUI double-`agent.run` race: `_process_queue` re-queues input dequeued while an
  autonomous turn runs (absorbed via interrupt_queue)
- REPL: reminder gate + turn wrapped in try/except (a bare error used to die
  silently via the finally `os._exit(0)`); `last_interaction_time` updated after
  reminder turns (no back-to-back desire fires)
- GUI/TUI tick bodies exception-guarded (a sqlite error can't kill the idle loop)
- `due_for_reminder` index clamped + inconsistent-state test
- `decide_idle_action` docstring corrected to reality
- post-fix adversarial verification 7/7 resolved; completeness residuals
  (mark guard / GUI mark-before-run pin / clamp test) also closed

---

## Phase 4 — Persistent person model (ToM accumulation) ✅

**Problem**: the ToM tool produced structured JSON
`{evidence, inference[{state,confidence}], policy}` and threw it away after
formatting (only `_last_policy` kept, in-memory).

**Design** (follows RelationshipTracker persistence: lazy conn + WAL +
apply_migrations):
- migration 010: `person_inferences` table (id, person, state, confidence,
  evidence_json, policy, source, created_at ISO) in the shared observations.db
- **new** `familiar_neighbor/mind/person_model.py` `PersonModelTracker`:
  `record_inference` / `recent(person, n)` / `context_for_prompt(person)` →
  `[Person model]` block (recent states + confidence + last chosen approach;
  7-day staleness cutoff)
- `ToMTool`: writes back successful parsed inferences (optional dependency; a
  writeback failure never affects tool output); person keys canonicalized to the
  companion name (case-insensitive) + COLLATE NOCASE reads
- `agent.py`: constructs the tracker, injects the block next to the relationship
  context; `close()` also closes the person-model and commitment stores
- tests: tracker CRUD / prompt rendering / migration / writeback isolation /
  canonicalization / agent surface

## Phase 5 — Closing the social learning loop ✅

`failed_support_patterns` / `support_preferences` (recorded but never consulted)
now feed `SocialPolicyEngine.decide()`. Deterministic adjustment
`_apply_relationship_learning`:
- on advice-failure history (advice/solution/正論/説教 markers) or a
  validate-first support style:
  - distress acts (venting/fatigue/grief/conflict) →
    `should_recall_relational_memory=True` (the relational context renders the
    failed patterns, so the model actually sees what failed before) + softness up
  - explicit advice requests → still honored, but `should_use_tom=True` with
    gentler delivery (action requests deliberately NOT adjusted)
- `relationship_learning_inputs()` absorbs the tracker's stored item shapes
  (style / pattern|evidence), pinned by a contract test
- wired into `embodied_hook.prepare_turn`
- tests +7 (no-history invariance, JP/EN markers, non-firing on unrelated
  patterns, contract)

---

## Validation (end of every phase)

```bash
uv run ruff check .
uv run ruff format --check .
uv run --group dev mypy src/familiar_agent src/familiar_runtime src/familiar_capabilities src/familiar_neighbor
uv run pytest -q
```

## Status

- [x] Phase 1: commitment store + tests
- [x] Phase 2: tool + capability + wiring + surface + tests
- [x] Phase 3: proactive reminders (independent toggle, quiet hours, escalating
  backoff+cap, three-loop wiring, all 10 review findings fixed)
- [x] Phase 4: person model (person_inferences + PersonModelTracker + ToM
  writeback + prompt surface)
- [x] Phase 5: social learning loop (failed patterns → decide() adjustment,
  contract-tested)

Shipped as **PR #175** (merged) with the agenda block, staleness cutoff, and
CLAUDE.md updates. Follow-up round (deterministic ToM, agency boundary,
deferred-topic capture, 4-round classifier audit, ADR 0004) shipped as **PR #176**;
the dangling memory-link fix as **PR #177**.
