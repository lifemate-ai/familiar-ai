#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Create a new SQLite migration script.

Usage:
  scripts/new_migration.sh <name> [--date YYYY-MM-DD] [--dir migration]

Examples:
  scripts/new_migration.sh add_memory_index
  scripts/new_migration.sh "add memory jobs table" --date 2026-03-03
EOF
}

name=""
migration_date="$(date +%F)"
migration_dir="migration"

while (($#)); do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --date)
      shift
      if (($# == 0)); then
        echo "missing value for --date" >&2
        exit 1
      fi
      migration_date="$1"
      ;;
    --dir)
      shift
      if (($# == 0)); then
        echo "missing value for --dir" >&2
        exit 1
      fi
      migration_dir="$1"
      ;;
    --*)
      echo "unknown option: $1" >&2
      usage
      exit 1
      ;;
    *)
      if [[ -n "$name" ]]; then
        echo "multiple names provided: '$name' and '$1'" >&2
        usage
        exit 1
      fi
      name="$1"
      ;;
  esac
  shift
done

if [[ -z "$name" ]]; then
  echo "migration name is required" >&2
  usage
  exit 1
fi

if [[ ! "$migration_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "invalid --date format: $migration_date (expected YYYY-MM-DD)" >&2
  exit 1
fi

slug="$(printf '%s' "$name" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/_/g; s/^_+|_+$//g')"
if [[ -z "$slug" ]]; then
  slug="migration"
fi

mkdir -p "$migration_dir"

max_seq=0
shopt -s nullglob
for path in "$migration_dir/${migration_date}-"*.py; do
  base="$(basename "$path")"
  if [[ "$base" =~ ^${migration_date}-([0-9]{3})(_[a-z0-9_]+)?\.py$ ]]; then
    seq="${BASH_REMATCH[1]}"
    seq_num=$((10#$seq))
    if ((seq_num > max_seq)); then
      max_seq=$seq_num
    fi
  fi
done
shopt -u nullglob

next_seq="$(printf '%03d' "$((max_seq + 1))")"
target="$migration_dir/${migration_date}-${next_seq}_${slug}.py"

if [[ -e "$target" ]]; then
  echo "refusing to overwrite existing file: $target" >&2
  exit 1
fi

cat > "$target" <<'PY'
"""TODO: describe migration."""

from __future__ import annotations

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    """Apply schema/data changes."""
    # Example:
    # conn.execute("CREATE TABLE example (id INTEGER PRIMARY KEY)")
    pass
PY

echo "$target"
