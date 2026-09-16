"""Experience lessons — the agent's self-authored standing context.

An LLM that rewrites its own prompt region mechanically imitates learning
from experience; capacity forces distillation. Lessons are bounded,
tiered (agent-authored vs nightly auto-proposed), and revision-audited —
a self-rewriting prompt region must have an audit trail.
"""

from __future__ import annotations

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS experience_lessons (
            id TEXT PRIMARY KEY,
            lesson_key TEXT NOT NULL UNIQUE,
            lesson_text TEXT NOT NULL,
            tier TEXT NOT NULL DEFAULT 'agent',
            confidence REAL NOT NULL DEFAULT 0.6,
            source TEXT NOT NULL DEFAULT 'agent',
            use_count INTEGER NOT NULL DEFAULT 0,
            last_confirmed_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_experience_lessons_tier "
        "ON experience_lessons(tier, confidence DESC)"
    )
