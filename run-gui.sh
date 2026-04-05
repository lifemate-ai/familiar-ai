#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
exec uv run familiar --gui "$@"
