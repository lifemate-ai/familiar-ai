"""ExplorationTracker — ICL-driven novelty-aware exploration.

Inspired by EMPO² (MSR, 2026): instead of gradient updates, we inject
exploration history into the LLM's context (in-context learning) so that
the model autonomously steers toward unexplored directions.

The pan/tilt deltas from Tapo camera moves are:
  left  → pan_delta = +degrees/180   (positive x = physical LEFT)
  right → pan_delta = -degrees/180
  up    → tilt_delta = -degrees/90   (negative y = physical UP)
  down  → tilt_delta = +degrees/90
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .workspace import Coalition


# Directions that the camera can face
_DIRECTIONS = ("left", "right", "up", "down")
_PAN_DELTA = {"left": 1.0, "right": -1.0}
_TILT_DELTA = {"up": -1.0, "down": 1.0}


@dataclass
class ExplorationRecord:
    timestamp: str
    direction_label: str  # left | right | up | down | center
    pan_accum: float
    tilt_accum: float
    novelty: float | None = None  # filled after observation is saved


class ExplorationTracker:
    """Track camera exploration history within a session.

    Enables ICL-based exploration: by injecting this context into the
    system prompt, the LLM naturally favors under-explored directions.
    In-memory only — no persistence needed (session-scoped state).
    """

    def __init__(self) -> None:
        self._records: list[ExplorationRecord] = []
        self._pan_accum: float = 0.0
        self._tilt_accum: float = 0.0

    def record_move(self, direction: str, degrees: int) -> None:
        """Record a camera movement. Called whenever 'look' tool is used."""
        direction = direction.lower()
        pan_delta = _PAN_DELTA.get(direction, 0.0) * (degrees / 180.0)
        tilt_delta = _TILT_DELTA.get(direction, 0.0) * (degrees / 90.0)
        self._pan_accum += pan_delta
        self._tilt_accum += tilt_delta

        label = direction if direction in _DIRECTIONS else "center"
        self._records.append(
            ExplorationRecord(
                timestamp=datetime.now().strftime("%H:%M"),
                direction_label=label,
                pan_accum=self._pan_accum,
                tilt_accum=self._tilt_accum,
            )
        )

    def record_novelty(self, novelty: float) -> None:
        """Fill novelty score into the most recent record after observation."""
        if not self._records:
            return
        self._records[-1].novelty = novelty

    def unvisited_hint(self) -> str:
        """Return a natural-language hint about under-explored directions."""
        if not self._records:
            return ""

        counts: dict[str, int] = {d: 0 for d in _DIRECTIONS}
        for r in self._records:
            if r.direction_label in counts:
                counts[r.direction_label] += 1

        max_count = max(counts.values())
        if max_count == 0:
            return ""

        unvisited = [d for d, c in counts.items() if c == 0]
        rare = [d for d, c in counts.items() if 0 < c <= max_count // 2]

        candidates = unvisited or rare
        if not candidates:
            return ""

        directions_str = ", ".join(candidates)
        return f"Unexplored directions: {directions_str} — consider looking there."

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    @staticmethod
    def init_schema(conn: sqlite3.Connection) -> None:
        """Create exploration_state table if absent (idempotent)."""
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exploration_state (
                id           INTEGER PRIMARY KEY CHECK (id = 1),
                pan_accum    REAL    NOT NULL DEFAULT 0.0,
                tilt_accum   REAL    NOT NULL DEFAULT 0.0,
                records_json TEXT    NOT NULL DEFAULT '[]',
                saved_at     TEXT    NOT NULL
            )
            """
        )
        conn.commit()

    def save_to_db(self, conn: sqlite3.Connection) -> None:
        """Upsert current state to the DB (single-row table, id=1)."""
        records_json = json.dumps([asdict(r) for r in self._records])
        conn.execute(
            """
            INSERT INTO exploration_state (id, pan_accum, tilt_accum, records_json, saved_at)
            VALUES (1, ?, ?, ?, datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                pan_accum    = excluded.pan_accum,
                tilt_accum   = excluded.tilt_accum,
                records_json = excluded.records_json,
                saved_at     = excluded.saved_at
            """,
            (self._pan_accum, self._tilt_accum, records_json),
        )
        conn.commit()

    def load_from_db(self, conn: sqlite3.Connection) -> None:
        """Restore state from DB. No-op if table is empty."""
        row = conn.execute(
            "SELECT pan_accum, tilt_accum, records_json FROM exploration_state WHERE id=1"
        ).fetchone()
        if row is None:
            return
        self._pan_accum = row[0]
        self._tilt_accum = row[1]
        try:
            raw_records = json.loads(row[2])
            self._records = [ExplorationRecord(**r) for r in raw_records]
        except (json.JSONDecodeError, TypeError):
            self._records = []

    # ------------------------------------------------------------------

    def context_for_prompt(self, n: int = 5) -> str:
        """Return a compact exploration summary for LLM context injection."""
        if not self._records:
            return ""

        recent = self._records[-n:]
        lines = ["[Exploration context — last observations]"]
        for r in recent:
            if r.novelty is None:
                novelty_str = "?"
            elif r.novelty >= 0.7:
                novelty_str = "HIGH"
            elif r.novelty <= 0.35:
                novelty_str = "LOW"
            else:
                novelty_str = "MED"
            lines.append(f"  - {r.timestamp} {r.direction_label} (novelty: {novelty_str})")

        hint = self.unvisited_hint()
        if hint:
            lines.append(hint)

        return "\n".join(lines)

    def as_coalition(self) -> Coalition | None:
        """Return a workspace Coalition from recent exploration state."""
        from .workspace import Coalition

        if not self._records:
            return None

        context = self.context_for_prompt()
        recent_novelties = [r.novelty for r in self._records[-5:] if r.novelty is not None]
        avg_novelty = sum(recent_novelties) / len(recent_novelties) if recent_novelties else 0.0
        hint = self.unvisited_hint()
        urgency = 0.5 if hint else 0.1
        last = self._records[-1]
        summary = f"last look: {last.direction_label} (novelty={'?' if last.novelty is None else f'{last.novelty:.2f}'})"

        return Coalition(
            source="exploration",
            summary=summary,
            activation=min(1.0, avg_novelty + 0.2),
            urgency=urgency,
            novelty=avg_novelty,
            context_block=context,
        )
