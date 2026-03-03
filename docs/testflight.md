# Testflight Distribution Guide

## Goal
Ship a tester-friendly build where:
- First run asks only minimal setup items (persona + camera credentials).
- Testers do not need to obtain API keys.
- Mobility/vacuum controls are disabled.

## Recommended for Tonight
Use a **portable one-folder `.exe` zip** instead of a full installer.

Reasons:
- Faster iteration (rebuild + re-send in minutes).
- Easier rollback for a small trusted cohort.
- Fewer installer-specific failure points.

## Prepare Testflight `.env` (with current API key)

```bash
uv run python scripts/prepare_testflight_env.py --output .testflight/.env
```

This writes:
- `TESTFLIGHT_MODE=true`
- `MOBILITY_ENABLED=false`
- `API_KEY=<copied from current env/.env>`

## Build Suggestion (Windows)

Use PyInstaller one-folder mode and include the generated `.env` beside the executable.

Example command:

```bash
pyinstaller --noconfirm --windowed --name familiar-testflight scripts/familiar_testflight_entry.py
```

Then package:
- `dist/familiar-testflight/` directory
- `.testflight/.env` copied to `dist/familiar-testflight/.env`

Zip that directory and send it.

## First-run Setup Flow (in app)
When `TESTFLIGHT_MODE=true`, GUI shows a setup wizard with two pages:
1. Persona
2. Camera

On save, it writes:
- `.env` camera/name fields
- `TESTFLIGHT_SETUP_DONE=true`
- `MOBILITY_ENABLED=false`
- Persona markdown to `~/.familiar_ai/ME.md`

## After Pilot Stabilizes
If distribution is stable and updates are less frequent, consider moving to an installer (Inno Setup / NSIS).
