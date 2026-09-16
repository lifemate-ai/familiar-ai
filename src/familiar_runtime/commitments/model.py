"""Generic commitment model — the secretary core primitive.

A :class:`Commitment` is anything the agent or the user has committed to and
may need to be reminded of: a reminder, an appointment, a promise, a follow-up,
or a lightweight task. Unlike :mod:`familiar_runtime.tasks` (goal-directed
execution records), commitments carry an optional due time and priority and are
designed to surface back to the user when they come due.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CommitmentKind(str, Enum):
    REMINDER = "reminder"
    APPOINTMENT = "appointment"
    PROMISE = "promise"
    FOLLOWUP = "followup"
    TASK = "task"


class CommitmentStatus(str, Enum):
    OPEN = "open"
    SNOOZED = "snoozed"
    DONE = "done"
    CANCELLED = "cancelled"


_ACTIVE = (CommitmentStatus.OPEN, CommitmentStatus.SNOOZED)

# Proactive-reminder cadence: stop after this many self-initiated reminders, and
# widen the gap between them by these multipliers of the base cooldown. After the
# cap is reached the commitment goes quiet (it still surfaces in turn context).
REMINDER_CAP = 3
_REMINDER_BACKOFF: tuple[float, ...] = (1.0, 3.0)


@dataclass(slots=True)
class Commitment:
    id: str
    summary: str
    kind: CommitmentKind = CommitmentKind.REMINDER
    status: CommitmentStatus = CommitmentStatus.OPEN
    due_at: float | None = None
    priority: int = 0
    created_by: str = "agent"
    person: str | None = None
    created_at: float = 0.0
    updated_at: float = 0.0
    completed_at: float | None = None
    snooze_until: float | None = None
    last_reminded_at: float | None = None
    reminder_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        return self.status in _ACTIVE

    def effective_due(self) -> float | None:
        """When this commitment next wants attention.

        A snoozed commitment is silent until its snooze window elapses, after
        which its original due time applies again.
        """
        if self.status is CommitmentStatus.SNOOZED and self.snooze_until is not None:
            return self.snooze_until
        return self.due_at

    def is_due(self, *, now: float) -> bool:
        if not self.is_active:
            return False
        due = self.effective_due()
        return due is not None and due <= now

    def is_upcoming(self, *, now: float, horizon: float) -> bool:
        if not self.is_active:
            return False
        due = self.effective_due()
        return due is not None and now < due <= now + horizon

    def due_for_reminder(self, *, now: float, base_cooldown: float) -> bool:
        """Whether a *proactive* reminder should fire now.

        Independent of context surfacing: applies an escalating backoff between
        self-initiated reminders and stops entirely after ``REMINDER_CAP`` so an
        un-actioned commitment goes quiet instead of nagging forever.
        """
        if not self.is_due(now=now):
            return False
        if self.reminder_count >= REMINDER_CAP:
            return False
        if self.last_reminded_at is None:
            return True
        idx = max(0, self.reminder_count - 1)
        factor = _REMINDER_BACKOFF[idx] if idx < len(_REMINDER_BACKOFF) else _REMINDER_BACKOFF[-1]
        return (now - self.last_reminded_at) >= base_cooldown * factor
