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
- Testflight onboarding flow for GUI (`TESTFLIGHT_MODE=true`) with a two-page setup wizard:
  - Persona page (agent/user names, user profile, agent profile, relationship)
  - Camera page (IP, account, password)
  - Auto-generates `~/.familiar_ai/ME.md` from structured inputs
- Testflight helper scripts:
  - `scripts/prepare_testflight_env.py` to generate distributable `.env` with embedded API key from local environment
  - `scripts/familiar_testflight_entry.py` as a PyInstaller-friendly GUI entrypoint
  - `scripts/build_testflight_windows.py` to package onefile/onedir testflight zips with external `.env`
  - `scripts/release_testflight_windows.py` to run env preparation + build in one command
- `docs/testflight.md` with practical distribution guidance (portable onefile/onedir `.exe` flows)
- Owl-style app icon assets for Windows packaging/runtime (`assets/app.ico`, `assets/app.bmp`)

### Changed
- GUI settings dialog now keeps JP labels fully visible (including short labels like `名`), refreshed the app to a bright, soft, rounded light theme, split first-turn startup status from "thinking", and increased GUI font sizing for readability.
- Mobility initialization now respects `MOBILITY_ENABLED`; in testflight mode it defaults to disabled.

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
