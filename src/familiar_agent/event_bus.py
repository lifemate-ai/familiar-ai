"""Event Bus — canonical event representation and JSONL logging.

Normalizes all agent activity (tool calls, observations, state changes,
interventions) into a unified Event stream.  Supports append-only logging
to JSONL and replay from logs.

This is Layer A of the Neighbor Intelligence Stack.
"""

from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

EventHandler = Callable[["Event"], None]


@dataclass
class Affect:
    """Estimated affect associated with an event."""

    valence: float = 0.0  # -1 (negative) to +1 (positive)
    arousal: float = 0.0  # 0 (calm) to 1 (activated)
    tags: list[str] = field(default_factory=list)


@dataclass
class Event:
    """Canonical event representation.

    Every signal flowing through the system is normalized to this form:
    text messages, camera captures, state changes, interventions, etc.
    """

    source: str  # "text" | "vision" | "audio" | "bio" | "device" | "system" | "memory" | "action"
    entity: str  # "user" | "assistant" | "environment" | "device"
    payload: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    salience: float = 0.5
    confidence: float = 1.0
    affect: Affect | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Event:
        affect_data = d.pop("affect", None)
        affect = Affect(**affect_data) if affect_data else None
        return cls(affect=affect, **d)


class EventBus:
    """Publish-subscribe event bus with JSONL persistence and replay."""

    def __init__(self, log_dir: str | Path | None = None):
        self._subscribers: list[EventHandler] = []
        self._lock = threading.Lock()
        self._log_file = None
        self._log_path: Path | None = None

        if log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            self._log_path = log_dir / f"events_{int(time.time())}.jsonl"
            self._log_file = open(self._log_path, "a", encoding="utf-8")

    def subscribe(self, handler: EventHandler) -> None:
        with self._lock:
            self._subscribers.append(handler)

    def unsubscribe(self, handler: EventHandler) -> None:
        with self._lock:
            self._subscribers = [h for h in self._subscribers if h is not handler]

    def emit(self, event: Event) -> None:
        """Append event to log and notify all subscribers."""
        # Persist
        if self._log_file:
            try:
                self._log_file.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
                self._log_file.flush()
            except Exception as e:
                logger.warning("Failed to write event to log: %s", e)

        # Notify
        with self._lock:
            handlers = list(self._subscribers)
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.warning("Event handler error: %s", e)

    def emit_simple(
        self,
        source: str,
        entity: str,
        payload: dict[str, Any],
        salience: float = 0.5,
    ) -> Event:
        """Convenience: create and emit an event in one call."""
        event = Event(source=source, entity=entity, payload=payload, salience=salience)
        self.emit(event)
        return event

    def close(self) -> None:
        if self._log_file:
            self._log_file.close()
            self._log_file = None

    @staticmethod
    def replay(log_path: str | Path) -> list[Event]:
        """Replay events from a JSONL log file."""
        events: list[Event] = []
        path = Path(log_path)
        if not path.exists():
            return events
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(Event.from_dict(json.loads(line)))
                except Exception as e:
                    logger.warning("Failed to parse event line: %s", e)
        return events

    @staticmethod
    def replay_all(log_dir: str | Path) -> list[Event]:
        """Replay all JSONL files in a directory, sorted by timestamp."""
        log_dir = Path(log_dir)
        events = []
        for p in sorted(log_dir.glob("events_*.jsonl")):
            events.extend(EventBus.replay(p))
        events.sort(key=lambda e: e.timestamp)
        return events
