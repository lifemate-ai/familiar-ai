# Changelog

All notable changes to familiar-ai will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
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

### Changed
- Lint and test workflows now run for both `develop` and `main`, matching the new default-branch strategy
- CI now runs the full pytest suite again instead of excluding GUI async stability coverage
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

### Fixed
- `scripts/new_migration.sh` now accepts Windows-style `--dir` paths in Git Bash so cross-platform CI migration tests pass on `windows-latest`
- The app no longer exits before opening setup when `API_KEY` is missing; GUI users are routed into first-run setup and non-GUI users get a clear fallback path
- Realtime STT no longer re-ingests the agent's own speech during or immediately after TTS playback, and repeated echo loops now trigger an automatic reconnect
- Several async tests that relied on `asyncio.get_event_loop().run_until_complete(...)` now run correctly under `uvloop` and in the full CI suite

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
