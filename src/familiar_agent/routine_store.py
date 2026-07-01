"""Self-authored routines — the agent's own recurring schedule.

The reference deployment showed that self-authored schedule entries ARE
identity structure: reading novels at half past midnight, a tanka at ten, a
self-reflection pass before sleep. This store gives the standalone agent the
same power, with the same trust split as identity assertions: ``seed``
routines are operator-supplied (hand-edit the JSON); the agent authors its
own via tools, under guardrails enforced HERE at the store layer — interval
floor and count cap — so it cannot schedule itself into a spam loop.

Firing rides the existing commitments machinery: a due routine materializes
one commitment, which then flows through the proactive-reminder gates (idle
precedence, quiet hours, backoff) completely unchanged. The store never
starts turns itself.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_ROUTINES_PATH = Path.home() / ".familiar_ai" / "routines.json"

# Guardrails for agent-authored routines (seed rows are operator-owned and
# exempt — the operator can hand themselves footguns, the agent cannot).
MIN_AGENT_INTERVAL_SEC = 600.0
MAX_AGENT_ROUTINES = 12


@dataclass(slots=True)
class Routine:
    routine_id: str
    name: str
    schedule: str  # "daily@HH:MM" | "interval:<seconds>"
    prompt: str  # the impulse text a firing injects (via a commitment)
    source: str = "agent"  # "seed" (operator) | "agent" (self-authored)
    enabled: bool = True
    priority: int = 1
    last_fired_at: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


def _parse_daily(schedule: str) -> tuple[int, int] | None:
    """Return (hour, minute) for "daily@HH:MM", else None."""
    if not schedule.startswith("daily@"):
        return None
    try:
        hh, mm = schedule[len("daily@") :].split(":", 1)
        hour, minute = int(hh), int(mm)
    except ValueError:
        return None
    if 0 <= hour < 24 and 0 <= minute < 60:
        return hour, minute
    return None


def _parse_interval(schedule: str) -> float | None:
    """Return seconds for "interval:<seconds>", else None."""
    if not schedule.startswith("interval:"):
        return None
    try:
        seconds = float(schedule[len("interval:") :])
    except ValueError:
        return None
    return seconds if seconds > 0 else None


def schedule_is_valid(schedule: str) -> bool:
    return _parse_daily(schedule) is not None or _parse_interval(schedule) is not None


def routine_is_due(routine: Routine, now: float) -> bool:
    """Pure schedule check — daily fires once per day at/after its time."""
    if not routine.enabled:
        return False
    daily = _parse_daily(routine.schedule)
    if daily is not None:
        local = datetime.fromtimestamp(now)
        fire_at = local.replace(hour=daily[0], minute=daily[1], second=0, microsecond=0)
        fire_ts = fire_at.timestamp()
        return now >= fire_ts and routine.last_fired_at < fire_ts
    interval = _parse_interval(routine.schedule)
    if interval is not None:
        return now - routine.last_fired_at >= interval
    return False


class RoutineStore:
    """JSON-backed routine list; the cortex is the single writer."""

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = Path(path).expanduser() if path else DEFAULT_ROUTINES_PATH
        self._routines: list[Routine] = []
        self._load()

    # ── persistence ─────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            for item in raw.get("routines", []):
                if not isinstance(item, dict):
                    continue
                try:
                    self._routines.append(Routine(**item))
                except TypeError:
                    logger.warning("Skipping malformed routine entry: %r", item)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not load routines: %s", exc)

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"routines": [asdict(r) for r in self._routines]}
            tmp = self._path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self._path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not save routines: %s", exc)

    # ── reads ───────────────────────────────────────────────────────────────

    def list_routines(self, *, include_disabled: bool = True) -> list[Routine]:
        return [r for r in self._routines if include_disabled or r.enabled]

    def get(self, routine_id: str) -> Routine | None:
        return next((r for r in self._routines if r.routine_id == routine_id), None)

    def due(self, now: float | None = None) -> list[Routine]:
        now = now if now is not None else time.time()
        return [r for r in self._routines if routine_is_due(r, now)]

    # ── writes (guardrails live here, not in the tool) ─────────────────────

    def commit(
        self,
        *,
        name: str,
        schedule: str,
        prompt: str,
        source: str = "agent",
        priority: int = 1,
        routine_id: str | None = None,
    ) -> tuple[Routine | None, str]:
        """Create or update a routine. Returns (routine, message).

        Agent-authored rows cannot touch seed rows, cannot exceed the count
        cap, and cannot schedule tighter than the interval floor — enforced
        here so no tool wrapper can bypass it.
        """
        if not name.strip() or not prompt.strip():
            return None, "name and prompt are required"
        if not schedule_is_valid(schedule):
            return None, f"invalid schedule '{schedule}' (use daily@HH:MM or interval:<seconds>)"
        interval = _parse_interval(schedule)
        if source == "agent" and interval is not None and interval < MIN_AGENT_INTERVAL_SEC:
            return None, f"agent routines need interval >= {int(MIN_AGENT_INTERVAL_SEC)}s"

        if routine_id:
            existing = self.get(routine_id)
            if existing is None:
                return None, f"no routine '{routine_id}'"
            if existing.source == "seed" and source != "seed":
                return None, "seed routines are operator-owned; the agent cannot edit them"
            existing.name = name.strip()
            existing.schedule = schedule
            existing.prompt = prompt.strip()
            existing.priority = max(0, min(3, int(priority)))
            existing.enabled = True
            self._save()
            return existing, "updated"

        if source == "agent":
            agent_count = sum(1 for r in self._routines if r.source == "agent" and r.enabled)
            if agent_count >= MAX_AGENT_ROUTINES:
                return None, f"routine cap reached ({MAX_AGENT_ROUTINES}); drop one first"
        routine = Routine(
            routine_id=f"routine_{uuid.uuid4().hex[:8]}",
            name=name.strip(),
            schedule=schedule,
            prompt=prompt.strip(),
            source=source,
            priority=max(0, min(3, int(priority))),
        )
        self._routines.append(routine)
        self._save()
        return routine, "created"

    def drop(self, routine_id: str, *, source: str = "agent") -> tuple[bool, str]:
        """Disable a routine. The agent may only drop its own."""
        routine = self.get(routine_id)
        if routine is None:
            return False, f"no routine '{routine_id}'"
        if routine.source == "seed" and source != "seed":
            return False, "seed routines are operator-owned; the agent cannot drop them"
        routine.enabled = False
        self._save()
        return True, "disabled"

    # ── firing (rides the commitments machinery) ────────────────────────────

    def materialize_due(self, commitment_store: Any, now: float | None = None) -> int:
        """Turn due routines into commitments; returns how many fired.

        ``last_fired_at`` advances immediately, so one due window produces
        exactly one commitment regardless of how often this is polled. The
        commitment then flows through the existing proactive-reminder gates.
        """
        now = now if now is not None else time.time()
        fired = 0
        for routine in self.due(now):
            try:
                commitment_store.create(
                    summary=f"Routine — {routine.name}: {routine.prompt[:200]}",
                    due_at=now,
                    priority=routine.priority,
                    created_by="routine",
                    metadata={"routine_id": routine.routine_id},
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Routine '%s' failed to materialize: %s", routine.name, exc)
                continue
            routine.last_fired_at = now
            fired += 1
        if fired:
            self._save()
        return fired
