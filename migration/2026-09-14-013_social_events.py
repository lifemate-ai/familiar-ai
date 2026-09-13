"""Social events — one append-only relational timeline.

Relationship shifts, boundaries, permissions, commitments, identity
violations and person-model writes were scattered across mental_state.jsonl,
relationship evidence lists and person_inferences. This ledger gives them a
single typed, queryable timeline (selfhood/sociality substrate, Phase 1).
"""

from __future__ import annotations

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS social_events (
            id TEXT PRIMARY KEY,
            ts TEXT NOT NULL,
            source TEXT NOT NULL,
            kind TEXT NOT NULL,
            person_key TEXT,
            session_id TEXT,
            correlation_id TEXT,
            confidence REAL,
            payload_json TEXT NOT NULL DEFAULT '{}'
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_social_events_ts ON social_events(ts)")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_social_events_person_kind "
        "ON social_events(person_key, kind)"
    )
