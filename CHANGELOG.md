# Changelog

All notable changes to familiar-ai will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Realtime STT via ElevenLabs Scribe v2 Realtime WebSocket API
  - Always-on, hands-free voice input with VAD auto-commit
  - Works in both REPL (`--no-tui`) and TUI modes
  - Filler word filtering and deduplication
  - Opt-in via `REALTIME_STT=true` in `.env`
  - Coexists with existing batch STT (Ctrl+T / Space PTT)
- Support for full RTSP URLs in `CAMERA_HOST` (enables ATOMCam and other non-standard RTSP paths)
- Persistent latent self state driven by workspace broadcasts, with prompt-visible interoception updates and dedicated test coverage
- Action-conditioned prediction with agency-error tracking for `see` / `look` / `walk`, including scene integration and focused tests
- Online temporal-self context during ordinary turns, with resurfaced memories, unresolved-thread prompts, and within-session self-narrative capture
- Lightweight adaptive confidence updates for semantic facts and behavior policies, including revision history for experience-driven value shifts

### Changed
- GUI settings dialog now keeps JP labels fully visible (including short labels like `名`), refreshed the app to a bright, soft, rounded light theme, split first-turn startup status from "thinking", and increased GUI font sizing for readability.
- Interoception now reflects internal self-state signals in addition to time, uptime, social context, and mood
- Prediction signals now distinguish external surprise from mismatches in the agent's own embodied actions
- Self-narrative entries now record their trigger and suppress duplicate same-day rewrites
- Realtime STT now supervises the websocket transport and reconnects automatically after mid-session disconnects instead of silently stopping after a few turns

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
