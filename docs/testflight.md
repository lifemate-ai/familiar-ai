# Testflight Distribution Guide

## Goal
Ship a tester-friendly build where:
- First run asks only minimal setup items (persona + camera credentials).
- Testers do not need to obtain API keys.
- Mobility/vacuum controls are disabled.

## Recommended for Tonight
Use a **portable onefile `.exe` zip** (single executable + external `.env`).

Reasons:
- Easiest handoff for non-technical testers.
- No installer friction/UAC surprises.
- Keeps only settings (`.env`) editable outside the executable.

Note:
- Onefile extraction can make cold startup slower than onedir. For two testers this is usually acceptable.

## Build (Windows)

Optional icon asset:
- `assets/app.ico` (already prepared)
- `assets/app.bmp` (preview/reference)
- Override icon path at runtime with env var: `FAMILIAR_APP_ICON=app.ico`

Build package zip in one command:

```bash
./build.sh
```

```bat
build.bat
```

`build-testflight.bat` でも同じ動作です。

Outputs:
- `.release/familiar-testflight/` (ready-to-send folder)
- `.release/familiar-testflight.zip` (send this file)

What this one command does:
1. Generates `.testflight/.env` from your local `.env` / env vars (API key embedded).
2. Builds Windows package with PyInstaller.

If you want faster startup instead of single-file convenience:

```bash
./build.sh --mode onedir --name familiar-testflight
```

```bat
build.bat --mode onedir --name familiar-testflight
```

If you want to run each step manually:

```bash
uv run python scripts/prepare_testflight_env.py --output .testflight/.env
uv run python scripts/build_testflight_windows.py --mode onefile --name familiar-testflight
```

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
