"""Tests for generic runtime events."""

from __future__ import annotations

from familiar_runtime.events import AgentEvent, EventBus, SQLiteEventStore


def test_event_bus_logs_and_replays_jsonl(tmp_path) -> None:
    bus = EventBus(log_dir=tmp_path)
    seen: list[str] = []
    bus.subscribe(lambda event: seen.append(event.type))
    event = bus.emit_simple(source="user", type="message", payload={"text": "hi"})
    bus.close()

    assert seen == ["message"]
    assert bus.log_path is not None
    replayed = EventBus.replay(bus.log_path)
    assert [item.id for item in replayed] == [event.id]
    assert replayed[0].payload == {"text": "hi"}


def test_sqlite_event_store_replays_in_timestamp_order(tmp_path) -> None:
    store = SQLiteEventStore(tmp_path / "events.db")
    later = AgentEvent(source="tool", type="tool_result", payload={"name": "b"}, timestamp=2.0)
    earlier = AgentEvent(source="user", type="message", payload={"text": "a"}, timestamp=1.0)

    store.append(later)
    store.append(earlier)
    replayed = store.replay()
    store.close()

    assert [event.id for event in replayed] == [earlier.id, later.id]
