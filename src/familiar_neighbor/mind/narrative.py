"""Narrative arcs, daybook and self summary — the plot layer of selfhood.

The self-narrative writes one sentence per session and the experience ledger
keeps a dozen advisory lessons; neither says *what the agent's life is
currently about*. This module adds that:

- :class:`NarrativeStore` — the bounded set of **arcs** (ongoing storylines:
  a project, a relationship thread, a becoming). At most
  :data:`MAX_ACTIVE_ARCS` are active; committing one more demotes the
  lowest-importance active arc to ``dormant``. Rows live in
  ``narrative_arcs`` (observations DB, migration 014).
- :class:`Daybook` — one merged JSONL record per day (events, boundary
  moments, open loops, private reflections, next actions) in
  ``~/.familiar_ai/daybook.jsonl``.
- :func:`build_self_summary` — a bounded first-person digest of active arcs,
  the latest daybook record and the recent self-narrative.

Design constraints:

- **Never breaks a turn.** Reads return empty on any failure; writes log and
  swallow storage errors (``upsert_arc`` only raises on invalid *input*).
- **Byte-stable when empty.** :meth:`NarrativeStore.context_block` returns
  ``""`` with no active arcs so existing prompt pins hold.
- **No persona strings.** Titles and summaries come from the agent.
- Arc changes are mirrored onto the social event ledger as ``arc_updated``
  via the optional duck-typed ``event_log`` (best-effort, same as Phase 1).
- **Thread-safe.** :class:`NarrativeStore` serializes all connection access
  through one ``threading.Lock`` (same pattern as the commitment store).
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from familiar_agent.sqlite_migrations import apply_migrations, default_migration_dir
from familiar_neighbor.mind.social_events import emit_social_event

logger = logging.getLogger(__name__)

DEFAULT_NARRATIVE_DB_PATH = Path.home() / ".familiar_ai" / "observations.db"
DEFAULT_DAYBOOK_PATH = Path.home() / ".familiar_ai" / "daybook.jsonl"

MAX_ACTIVE_ARCS = 7
ARC_STATUSES: frozenset[str] = frozenset({"active", "dormant", "closed"})

_CONTEXT_BLOCK_MAX_CHARS = 1500
_ARC_SUMMARY_MAX_CHARS = 240
_ARC_TITLE_MAX_CHARS = 80
_DAYBOOK_FIELDS = (
    "events",
    "boundary_moments",
    "open_loops",
    "private_reflections",
    "next_actions",
)
_DAYBOOK_ITEM_MAX_CHARS = 300
_DAYBOOK_ITEMS_PER_FIELD = 20
_SELF_SUMMARY_MAX_CHARS = 1800
_SELF_SUMMARY_ARCS = 5
_SELF_SUMMARY_ITEMS_PER_FIELD = 4
_SELF_SUMMARY_NARRATIVE_LINES = 3


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today() -> str:
    return date.today().isoformat()


def _clamp01(value: Any, default: float = 0.5) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def _trim(text: Any, limit: int) -> str:
    cleaned = " ".join(str(text or "").split())
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 1] + "…"


# ── arcs ──


@dataclass(frozen=True)
class NarrativeArc:
    """One storyline the agent holds about its own life."""

    id: str
    arc_key: str
    title: str
    summary: str
    importance: float
    status: str
    created_at: str
    updated_at: str


class NarrativeStore:
    """Bounded arc store over the shared observations DB (lazy connection)."""

    def __init__(
        self,
        db_path: str | Path | None = None,
        *,
        event_log: Any = None,
        max_active: int = MAX_ACTIVE_ARCS,
    ) -> None:
        self._db_path = Path(db_path) if db_path is not None else DEFAULT_NARRATIVE_DB_PATH
        self._db: sqlite3.Connection | None = None
        self._lock = threading.Lock()
        self.event_log = event_log
        self._max_active = max(1, int(max_active))

    # ── connection ──

    def _ensure_db(self) -> sqlite3.Connection:
        if self._db is None:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._db = sqlite3.connect(self._db_path, check_same_thread=False)
            self._db.row_factory = sqlite3.Row
            self._db.execute("PRAGMA journal_mode = WAL")
            self._db.execute("PRAGMA synchronous = NORMAL")
            apply_migrations(self._db, default_migration_dir())
            self._db.commit()
        return self._db

    def close(self) -> None:
        with self._lock:
            if self._db is not None:
                try:
                    self._db.close()
                finally:
                    self._db = None

    # ── helpers ──

    @staticmethod
    def normalize_key(key: Any) -> str:
        return " ".join(str(key or "").split()).lower()

    @staticmethod
    def _from_row(row: sqlite3.Row) -> NarrativeArc:
        return NarrativeArc(
            id=str(row["id"]),
            arc_key=str(row["arc_key"]),
            title=str(row["title"]),
            summary=str(row["summary"] or ""),
            importance=float(row["importance"]),
            status=str(row["status"]),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )

    def _emit(self, action: str, arc: NarrativeArc) -> None:
        emit_social_event(
            self.event_log,
            "arc_updated",
            source="narrative",
            correlation_id=arc.id,
            confidence=arc.importance,
            payload={
                "action": action,
                "arc_key": arc.arc_key,
                "title": arc.title,
                "status": arc.status,
                "importance": arc.importance,
            },
        )

    def _select(
        self, where: str, params: list[Any], limit: int | None = None
    ) -> list[NarrativeArc]:
        sql = (
            "SELECT id, arc_key, title, summary, importance, status, created_at, updated_at "
            f"FROM narrative_arcs{where} ORDER BY importance DESC, updated_at DESC, rowid DESC"
        )
        if limit is not None:
            sql += " LIMIT ?"
            params = [*params, max(1, int(limit))]
        try:
            with self._lock:
                rows = self._ensure_db().execute(sql, params).fetchall()
        except Exception as exc:  # noqa: BLE001
            logger.warning("narrative_arcs: read failed: %s", exc)
            return []
        return [self._from_row(r) for r in rows]

    # ── writes ──

    def upsert_arc(self, key: str, title: str, summary: str, importance: float) -> NarrativeArc:
        """Create or update an arc; (re)activates it and enforces the bound.

        Raises ``ValueError`` on an empty key/title. Storage failures are
        logged and re-raised as ``RuntimeError`` so the tool can report them;
        the prompt path only ever calls the (never-raising) readers.
        """
        arc_key = self.normalize_key(key)
        clean_title = _trim(title, _ARC_TITLE_MAX_CHARS)
        if not arc_key:
            raise ValueError("arc key must not be empty")
        if not clean_title:
            raise ValueError("arc title must not be empty")
        clean_summary = _trim(summary, _ARC_SUMMARY_MAX_CHARS)
        weight = _clamp01(importance)
        now = _now_iso()
        try:
            with self._lock:
                db = self._ensure_db()
                existing = db.execute(
                    "SELECT id, created_at FROM narrative_arcs WHERE arc_key = ?", (arc_key,)
                ).fetchone()
                if existing is None:
                    arc_id = f"arc_{uuid.uuid4().hex}"
                    db.execute(
                        "INSERT INTO narrative_arcs "
                        "(id, arc_key, title, summary, importance, status, created_at, updated_at) "
                        "VALUES (?, ?, ?, ?, ?, 'active', ?, ?)",
                        (arc_id, arc_key, clean_title, clean_summary, weight, now, now),
                    )
                else:
                    arc_id = str(existing["id"])
                    db.execute(
                        "UPDATE narrative_arcs SET title = ?, summary = ?, importance = ?, "
                        "status = 'active', updated_at = ? WHERE id = ?",
                        (clean_title, clean_summary, weight, now, arc_id),
                    )
                demoted = self._enforce_bound(db)
                db.commit()
            arc = self._get_by_id(arc_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("narrative_arcs: upsert failed (%s): %s", arc_key, exc)
            raise RuntimeError(f"could not store arc '{arc_key}'") from exc
        if arc is None:  # pragma: no cover — row vanished between write and read
            raise RuntimeError(f"could not store arc '{arc_key}'")
        self._emit("upsert", arc)
        for other in demoted:
            self._emit("demote", other)
        return arc

    def _enforce_bound(self, db: sqlite3.Connection) -> list[NarrativeArc]:
        """Demote the lowest-importance active arcs beyond the cap (oldest first on ties)."""
        rows = db.execute(
            "SELECT id, arc_key, title, summary, importance, status, created_at, updated_at "
            "FROM narrative_arcs WHERE status = 'active' "
            "ORDER BY importance ASC, updated_at ASC, rowid ASC"
        ).fetchall()
        overflow = len(rows) - self._max_active
        if overflow <= 0:
            return []
        now = _now_iso()
        demoted: list[NarrativeArc] = []
        for row in rows[:overflow]:
            db.execute(
                "UPDATE narrative_arcs SET status = 'dormant', updated_at = ? WHERE id = ?",
                (now, row["id"]),
            )
            base = self._from_row(row)
            demoted.append(NarrativeArc(**{**asdict(base), "status": "dormant", "updated_at": now}))
        return demoted

    def close_arc(self, key: str) -> bool:
        """Mark an arc closed. False when unknown, already closed, or on storage failure."""
        arc_key = self.normalize_key(key)
        if not arc_key:
            return False
        try:
            with self._lock:
                db = self._ensure_db()
                cur = db.execute(
                    "UPDATE narrative_arcs SET status = 'closed', updated_at = ? "
                    "WHERE arc_key = ? AND status != 'closed'",
                    (_now_iso(), arc_key),
                )
                db.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning("narrative_arcs: close failed (%s): %s", arc_key, exc)
            return False
        if cur.rowcount <= 0:
            return False
        arc = self.get_arc(arc_key)
        if arc is not None:
            self._emit("close", arc)
        return True

    # ── reads (never raise) ──

    def _get_by_id(self, arc_id: str) -> NarrativeArc | None:
        found = self._select(" WHERE id = ?", [arc_id], limit=1)
        return found[0] if found else None

    def get_arc(self, key: str) -> NarrativeArc | None:
        arc_key = self.normalize_key(key)
        if not arc_key:
            return None
        found = self._select(" WHERE arc_key = ?", [arc_key], limit=1)
        return found[0] if found else None

    def active_arcs(self, limit: int = MAX_ACTIVE_ARCS) -> list[NarrativeArc]:
        """Active arcs, highest importance first (most recently touched on ties)."""
        return self._select(" WHERE status = 'active'", [], limit=limit)

    def dormant_arcs(self, limit: int = MAX_ACTIVE_ARCS) -> list[NarrativeArc]:
        return self._select(" WHERE status = 'dormant'", [], limit=limit)

    def context_block(self) -> str:
        """``[Life arcs]`` prompt block, or ``""`` when nothing is active."""
        arcs = self.active_arcs()
        if not arcs:
            return ""
        lines = ["[Life arcs]"]
        for arc in arcs:
            line = f"- {arc.title} (importance {arc.importance:.1f})"
            if arc.summary:
                line += f": {arc.summary}"
            lines.append(line)
        return "\n".join(lines)[:_CONTEXT_BLOCK_MAX_CHARS]


# ── daybook ──


@dataclass
class DaybookRecord:
    """One day's merged record."""

    date: str
    events: list[str] = field(default_factory=list)
    boundary_moments: list[str] = field(default_factory=list)
    open_loops: list[str] = field(default_factory=list)
    private_reflections: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DaybookRecord:
        return cls(
            date=str(data.get("date", "")),
            **{
                name: [str(x) for x in data.get(name, []) if isinstance(x, (str, int, float))]
                for name in _DAYBOOK_FIELDS
            },
        )

    def merged(self, **fields: list[str] | None) -> DaybookRecord:
        """Return a new record with the given items appended (deduplicated, bounded)."""
        merged: dict[str, list[str]] = {}
        for name in _DAYBOOK_FIELDS:
            current = list(getattr(self, name))
            for item in fields.get(name) or []:
                text = _trim(item, _DAYBOOK_ITEM_MAX_CHARS)
                if text and text not in current:
                    current.append(text)
            merged[name] = current[-_DAYBOOK_ITEMS_PER_FIELD:]
        return DaybookRecord(date=self.date, **merged)


class Daybook:
    """One record per day in a JSONL file; ``append_today`` merges in place."""

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = Path(path) if path is not None else DEFAULT_DAYBOOK_PATH

    def _read_all(self) -> list[DaybookRecord]:
        if not self._path.is_file():
            return []
        records: list[DaybookRecord] = []
        try:
            with self._path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except ValueError:
                        logger.warning("daybook: skipping corrupt line")
                        continue
                    if isinstance(data, dict) and data.get("date"):
                        records.append(DaybookRecord.from_dict(data))
        except Exception as exc:  # noqa: BLE001
            logger.warning("daybook: read failed: %s", exc)
            return []
        return records

    def _write_all(self, records: list[DaybookRecord]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(self._path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
        os.replace(tmp, self._path)

    def append_today(
        self,
        *,
        events: list[str] | None = None,
        boundary_moments: list[str] | None = None,
        open_loops: list[str] | None = None,
        private_reflections: list[str] | None = None,
        next_actions: list[str] | None = None,
    ) -> DaybookRecord | None:
        """Merge items into today's record. Never raises; returns the record or None."""
        incoming = {
            "events": events,
            "boundary_moments": boundary_moments,
            "open_loops": open_loops,
            "private_reflections": private_reflections,
            "next_actions": next_actions,
        }
        if not any(
            _trim(item, _DAYBOOK_ITEM_MAX_CHARS)
            for items in incoming.values()
            for item in (items or [])
        ):
            return None
        today = _today()
        try:
            records = self._read_all()
            others = [r for r in records if r.date != today]
            current = next((r for r in records if r.date == today), DaybookRecord(date=today))
            updated = current.merged(**incoming)
            self._write_all([*others, updated])
            return updated
        except Exception as exc:  # noqa: BLE001
            logger.warning("daybook: append failed: %s", exc)
            return None

    def record_for(self, day: str) -> DaybookRecord | None:
        return next((r for r in self._read_all() if r.date == day), None)

    def latest(self) -> DaybookRecord | None:
        """The most recent record by date, or None."""
        records = self._read_all()
        if not records:
            return None
        return max(records, key=lambda r: r.date)


# ── self summary ──


def _section(title: str, items: list[str]) -> str:
    return title + "\n" + "\n".join(f"- {item}" for item in items)


def build_self_summary(
    store: Any,
    daybook: Any,
    self_narrative_lines: list[str],
    *,
    max_chars: int = _SELF_SUMMARY_MAX_CHARS,
) -> str:
    """Aggregate active arcs + latest daybook + recent narrative into one bounded text.

    Every part is optional and duck-typed; a broken part is skipped. Returns
    ``""`` when there is nothing to say.
    """
    sections: list[str] = []

    arcs: list[Any] = []
    if store is not None:
        try:
            arcs = list(store.active_arcs(limit=_SELF_SUMMARY_ARCS))
        except Exception as exc:  # noqa: BLE001
            logger.warning("self_summary: arcs unavailable: %s", exc)
    if arcs:
        sections.append(
            _section(
                "Life arcs:",
                [
                    f"{a.title} (importance {a.importance:.1f})"
                    + (f": {a.summary}" if a.summary else "")
                    for a in arcs
                ],
            )
        )

    record: Any = None
    if daybook is not None:
        try:
            record = daybook.latest()
        except Exception as exc:  # noqa: BLE001
            logger.warning("self_summary: daybook unavailable: %s", exc)
    if record is not None:
        labels = {
            "events": "events",
            "boundary_moments": "boundary moments",
            "open_loops": "open loops",
            "private_reflections": "private reflections",
            "next_actions": "next actions",
        }
        day_lines = [
            f"{labels[name]}: " + "; ".join(items[-_SELF_SUMMARY_ITEMS_PER_FIELD:])
            for name in _DAYBOOK_FIELDS
            if (items := list(getattr(record, name, []) or []))
        ]
        if day_lines:
            sections.append(_section(f"Latest daybook ({record.date}):", day_lines))

    lines = [
        _trim(line, _DAYBOOK_ITEM_MAX_CHARS)
        for line in (self_narrative_lines or [])[-_SELF_SUMMARY_NARRATIVE_LINES:]
    ]
    lines = [line for line in lines if line]
    if lines:
        sections.append(_section("Recent self-narrative:", lines))

    if not sections:
        return ""
    return "\n\n".join(sections)[:max_chars]
