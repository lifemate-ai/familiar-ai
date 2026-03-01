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
