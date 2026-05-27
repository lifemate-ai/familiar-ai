"""Event bus with JSONL logging, subscriptions, and replay."""

from __future__ import annotations

import json
import logging
import threading
import time
from collections.abc import Callable
from pathlib import Path

from .model import AgentEvent

logger = logging.getLogger(__name__)
EventHandler = Callable[[AgentEvent], None]


class EventBus:
    """Publish-subscribe bus for runtime events."""

    def __init__(self, log_dir: str | Path | None = None) -> None:
        self._subscribers: list[EventHandler] = []
        self._lock = threading.Lock()
        self._log_file = None
        self._log_path: Path | None = None
        if log_dir:
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)
            self._log_path = log_path / f"events_{int(time.time())}.jsonl"
            self._log_file = open(self._log_path, "a", encoding="utf-8")

    @property
    def log_path(self) -> Path | None:
        return self._log_path

    def subscribe(self, handler: EventHandler) -> None:
        with self._lock:
            self._subscribers.append(handler)

    def unsubscribe(self, handler: EventHandler) -> None:
        with self._lock:
            self._subscribers = [item for item in self._subscribers if item is not handler]

    def emit(self, event: AgentEvent) -> AgentEvent:
        if self._log_file is not None:
            try:
                self._log_file.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
                self._log_file.flush()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to write event: %s", exc)

        with self._lock:
            subscribers = list(self._subscribers)
        for handler in subscribers:
            try:
                handler(event)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Event handler failed: %s", exc)
        return event

    def emit_simple(
        self,
        *,
        source: str,
        type: str,
        payload: dict,
        run_id: str | None = None,
        task_id: str | None = None,
        turn_id: str | None = None,
    ) -> AgentEvent:
        return self.emit(
            AgentEvent(
                source=source,
                type=type,
                payload=payload,
                run_id=run_id,
                task_id=task_id,
                turn_id=turn_id,
            )
        )

    def close(self) -> None:
        if self._log_file is not None:
            self._log_file.close()
            self._log_file = None

    @staticmethod
    def replay(log_path: str | Path) -> list[AgentEvent]:
        path = Path(log_path)
        if not path.exists():
            return []
        events: list[AgentEvent] = []
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(AgentEvent.from_dict(json.loads(line)))
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to parse event line: %s", exc)
        return events

    @staticmethod
    def replay_all(log_dir: str | Path) -> list[AgentEvent]:
        events: list[AgentEvent] = []
        for path in sorted(Path(log_dir).glob("events_*.jsonl")):
            events.extend(EventBus.replay(path))
        events.sort(key=lambda event: event.timestamp)
        return events
