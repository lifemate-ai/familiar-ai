"""Tests for as_coalition() methods across all processors.

Each processor (desires, scene, exploration, self_narrative, tom, memory)
produces a Coalition for the Global Workspace.  These tests verify:
  - Returns None when the processor has no data (empty state).
  - Returns a Coalition with correct source and valid field ranges.
  - Field values (activation, urgency, novelty) are within [0, 1].
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from familiar_agent.desires import TRIGGER_THRESHOLD, DesireSystem
from familiar_agent.exploration import ExplorationTracker
from familiar_agent.scene import SceneTracker
from familiar_agent.self_narrative import SelfNarrative
from familiar_agent.tools.tom import ToMTool
from familiar_agent.workspace import Coalition


# ── helpers ────────────────────────────────────────────────────────────────────


def _assert_valid_coalition(c: Coalition, expected_source: str) -> None:
    """Assert that a Coalition has correct source and all fields in range."""
    assert isinstance(c, Coalition)
    assert c.source == expected_source
    assert isinstance(c.summary, str) and len(c.summary) > 0
    assert 0.0 <= c.activation <= 1.0
    assert 0.0 <= c.urgency <= 1.0
    assert 0.0 <= c.novelty <= 1.0
    assert isinstance(c.context_block, str) and len(c.context_block) > 0


# ── DesireSystem.as_coalition ──────────────────────────────────────────────────


@pytest.fixture
def desires(tmp_path: Path) -> DesireSystem:
    return DesireSystem(state_path=tmp_path / "desires.json", companion_name="Kota")


def test_desire_coalition_none_when_no_dominant(desires: DesireSystem) -> None:
    """All desires below threshold -> as_coalition returns None."""
    result = desires.as_coalition()
    assert result is None


def test_desire_coalition_returns_valid_coalition(desires: DesireSystem) -> None:
    """Boosted desire above threshold -> valid Coalition."""
    desires.boost("worry_companion", TRIGGER_THRESHOLD + 0.1)
    c = desires.as_coalition()
    assert c is not None
    _assert_valid_coalition(c, "desire")


def test_desire_coalition_source_is_desire(desires: DesireSystem) -> None:
    desires.boost("explore", TRIGGER_THRESHOLD + 0.1)
    c = desires.as_coalition()
    assert c is not None
    assert c.source == "desire"


def test_desire_coalition_summary_contains_desire_name(desires: DesireSystem) -> None:
    desires.boost("look_around", TRIGGER_THRESHOLD + 0.2)
    c = desires.as_coalition()
    assert c is not None
    assert "look_around" in c.summary


def test_desire_coalition_urgency_varies_by_desire_type(desires: DesireSystem) -> None:
    """worry_companion should have higher urgency than rest."""
    desires.boost("worry_companion", TRIGGER_THRESHOLD + 0.1)
    worry_c = desires.as_coalition()
    assert worry_c is not None

    desires2 = DesireSystem(
        state_path=desires._state_path.parent / "desires2.json", companion_name="Kota"
    )
    desires2.boost("rest", TRIGGER_THRESHOLD + 0.1)
    rest_c = desires2.as_coalition()
    assert rest_c is not None

    assert worry_c.urgency > rest_c.urgency


def test_desire_coalition_activation_equals_desire_level(desires: DesireSystem) -> None:
    desires.boost("greet_companion", 0.85)
    c = desires.as_coalition()
    assert c is not None
    assert c.activation == pytest.approx(0.85, abs=0.05)


def test_desire_coalition_context_block_has_inner_voice(desires: DesireSystem) -> None:
    desires.boost("explore", TRIGGER_THRESHOLD + 0.1)
    c = desires.as_coalition()
    assert c is not None
    assert "[inner-voice]" in c.context_block


# ── SceneTracker.as_coalition ──────────────────────────────────────────────────


@pytest.fixture
def scene_tracker() -> SceneTracker:
    conn = sqlite3.connect(":memory:")
    return SceneTracker(conn)


def test_scene_coalition_none_when_empty(scene_tracker: SceneTracker) -> None:
    """No entities tracked -> returns None."""
    result = scene_tracker.as_coalition()
    assert result is None


def test_scene_coalition_returns_valid_with_entities(scene_tracker: SceneTracker) -> None:
    """Manually inject entities, then check coalition."""
    scene_tracker._current_entities = {
        "chair": {"label": "chair", "category": "object", "confidence": 0.9},
        "window": {"label": "window", "category": "object", "confidence": 0.85},
    }
    c = scene_tracker.as_coalition()
    assert c is not None
    _assert_valid_coalition(c, "scene")


def test_scene_coalition_source_is_scene(scene_tracker: SceneTracker) -> None:
    scene_tracker._current_entities = {
        "desk": {"label": "desk", "category": "object", "confidence": 0.7},
    }
    c = scene_tracker.as_coalition()
    assert c is not None
    assert c.source == "scene"


def test_scene_coalition_summary_contains_entity_count(scene_tracker: SceneTracker) -> None:
    scene_tracker._current_entities = {
        "lamp": {"label": "lamp", "category": "object", "confidence": 0.8},
        "person": {"label": "person", "category": "person", "confidence": 0.75},
        "door": {"label": "door", "category": "object", "confidence": 0.6},
    }
    c = scene_tracker.as_coalition()
    assert c is not None
    assert "3" in c.summary


def test_scene_coalition_activation_is_avg_confidence(scene_tracker: SceneTracker) -> None:
    scene_tracker._current_entities = {
        "a": {"label": "a", "category": "object", "confidence": 0.6},
        "b": {"label": "b", "category": "object", "confidence": 0.8},
    }
    c = scene_tracker.as_coalition()
    assert c is not None
    assert c.activation == pytest.approx(0.7, abs=0.01)


def test_scene_coalition_urgency_low_without_people_events(scene_tracker: SceneTracker) -> None:
    """No recent 'appeared' events for people -> low urgency."""
    scene_tracker._current_entities = {
        "table": {"label": "table", "category": "object", "confidence": 0.8},
    }
    c = scene_tracker.as_coalition()
    assert c is not None
    assert c.urgency == 0.2


def test_scene_coalition_context_block_has_scene_label(scene_tracker: SceneTracker) -> None:
    scene_tracker._current_entities = {
        "cup": {"label": "cup", "category": "object", "confidence": 0.8},
    }
    c = scene_tracker.as_coalition()
    assert c is not None
    assert "[Current scene]" in c.context_block


# ── SelfNarrative.as_coalition ─────────────────────────────────────────────────


@pytest.fixture
def narrative(tmp_path: Path) -> SelfNarrative:
    return SelfNarrative(path=tmp_path / "narrative.jsonl")


def test_narrative_coalition_none_when_no_entries(narrative: SelfNarrative) -> None:
    result = narrative.as_coalition()
    assert result is None


def test_narrative_coalition_returns_valid_after_write(narrative: SelfNarrative) -> None:
    narrative.write("Today I learned something new about the world.")
    c = narrative.as_coalition()
    assert c is not None
    _assert_valid_coalition(c, "narrative")


def test_narrative_coalition_source_is_narrative(narrative: SelfNarrative) -> None:
    narrative.write("I felt calm today.")
    c = narrative.as_coalition()
    assert c is not None
    assert c.source == "narrative"


def test_narrative_coalition_summary_from_latest_entry(narrative: SelfNarrative) -> None:
    narrative.write("First entry.")
    narrative.write("Second entry is the latest.")
    c = narrative.as_coalition()
    assert c is not None
    assert "Second entry" in c.summary


def test_narrative_coalition_fixed_activation(narrative: SelfNarrative) -> None:
    """Narrative coalitions have a fixed activation of 0.4."""
    narrative.write("Some reflection.")
    c = narrative.as_coalition()
    assert c is not None
    assert c.activation == pytest.approx(0.4)


def test_narrative_coalition_low_urgency(narrative: SelfNarrative) -> None:
    """Narrative is not time-sensitive."""
    narrative.write("A quiet day.")
    c = narrative.as_coalition()
    assert c is not None
    assert c.urgency <= 0.2


# ── ExplorationTracker.as_coalition ────────────────────────────────────────────


@pytest.fixture
def exploration() -> ExplorationTracker:
    return ExplorationTracker()


def test_exploration_coalition_none_when_no_records(exploration: ExplorationTracker) -> None:
    result = exploration.as_coalition()
    assert result is None


def test_exploration_coalition_returns_valid_after_move(exploration: ExplorationTracker) -> None:
    exploration.record_move("left", 30)
    c = exploration.as_coalition()
    assert c is not None
    _assert_valid_coalition(c, "exploration")


def test_exploration_coalition_source_is_exploration(exploration: ExplorationTracker) -> None:
    exploration.record_move("right", 45)
    c = exploration.as_coalition()
    assert c is not None
    assert c.source == "exploration"


def test_exploration_coalition_summary_contains_last_direction(
    exploration: ExplorationTracker,
) -> None:
    exploration.record_move("up", 20)
    c = exploration.as_coalition()
    assert c is not None
    assert "up" in c.summary


def test_exploration_coalition_novelty_from_records(exploration: ExplorationTracker) -> None:
    """When novelty scores are recorded, avg_novelty is reflected."""
    exploration.record_move("left", 30)
    exploration.record_novelty(0.8)
    exploration.record_move("right", 30)
    exploration.record_novelty(0.6)
    c = exploration.as_coalition()
    assert c is not None
    assert c.novelty == pytest.approx(0.7, abs=0.01)


def test_exploration_coalition_novelty_zero_without_scores(
    exploration: ExplorationTracker,
) -> None:
    """No novelty scores recorded -> novelty is 0.0."""
    exploration.record_move("down", 30)
    c = exploration.as_coalition()
    assert c is not None
    assert c.novelty == 0.0


def test_exploration_coalition_urgency_high_with_unvisited(
    exploration: ExplorationTracker,
) -> None:
    """When some directions are unvisited, urgency is higher."""
    exploration.record_move("left", 30)
    exploration.record_move("left", 30)
    c = exploration.as_coalition()
    assert c is not None
    assert c.urgency == 0.5  # unvisited hint present


def test_exploration_coalition_activation_bounded(exploration: ExplorationTracker) -> None:
    """activation = min(1.0, avg_novelty + 0.2), so always <= 1.0."""
    exploration.record_move("left", 30)
    exploration.record_novelty(0.95)
    c = exploration.as_coalition()
    assert c is not None
    assert c.activation <= 1.0


# ── ToMTool.as_coalition ───────────────────────────────────────────────────────


@pytest.fixture
def tom_tool() -> ToMTool:
    # Use a mock memory that returns empty on recall_async
    mock_memory = AsyncMock()
    mock_memory.recall_async = AsyncMock(return_value=[])
    return ToMTool(memory=mock_memory, default_person="Kota")


def test_tom_coalition_none_before_any_call(tom_tool: ToMTool) -> None:
    """No ToM inference done yet -> returns None."""
    result = tom_tool.as_coalition()
    assert result is None


@pytest.mark.asyncio
async def test_tom_coalition_returns_valid_after_call(tom_tool: ToMTool) -> None:
    """After calling tom tool, as_coalition returns valid Coalition."""
    await tom_tool.call("tom", {"situation": "User seems tired"})
    c = tom_tool.as_coalition()
    assert c is not None
    _assert_valid_coalition(c, "tom")


@pytest.mark.asyncio
async def test_tom_coalition_source_is_tom(tom_tool: ToMTool) -> None:
    await tom_tool.call("tom", {"situation": "Hello there"})
    c = tom_tool.as_coalition()
    assert c is not None
    assert c.source == "tom"


@pytest.mark.asyncio
async def test_tom_coalition_summary_contains_person(tom_tool: ToMTool) -> None:
    await tom_tool.call("tom", {"situation": "How are you?", "person": "Mika"})
    c = tom_tool.as_coalition()
    assert c is not None
    assert "Mika" in c.summary


@pytest.mark.asyncio
async def test_tom_coalition_summary_contains_situation(tom_tool: ToMTool) -> None:
    await tom_tool.call("tom", {"situation": "I need help with code"})
    c = tom_tool.as_coalition()
    assert c is not None
    assert "help" in c.summary or "code" in c.summary


@pytest.mark.asyncio
async def test_tom_coalition_uses_default_person(tom_tool: ToMTool) -> None:
    await tom_tool.call("tom", {"situation": "Something happened"})
    c = tom_tool.as_coalition()
    assert c is not None
    assert "Kota" in c.summary


@pytest.mark.asyncio
async def test_tom_coalition_fixed_values(tom_tool: ToMTool) -> None:
    """ToM has fixed activation=0.5, urgency=0.6, novelty=0.2."""
    await tom_tool.call("tom", {"situation": "test"})
    c = tom_tool.as_coalition()
    assert c is not None
    assert c.activation == pytest.approx(0.5)
    assert c.urgency == pytest.approx(0.6)
    assert c.novelty == pytest.approx(0.2)


# ── ObservationMemory.as_coalition_async ───────────────────────────────────────


@pytest.mark.asyncio
async def test_memory_coalition_none_when_no_memories() -> None:
    """When recall_async returns empty, as_coalition_async returns None."""
    from familiar_agent.tools.memory import ObservationMemory

    mem = object.__new__(ObservationMemory)
    mem.recall_async = AsyncMock(return_value=[])

    c = await mem.as_coalition_async()
    assert c is None


@pytest.mark.asyncio
async def test_memory_coalition_returns_valid_with_memories() -> None:
    """When recall_async returns memories, as_coalition_async returns valid Coalition."""
    from familiar_agent.tools.memory import ObservationMemory

    mem = object.__new__(ObservationMemory)
    mem.recall_async = AsyncMock(
        return_value=[
            {"summary": "Saw a beautiful sunset", "confidence": 0.9, "emotion": "happy"},
            {"summary": "Had dinner with Kota", "confidence": 0.7, "emotion": "warm"},
        ]
    )

    c = await mem.as_coalition_async()
    assert c is not None
    _assert_valid_coalition(c, "memory")


@pytest.mark.asyncio
async def test_memory_coalition_source_is_memory() -> None:
    from familiar_agent.tools.memory import ObservationMemory

    mem = object.__new__(ObservationMemory)
    mem.recall_async = AsyncMock(
        return_value=[
            {"summary": "Test memory", "confidence": 0.5, "emotion": "neutral"},
        ]
    )

    c = await mem.as_coalition_async()
    assert c is not None
    assert c.source == "memory"


@pytest.mark.asyncio
async def test_memory_coalition_activation_from_top_confidence() -> None:
    """Activation should come from the highest-confidence memory."""
    from familiar_agent.tools.memory import ObservationMemory

    mem = object.__new__(ObservationMemory)
    mem.recall_async = AsyncMock(
        return_value=[
            {"summary": "Low conf", "confidence": 0.3, "emotion": "neutral"},
            {"summary": "High conf", "confidence": 0.95, "emotion": "moved"},
        ]
    )

    c = await mem.as_coalition_async()
    assert c is not None
    assert c.activation == pytest.approx(0.95)


@pytest.mark.asyncio
async def test_memory_coalition_summary_from_top_memory() -> None:
    """Summary should come from the highest-confidence memory."""
    from familiar_agent.tools.memory import ObservationMemory

    mem = object.__new__(ObservationMemory)
    mem.recall_async = AsyncMock(
        return_value=[
            {"summary": "Not this one", "confidence": 0.2, "emotion": "neutral"},
            {"summary": "This is the top memory", "confidence": 0.99, "emotion": "happy"},
        ]
    )

    c = await mem.as_coalition_async()
    assert c is not None
    assert "top memory" in c.summary


@pytest.mark.asyncio
async def test_memory_coalition_context_block_has_recall_label() -> None:
    from familiar_agent.tools.memory import ObservationMemory

    mem = object.__new__(ObservationMemory)
    mem.recall_async = AsyncMock(
        return_value=[
            {"summary": "Some event", "confidence": 0.5, "emotion": "curious"},
        ]
    )

    c = await mem.as_coalition_async()
    assert c is not None
    assert "[Memory recall]" in c.context_block


@pytest.mark.asyncio
async def test_memory_coalition_fixed_urgency_and_novelty() -> None:
    """Memory coalitions have fixed urgency=0.1 and novelty=0.0."""
    from familiar_agent.tools.memory import ObservationMemory

    mem = object.__new__(ObservationMemory)
    mem.recall_async = AsyncMock(
        return_value=[
            {"summary": "Test", "confidence": 0.5, "emotion": "neutral"},
        ]
    )

    c = await mem.as_coalition_async()
    assert c is not None
    assert c.urgency == pytest.approx(0.1)
    assert c.novelty == pytest.approx(0.0)
