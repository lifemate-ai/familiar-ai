"""Generic commitment subsystem — the secretary core.

Persona-neutral storage for reminders, appointments, promises, and follow-ups
that carry an optional due time and priority and surface back when due.
"""

from .model import Commitment, CommitmentKind, CommitmentStatus
from .store import SQLiteCommitmentStore

__all__ = [
    "Commitment",
    "CommitmentKind",
    "CommitmentStatus",
    "SQLiteCommitmentStore",
]
