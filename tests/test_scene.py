"""Tests for SceneTracker — entity extraction and change detection.

TDD: these tests are written BEFORE the implementation in scene.py.
All tests that touch the DB use an in-memory SQLite connection.
"""

from __future__ import annotations

import json
import sqlite3
from unittest.mock import AsyncMock, MagicMock

import pytest

from familiar_agent.scene import SceneTracker, extract_entities


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _in_memory_tracker() -> SceneTracker:
    """SceneTracker backed by an in-memory SQLite DB."""
    conn = sqlite3.connect(":memory:")
    tracker = SceneTracker.__new__(SceneTracker)
    tracker._conn = conn
    tracker._current_entities = {}
    tracker._init_schema(conn)
    return tracker


def _backend_with_response(json_response: str) -> MagicMock:
    backend = MagicMock()
    backend.complete = AsyncMock(return_value=json_response)
    return backend


# ---------------------------------------------------------------------------
# Tests: extract_entities()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_extract_entities_calls_backend():
    """extract_entities() must call backend.complete with the description."""
    backend = _backend_with_response('{"entities": []}')

    await extract_entities("A room with a chair.", backend)

    backend.complete.assert_awaited_once()
    prompt_arg = backend.complete.call_args[0][0]
    assert "A room with a chair." in prompt_arg


@pytest.mark.asyncio
async def test_extract_entities_returns_list():
    """extract_entities() returns a list of entity dicts."""
    payload = json.dumps(
        {
            "entities": [
                {"label": "chair", "category": "object", "confidence": 0.9},
                {"label": "person", "category": "person", "confidence": 0.85},
            ]
        }
    )
    backend = _backend_with_response(payload)

    result = await extract_entities("A room with a chair and person.", backend)

    assert len(result) == 2
    labels = {e["label"] for e in result}
    assert labels == {"chair", "person"}


@pytest.mark.asyncio
async def test_extract_entities_handles_malformed_json():
    """extract_entities() returns empty list when backend returns non-JSON."""
    backend = _backend_with_response("Sorry, I can't parse that.")

    result = await extract_entities("Some description.", backend)

    assert result == []


@pytest.mark.asyncio
async def test_extract_entities_handles_missing_entities_key():
    """extract_entities() returns empty list when JSON has no 'entities' key."""
    backend = _backend_with_response('{"result": "ok"}')

    result = await extract_entities("Some description.", backend)

    assert result == []


# ---------------------------------------------------------------------------
# Tests: SceneTracker.update() — entity storage
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_stores_entities_in_db():
    """update() persists extracted entities to the DB."""
    tracker = _in_memory_tracker()
    payload = json.dumps({"entities": [{"label": "sofa", "category": "object", "confidence": 0.9}]})
    backend = _backend_with_response(payload)

    await tracker.update("A sofa in the room.", backend)

    rows = tracker._conn.execute("SELECT label FROM scene_entities").fetchall()
    labels = {r[0] for r in rows}
    assert "sofa" in labels


@pytest.mark.asyncio
async def test_update_sets_current_entities():
    """After update(), _current_entities reflects the latest scene."""
    tracker = _in_memory_tracker()
    payload = json.dumps({"entities": [{"label": "lamp", "category": "object", "confidence": 0.8}]})
    backend = _backend_with_response(payload)

    await tracker.update("A lamp on the table.", backend)

    assert "lamp" in tracker._current_entities


# ---------------------------------------------------------------------------
# Tests: SceneTracker.update() — change detection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_detects_appeared_entity():
    """Entity in new frame but not in previous → 'appeared' event."""
    tracker = _in_memory_tracker()

    # First frame: empty room
    backend1 = _backend_with_response('{"entities": []}')
    await tracker.update("Empty room.", backend1)

    # Second frame: a cat appears
    payload = json.dumps({"entities": [{"label": "cat", "category": "object", "confidence": 0.9}]})
    backend2 = _backend_with_response(payload)
    events = await tracker.update("A cat in the room.", backend2)

    appeared = [e for e in events if e["event_type"] == "appeared"]
    assert any(e["entity_label"] == "cat" for e in appeared)


@pytest.mark.asyncio
async def test_update_detects_disappeared_entity():
    """Entity in previous frame but not in new → 'disappeared' event."""
    tracker = _in_memory_tracker()

    # First frame: chair present
    payload1 = json.dumps(
        {"entities": [{"label": "chair", "category": "object", "confidence": 0.9}]}
    )
    await tracker.update("A chair.", _backend_with_response(payload1))

    # Second frame: chair gone
    backend2 = _backend_with_response('{"entities": []}')
    events = await tracker.update("Empty room.", backend2)

    disappeared = [e for e in events if e["event_type"] == "disappeared"]
    assert any(e["entity_label"] == "chair" for e in disappeared)


@pytest.mark.asyncio
async def test_update_no_events_when_entities_unchanged():
    """Same entities across two frames → no events."""
    tracker = _in_memory_tracker()

    payload = json.dumps({"entities": [{"label": "desk", "category": "object", "confidence": 0.9}]})
    await tracker.update("A desk.", _backend_with_response(payload))
    events = await tracker.update("A desk.", _backend_with_response(payload))

    assert events == []


@pytest.mark.asyncio
async def test_update_stores_events_in_db():
    """Detected events are persisted to scene_events table."""
    tracker = _in_memory_tracker()

    await tracker.update("Empty room.", _backend_with_response('{"entities": []}'))
    payload = json.dumps(
        {"entities": [{"label": "person", "category": "person", "confidence": 0.95}]}
    )
    await tracker.update("A person entered.", _backend_with_response(payload))

    rows = tracker._conn.execute("SELECT event_type, entity_label FROM scene_events").fetchall()
    assert any(r[0] == "appeared" and r[1] == "person" for r in rows)


# ---------------------------------------------------------------------------
# Tests: SceneTracker.context_for_prompt()
# ---------------------------------------------------------------------------


def test_context_for_prompt_empty_when_no_entities():
    """No entities → empty string."""
    tracker = _in_memory_tracker()
    assert tracker.context_for_prompt() == ""


@pytest.mark.asyncio
async def test_context_for_prompt_includes_entity_labels():
    """context_for_prompt() contains entity labels after update."""
    tracker = _in_memory_tracker()
    payload = json.dumps(
        {
            "entities": [
                {"label": "monitor", "category": "object", "confidence": 0.9},
                {"label": "keyboard", "category": "object", "confidence": 0.85},
            ]
        }
    )
    await tracker.update("A monitor and keyboard.", _backend_with_response(payload))

    context = tracker.context_for_prompt()
    assert "monitor" in context
    assert "keyboard" in context


# ---------------------------------------------------------------------------
# Tests: SceneTracker.recent_events()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_recent_events_returns_latest_n():
    """recent_events(n) returns at most n recent events."""
    tracker = _in_memory_tracker()

    # Three separate updates to generate events
    await tracker.update("Empty.", _backend_with_response('{"entities": []}'))
    for label in ["apple", "book", "lamp"]:
        payload = json.dumps(
            {"entities": [{"label": label, "category": "object", "confidence": 0.8}]}
        )
        await tracker.update(f"A {label}.", _backend_with_response(payload))
        await tracker.update("Empty.", _backend_with_response('{"entities": []}'))

    events = tracker.recent_events(n=2)
    assert len(events) <= 2
