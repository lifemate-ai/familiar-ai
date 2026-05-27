"""Generic runtime event model."""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentEvent:
    """Append-only event emitted by the generic runtime."""

    source: str
    type: str
    payload: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str | None = None
    task_id: str | None = None
    turn_id: str | None = None
    timestamp: float = field(default_factory=time.time)
    salience: float = 0.5
    confidence: float = 1.0
    parent_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentEvent:
        return cls(**data)
