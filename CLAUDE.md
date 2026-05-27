# familiar-ai — Developer Guide

## Project overview

familiar-ai is an embodied companion agent. It combines:

- a ReAct tool loop
- local SQLite memory
- prediction / workspace / self-state layers
- explicit relationship, appraisal, social policy, and drive regulation
- optional camera, mobility, TTS, STT, GUI, and MCP integrations

The codebase is backend-agnostic. Anthropic is supported, but it is no longer the only runtime path.

## Source tree

```text
src/familiar_agent/
├── agent.py              # Main embodied turn loop
├── appraisal.py          # Low-dimensional affect updates
├── attention_schema.py   # Recent focus / attention state
├── backend.py            # LLM backend protocol + implementations
├── bootstrap.py          # Startup/setup/configured-state handling
├── concern_engine.py     # Active unfinished concerns
├── config.py             # Runtime config objects
├── default_mode.py       # Idle/default-mode memory processing
├── desires.py            # Autonomous drives + drive selection
├── diagnostics.py        # GUI diagnostics and connection tests
├── gui.py                # GTK GUI
├── heartbeat.py          # Continuation/runtime status logic
├── interoception.py      # Interoception providers + semantic pressure
├── main.py               # CLI entry point / mode selection
├── mental_state.py       # Mental-state bus and JSONL snapshots
├── meta_monitor.py       # Metacognitive logging + response gating
├── prediction.py         # Prediction error / agency error
├── relationship.py       # Longitudinal relationship state
├── routines.py           # Quiet-hours / routine config helpers
├── self_narrative.py     # Session-spanning autobiographical narrative
├── self_state.py         # Persistent latent bodily state
├── setup.py              # Setup flow, env migration, validation
├── social_policy.py      # Speech-act classification + response mode
├── sqlite_migrations.py  # Migration runner
├── tools/
│   ├── camera.py
│   ├── coding.py
│   ├── memory.py
│   ├── mic.py
│   ├── mobility.py
│   ├── realtime_stt.py
│   ├── stt.py
│   ├── tom.py
│   └── tts.py
├── tui.py                # Text UI
├── voice_guard.py        # TTS/STT loop prevention
└── workspace.py          # Coalition competition / broadcast
```

## Runtime architecture

The current turn flow in `agent.py` is:

1. ingest user input and tool/scene context
2. collect interoception
3. read prediction state
4. activate memory, working memory, and open episodes
5. update provisional relationship evidence
6. appraise affect
7. choose social policy
8. regulate drives
9. run workspace competition
10. execute the ReAct loop
11. meta-gate the response
12. persist post-turn traces and mental-state snapshots

The old prompt-only social logic is no longer the full story. Deterministic state layers now sit between raw input and response planning.

## Persistence

Primary persistent stores:

- `~/.familiar_ai/observations.db`
  - observations
  - embeddings
  - semantic facts
  - behavior policies
  - revisions
  - episodes
  - episode membership
  - memory activation
  - unfinished business
  - relationship state
- `~/.familiar_ai/mental_state.jsonl`
  - append-only mental-state snapshots
- `~/.familiar_ai/heartbeat_state.json`
  - continuation / carryover status
- `~/.familiar_ai/desires.json`
  - drive levels
- `~/.familiar_ai/self_state.json`
  - latent bodily carryover

Legacy compatibility:

- `~/.familiar_ai/relationship.json`
  - imported once if present, then SQLite becomes authoritative

Schema changes must go through timestamped files under `migration/`.

## Development rules

- Python 3.10+
- Async-first style
- SQLite stays the primary storage
- Prefer deterministic logic and typed dataclasses over giant prompt blobs
- Do not leak raw interoception/body metrics into normal user-facing text
- Keep compatibility for existing memory DBs; add migrations for every schema change

## Validation before merge

Run before opening a PR:

```bash
uv run ruff check .
uv run --group dev mypy src/familiar_agent
uv run pytest -q
```

## Git workflow

- Work from `develop`
- Cut a feature branch before changes
- Open focused PRs into `develop`
- Use Conventional Commits in English

Examples:

```text
feat(memory): add episode compression to recall
fix(agent): gate raw interoception leakage
docs: refresh technical architecture guide
```

## Editing guidance

- When adding a tool, wire all three places:
  - tool implementation
  - agent registration / routing
  - tests
- When changing state or persistence:
  - add a migration
  - add migration coverage
  - update docs
- When changing social behavior:
  - prefer appraisal / social policy / meta gate logic first
  - only extend prompt instructions when state logic is insufficient
