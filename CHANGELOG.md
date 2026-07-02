# Changelog

All notable changes to familiar-ai will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Reality monitor (`FAMILIAR_REALITY_GATE`, default off): a reply that claims present-tense perception on a turn that never called `see()` gets one deterministic `[REALITY]` re-ask — look now, or reframe honestly as memory/uncertainty. Fixed EN+JA pattern library with memory-framing exclusions (false negatives preferred over false re-asks), once-latched, exempt for desire/brief turns and camera-less tool surfaces; runs between the identity and voice gates. Plus an epistemic provenance mapping (perceived/recalled/generated, derived from existing coalition/memory tags) and a session-scoped grounding tracker that feeds the consciousness profile's reality-testing dimension
- Consciousness profile (`FAMILIAR_CONSCIOUSNESS_PROFILE`, default off): consciousness rendered as six graded dimensions — wakefulness, access, self-model integrity, integration, reality testing, reportability — computed deterministically from signals the mind layers already produce (interoception, workspace ignition margin, identity dissonance/threat, metacognitive source diversity, prediction errors, voice recency). Strictly instrumentation: the profile surfaces in the GUI status card, the TUI turn summary, and `mental_state.jsonl` (key dropped when dormant — byte-identical logs), and never enters the prompt or the agent's own text
- Prompt profiles (`PROMPT_PROFILE`, default `full`): a `compact` framework prompt for small local models — 66% smaller (11,381 → 3,873 chars), keeping only the critical operational constraints with the voice rule moved to the end (recency position). The long-form social/cognitive guidance it drops (theory-of-mind, validation-before-advice, bid-for-connection, window-of-tolerance, perspective-taking, self-check) is already carried as deterministic state logic by auto-ToM, the social policy engine, the meta-gate, and the identity layer. The `full` profile stays byte-for-byte stable (SHA-pinned)
- Voice gate (`FAMILIAR_VOICE_GATE`, default off): a conversational reply that never called `say()` gets one in-loop `[VOICE]` re-ask so the model itself composes the short line to speak aloud — keeping `say()` as the deliberate voice channel instead of piping the whole reply (stage directions and all) into TTS like `auto_say` would. Aimed at small local models (Ollama gemma4) that write text but forget to speak; models that already call `say()` never trip it. Brief turns (own say-first design) and desire turns (private reflection stays silent) are exempt
- Inner-loop scaffolding (phase 2, part 1): the workspace competition body is factored into a reusable `_compete_once` (with a `cheap` mode that skips both embedding-backed sources), `_gather_workspace_context` becomes a thin byte-stable wrapper, and an `InnerLoop` background driver + `TrainOfThought` / `InnerThought` dataclasses land behind a default-off `FAMILIAR_INNER_LOOP` flag. Nothing runs yet — the tick is a no-op stub; the idle workspace cycle arrives in the next part
- Identity self-authorship (phase 1, part 3): an `identity_commit` tool lets the agent record values and self-commitments it has come to hold, and `identity_review` lists what it holds — but agent-authored assertions can never be non-negotiable and never gain a hard-veto checker (those stay operator/seed-only, a prompt-injection guard). A background honor-check (one bounded utility call per implicated value, off the hot path, only with a dedicated utility backend) nudges value conviction up when a reply honored it and down when it strained it, with revision-audited evidence
- Identity loop wiring (phase 1, part 2): the identity layer now participates in every turn — `assess()` feeds an `identity_dissonance` affect dimension and the mental-state snapshot, a two-tier veto guards boundaries in the final-reply channel (an in-loop `[IDENTITY]` retry lets the model refuse in its own words; the meta-gate replaces a still-violating reply with the assertion's repair text), violations raise a new boost-only `identity_coherence` drive that fires a self-initiated reflection turn through the existing idle machinery, and that reflection relieves the dissonance with a revision-audited reaffirmation; everything stays byte-identical when no identity is held. Like the coherence gate, this guards the `end_turn` reply, not text already spoken via the `say` tool mid-turn
- IdentityCore substrate (phase 1 of the ego/identity layer): values, boundaries, and self-commitments become typed, persisted state (`identity_assertions`, migration 011) with a fixed deterministic checker library (checkers are code, persona patterns are seed data), a dissonance ledger with decay and reflection relief, seed loading from `~/.familiar_ai/identity_seed.json` (insert-if-missing, `identity.sample.json` shipped), revision-audited slow confidence updates, and a workspace coalition that goes urgent only when something held is at stake — not yet wired into the turn loop (next PR)
- LLM fallback for speech-act classification (ADR 0004, accepted): when the regex layer has no signal (pattern fallthrough) or branch order would decide an inversion-risk conflict ({delight, distress, repair, boundary} co-match), one bounded utility call picks the act from the fixed vocabulary; the deterministic layer stays authoritative everywhere else and on any fallback failure
- Runtime substrate extensions toward hosting the embodied turn loop: `after_tool_result` hooks can replace tool results (adaptive replan), new `mid_turn_user_messages` and `format_interrupt_message` hooks, `run_turn` accepts the cache-preserving `(stable, variable)` system-prompt tuple, and `on_action` / `on_image` / `on_tool_result` observer callbacks thread through the ReAct loop
- Secretary layer: commitments (reminders, appointments, promises, follow-ups) with due times, priorities, and snooze in a dedicated store; add/list/complete/snooze tools; due and upcoming items surface in every turn and a `[Today's agenda]` block opens the day
- Proactive reminders: due commitments fire self-initiated turns from REPL/TUI/GUI idle loops, independent of `auto_desire` (`FAMILIAR_PROACTIVE_REMINDERS`, default on), quiet-hours aware (urgent-only at night), with escalating backoff capped at 3 reminders
- Persistent person model: ToM inferences accumulate per person (`person_inferences`) and surface as an accumulated `[Person model]` prompt block with a 7-day staleness cutoff
- Social learning loop: recorded failed support patterns and support preferences now adjust `SocialPolicyEngine.decide()` (surface relational memory and soften on distress; force perspective-taking on advice requests)
- Deterministic perspective-taking: `should_use_tom` turns now actually run the ToM inference (bounded, cooldown-protected) and inject the result instead of relying on the model to call the tool
- Agency boundary: when the agent itself is running low and is asked for work, advice, or repair, the policy instructs honest capacity acknowledgement instead of overpromising
- GitHub Actions-based release automation for the new `develop -> main -> tag` flow, including a manual release PR workflow and an automatic tag/release workflow on `main`
- Bootstrap-based startup recovery for missing or legacy `.env` files, including shared setup persistence and `ANTHROPIC_* -> PLATFORM/API_KEY/MODEL` migration support
- Schema-driven settings metadata that powers both the GUI settings dialog and the first-run setup wizard from one definition
- GUI diagnostics with a persistent readiness/status card, copyable support snapshot, and backend / camera / realtime STT connection tests
- Realtime STT via ElevenLabs Scribe v2 Realtime WebSocket API
  - Always-on, hands-free voice input with VAD auto-commit
  - Works in both REPL (`--no-tui`) and TUI modes
  - Filler word filtering and deduplication
  - Opt-in via `REALTIME_STT=true` in `.env`
  - Coexists with existing batch STT (Ctrl+T / Space PTT)
- Voice guard protection for TTS-driven realtime STT loops, including speak-time gating, echo fingerprint suppression, watchdog reconnects, and manual STT restart controls in GUI/TUI
- Dedicated `run-gui.sh` / `run-gui.bat` launchers for opening the desktop GUI without changing the existing TUI defaults
- Support for full RTSP URLs in `CAMERA_HOST` (enables ATOMCam and other non-standard RTSP paths)
- A dedicated `familiar-discover-cameras` tool that combines WS-Discovery, mDNS/zeroconf, SSDP, and an opt-in TCP fallback scan for Wi-Fi camera setup
- Persistent latent self state driven by workspace broadcasts, with prompt-visible interoception updates and dedicated test coverage
- Action-conditioned prediction with agency-error tracking for `see` / `look` / `walk`, including scene integration and focused tests
- Online temporal-self context during ordinary turns, with resurfaced memories, unresolved-thread prompts, and within-session self-narrative capture
- Lightweight adaptive confidence updates for semantic facts and behavior policies, including revision history for experience-driven value shifts
- Lightweight layered self continuity with inertial proto-self updates, recent intention-result traces, and persistent active concerns
- Freshness-aware MCP interoception ingestion, persisted heartbeat carryover state, SQLite-backed relationship storage with legacy JSON import, and sample autonomy config files for drives / schedule / operator wrappers
- Generic runtime substrate foundations: model/tool protocols, ToolRegistry, runtime event/task stores, a provider-neutral ReAct loop, neighbor profile boundary, and a non-embodied `familiar task ...` entry point

### Changed
- Lint and test workflows now run for both `develop` and `main`, matching the new default-branch strategy
- CI now runs the full pytest suite again instead of excluding GUI async stability coverage
- Camera discovery now browses `_onvif._tcp.local.` via zeroconf, respects RTSP TXT paths when present, and falls back to socket-based local-prefix detection when `ip route` is unavailable
- GUI settings dialog now keeps JP labels fully visible (including short labels like `名`), refreshed the app to a bright, soft, rounded light theme, split first-turn startup status from "thinking", and increased GUI font sizing for readability.
- GUI startup now shows the window before heavyweight agent warmup finishes, and surfaces readiness phases such as setup check, agent init, embedding warmup, MCP connect, and realtime STT connect
- GUI / TUI / REPL setup paths now share the same runtime-oriented env schema, exposing `BASE_URL`, `TOOLS_MODE`, `UTILITY_*`, `SCENE_*`, `REALTIME_STT`, and `FAMILIAR_AUTO_*` consistently
- Local TTS playback now prefers `afplay` on macOS, documents the actual platform-specific fallback chain, and CI now runs the test suite on Ubuntu, macOS, and Windows runners
- Interoception now reflects internal self-state signals in addition to time, uptime, social context, and mood
- Prediction signals now distinguish external surprise from mismatches in the agent's own embodied actions
- Self-narrative entries now record their trigger and suppress duplicate same-day rewrites
- Realtime STT now supervises the websocket transport and reconnects automatically after mid-session disconnects instead of silently stopping after a few turns
- Realtime STT now honors `STT_LANGUAGE` (default `ja`) for ElevenLabs sessions and logs session / transcript payload anomalies instead of failing silently
- Realtime STT now drops bracketed non-speech event tags like `（水の音）` and `（ドアの閉まる音）` before they reach the UI or input queue
- Camera settings now support optional `CAMERA_PTZ_*` overrides, with fallback to the existing `CAMERA_*` values and RTSP URL credentials when stream and PTZ endpoints differ
- Agent replies no longer wait on post-response memory/self-model updates, and TAPE planning is skipped when no separate utility backend is configured
- System prompts now surface at most one active concern and one recent misaligned intention trace, while post-response updates carry those states forward without adding hot-path LLM calls
- Embodied tool routing now goes through the generic ToolRegistry while preserving existing camera, voice, memory, coding, and MCP behavior
- `EmbodiedAgent.run()` is now a thin wrapper around the substrate `ReActLoop`: TAPE replan, coherence retry, interrupt drain, and say() reminders ride `EmbodiedAgentHook` lifecycle methods; finalisation and the forced final response stay in the wrapper, and the public `run()` signature is unchanged

### Fixed
- OpenAI-compatible backends now scrub inline `<think>…</think>` reasoning spans emitted by local reasoning models (gemma, qwen via Ollama): the chain-of-thought no longer leaks into replies or the persisted conversation, a `<tool_call>` the model merely contemplated inside a reasoning span is never executed, and an unclosed `<think>` (budget exhausted mid-reasoning) yields an empty reply instead of raw reasoning text
- Commitment store no longer pins its SQLite connection to the creating thread: in the GUI the agent (and store) are built inside `asyncio.to_thread`, so every commitment write from the event-loop thread (add/complete/snooze tools, reminder bookkeeping, delegated-task follow-ups) raised `ProgrammingError` and was silently swallowed
- Kansai past-tense "〜やった" (e.g. 「散々やった」) no longer classifies as delight; only exclamatory forms (やったー/やった！/やったぜ) celebrate
- `scripts/new_migration.sh` now accepts Windows-style `--dir` paths in Git Bash so cross-platform CI migration tests pass on `windows-latest`
- The app no longer exits before opening setup when `API_KEY` is missing; GUI users are routed into first-run setup and non-GUI users get a clear fallback path
- Realtime STT no longer re-ingests the agent's own speech during or immediately after TTS playback, and repeated echo loops now trigger an automatic reconnect
- Several async tests that relied on `asyncio.get_event_loop().run_until_complete(...)` now run correctly under `uvloop` and in the full CI suite
- Short greeting / acknowledgement / correction turns now stay in a lightweight reply path: they avoid exploratory tool chains, skip heavy prompt prep, and cap the response loop to a fast `say()`-first turn

## [0.1.0] - 2026-02-22

### Added
- ReAct agent loop powered by Claude (Anthropic)
- Wi-Fi PTZ camera support (Tapo / ONVIF)
- USB webcam support
- Robot vacuum control (Tuya)
- ElevenLabs TTS
- Observation memory with semantic search (SQLite + multilingual-e5-small)
- Desire system — autonomous behavior driven by internal drives
- ME.md persona file — give your familiar a name and personality
- CLI REPL (`uv run familiar`)
