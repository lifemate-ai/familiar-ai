#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

uv run --with pyinstaller python scripts/build_windows.py "$@"
