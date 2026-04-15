"""Routine and schedule helpers for quiet hours and continuation flow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True, frozen=True)
class QuietHoursRule:
    start_hour: int = 23
    end_hour: int = 7

    def is_active(self, now: datetime | None = None) -> bool:
        moment = now or datetime.now()
        if self.start_hour == self.end_hour:
            return False
        if self.start_hour < self.end_hour:
            return self.start_hour <= moment.hour < self.end_hour
        return moment.hour >= self.start_hour or moment.hour < self.end_hour


@dataclass(slots=True, frozen=True)
class RoutineDecision:
    quiet_hours: bool
    schedule_multiplier: float
    notes: tuple[str, ...] = ()


def parse_schedule_config(path: Path | None) -> QuietHoursRule:
    if path is None or not path.exists():
        return QuietHoursRule()
    start = 23
    end = 7
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = [part.strip() for part in stripped.split("=", 1)]
        if key == "quiet_hours_start":
            start = int(value)
        elif key == "quiet_hours_end":
            end = int(value)
    return QuietHoursRule(start_hour=start, end_hour=end)


def load_optional_notes(base_dir: Path | None = None) -> dict[str, str]:
    root = base_dir or Path.cwd()
    result: dict[str, str] = {}
    for name in ("SOUL.md", "TODO.md", "ROUTINES.md"):
        path = root / name
        if path.exists():
            result[name] = path.read_text(encoding="utf-8").strip()
    return result


def evaluate_routine_state(rule: QuietHoursRule, now: datetime | None = None) -> RoutineDecision:
    quiet = rule.is_active(now)
    return RoutineDecision(
        quiet_hours=quiet,
        schedule_multiplier=0.45 if quiet else 1.0,
        notes=("quiet-hours",) if quiet else (),
    )
