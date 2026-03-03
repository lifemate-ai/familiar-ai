#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ $# -eq 0 ]]; then
  set -- --mode onedir --name familiar-testflight
fi

exec uv run --with pyinstaller python scripts/release_testflight_windows.py "$@"
