# Selfhood & sociality substrate (kokone-informed)

Goal: make familiar-ai a substrate for agents with identity, sociality, and a
sense of self, borrowing structure from the `kokone` MCP stack (social-core /
sociality-mcp / identity-mcp) without importing any persona strings.

Gap analysis vs. current develop (`RelationshipTracker`, `IdentityCore`,
`PersonModel`, commitments, experience ledger, self-narrative already exist):

| kokone mechanism | familiar-ai today | plan |
|---|---|---|
| Append-only social event log (`SocialEventCreate`) | scattered: mental_state.jsonl, relationship evidence, person_inferences | **Phase 1** — landed (1dce643) |
| Narrative arcs + daybook + self summary | one-sentence self_narrative, experience lessons | **Phase 2** — landed (00e56b0) |
| `who_am_i` identity anchor tool; `evaluate_action` pre-action boundary check | IdentityCore only gates the final reply | **Phase 3** — landed |
| Consent records per person | `set_permission` (coarse) | **Phase 3** — landed |
| Preferences w/ evidence, rituals, tendencies, quiet mode, open loops | present | none |

Invariants (all phases): getattr-guarded wiring, byte-stable prompts when the
layer is empty/disabled, schema changes via timestamped `migration/`, no
persona strings in code, tests first, full gate green.

## Phase 1 — social event ledger (landed: 1dce643)
- `migration/2026-09-14-013_social_events.py`: `social_events(id, ts, source,
  kind, person_key, session_id, correlation_id, confidence, payload_json)` +
  index on (ts), (person_key, kind).
- `familiar_neighbor/mind/social_events.py`: `SocialEvent` dataclass,
  `SocialEventLog` (append / recent / by_person / by_kind / count), kinds as a
  frozenset constant; DB access via `ObservationMemory` connection.
- Emitters: RelationshipTracker trust/intimacy shifts, boundary adds,
  permission sets; CommitmentStore add/complete/snooze; IdentityCore
  violations; PersonModel writes. Emission is best-effort (never raises).
- Tool `social_timeline` (list recent events, optional person/kind filter).
- Tests: migration, log CRUD, emitter wiring, tool.

## Phase 2 — narrative arcs, daybook, self summary (landed: 00e56b0)
- `migration/...-014_narrative_arcs.py`: `narrative_arcs(id, arc_key, title,
  summary, importance, status, created_at, updated_at)`.
- `familiar_neighbor/mind/narrative.py`: `NarrativeStore` (arcs CRUD, bounded
  to 7 active), `Daybook` (`~/.familiar_ai/daybook.jsonl`: per-day events,
  boundary moments, open loops, private reflections, next actions), and
  `build_self_summary()` aggregating arcs + latest daybook + self_narrative.
- Tools `arc_commit` / `arc_review` / `arc_close`; `[Life arcs]` block injected
  next to `[Experience lessons]`; daybook entry written at session end.

## Phase 3 — identity anchor, action evaluation, consent (landed)
- Tool `who_am_i`: returns the IdentityCore statement of held values /
  boundaries (data from seed rows, not code).
- `IdentityCore.evaluate_action(action_kind, text) -> ActionVerdict`
  (allow/deny/override + reasons + safer alternative) reusing the checker
  library; tool `evaluate_action`.
- `RelationshipTracker.record_consent(person, consent_type, value, source)`
  + `consents()`; tool `consent_record`; consent surfaces in the relationship
  context block.
