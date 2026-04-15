#!/usr/bin/env bash
set -euo pipefail

# Operator example for autonomous sessions.
# This file is not required by the runtime; it documents a practical wrapper.

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE_DIR="${HOME}/.familiar_ai"

export FAMILIAR_AI_DESIRES_CONFIG="${ROOT_DIR}/desires.sample.conf"
export FAMILIAR_INTEROCEPTION_MCP_PATH="${STATE_DIR}/interoception.jsonl"
export FAMILIAR_INTEROCEPTION_MCP_MAX_STALENESS=45

# Keep optional continuity notes in the repo root:
# - SOUL.md
# - TODO.md
# - ROUTINES.md

# Continuation protocol used by the agent:
# - DONE
# - CONTINUE:reason
# - DEFER:reason
#
# After 3 chained CONTINUE statuses, the remainder is moved into unfinished
# business automatically and surfaced again on later turns.

# Example allowed-tools gating for unattended runs:
# export TOOLS_MODE="allowlist"
# export ALLOWED_TOOLS="remember,recall,tom,see,look,say"

exec ./run.sh "$@"
