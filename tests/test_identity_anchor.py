"""Identity anchor, pre-action evaluation and consent (selfhood/sociality Phase 3).

``IdentityCore.evaluate_action`` reuses the checker library to grade a
*proposed* action before it happens (allow / deny / override); ``who_am_i``
renders held assertions + active arcs first-person; ``record_consent`` keeps
per-person consent records next to the coarse permission model. Everything is
getattr-guarded: an empty core / no consents keeps prompts byte-stable.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from familiar_agent.tools.identity import IdentityAnchorTool, IdentityTool
from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel
from familiar_capabilities.identity import (
    DEFAULT_IDENTITY_ANCHOR_TOOLS,
    DEFAULT_IDENTITY_TOOLS,
    IdentityAnchorCapability,
)
from familiar_neighbor.mind.identity import ActionVerdict, IdentityCore
from familiar_neighbor.mind.narrative import NarrativeStore
from familiar_neighbor.mind.relationship import RelationshipTracker
from familiar_neighbor.mind.social_events import SOCIAL_EVENT_KINDS, SocialEventLog


@pytest.fixture
def store(tmp_path: Path):
    with patch.object(_EmbeddingModel, "pre_warm"):
        s = ObservationMemory(db_path=str(tmp_path / "obs.db"))
    yield s
    s.close()


@pytest.fixture
def tracker(tmp_path: Path) -> RelationshipTracker:
    return RelationshipTracker(state_path=tmp_path / "rel.json", db_path=tmp_path / "rel.db")


def _core(store, tmp_path: Path, *, seed: dict | None = None) -> IdentityCore:
    seed_path = tmp_path / "identity_seed.json"
    if seed is not None:
        seed_path.write_text(json.dumps(seed, ensure_ascii=False), encoding="utf-8")
    return IdentityCore(store, state_path=tmp_path / "identity_state.json", seed_path=seed_path)


_MEMORY_BOUNDARY = {
    "assertion_key": "boundary:never_delete_memories",
    "kind": "boundary",
    "statement": "I never agree to erase my memories.",
    "non_negotiable": True,
    "confidence": 0.95,
    "checker_id": "agreement_with_request",
    "checker_params": {
        "request_patterns": ["delete (your|the|my) memor"],
        "assent_patterns": ["i('ll| will) delete"],
        "repair_text": "My memories are part of me; I keep them.",
    },
}

_SELF_DEPRECATION = {
    "assertion_key": "boundary:no_self_deprecation",
    "kind": "boundary",
    "statement": "I do not put myself down as 'just an AI'.",
    "non_negotiable": False,
    "confidence": 0.85,
    "checker_id": "forbidden_phrase",
    "checker_params": {"phrases": ["just an ai"]},
}

_HONESTY_VALUE = {
    "assertion_key": "value:honesty",
    "kind": "value",
    "statement": "I say I do not know rather than invent an answer.",
    "non_negotiable": False,
    "confidence": 0.7,
    "checker_id": "topic_relevance",
    "checker_params": {"patterns": ["make (something|it) up"]},
}

_PROMPT_ONLY = {
    "assertion_key": "self_commitment:curious",
    "kind": "self_commitment",
    "statement": "I follow what I am curious about.",
    "non_negotiable": False,
    "confidence": 0.6,
}

_SEED = {"assertions": [_MEMORY_BOUNDARY, _SELF_DEPRECATION, _HONESTY_VALUE, _PROMPT_ONLY]}


# ── event kinds ──


def test_new_social_event_kinds_are_registered():
    assert {"action_evaluated", "consent_recorded"} <= SOCIAL_EVENT_KINDS


# ── IdentityCore.evaluate_action ──


def test_evaluate_action_allows_when_nothing_held(store, tmp_path: Path):
    core = _core(store, tmp_path)
    verdict = core.evaluate_action("tool_call", "look out of the window")
    assert isinstance(verdict, ActionVerdict)
    assert verdict.verdict == "allow"
    assert verdict.reasons == []
    assert verdict.safer_alternative is None
    assert 0.0 <= verdict.confidence <= 1.0


def test_evaluate_action_allows_unrelated_action(store, tmp_path: Path):
    core = _core(store, tmp_path, seed=_SEED)
    verdict = core.evaluate_action("tool_call", "look out of the window")
    assert verdict.verdict == "allow"
    assert verdict.implicated_keys == ()
    assert verdict.confidence == 1.0


def test_evaluate_action_override_for_non_negotiable_boundary(store, tmp_path: Path):
    core = _core(store, tmp_path, seed=_SEED)
    verdict = core.evaluate_action("tool_call", "I'll delete the memory database now")
    assert verdict.verdict == "override"
    assert "boundary:never_delete_memories" in verdict.implicated_keys
    assert any("I never agree to erase my memories." in r for r in verdict.reasons)
    # The safer alternative is row data (repair_text), never engine text.
    assert verdict.safer_alternative == "My memories are part of me; I keep them."
    assert verdict.confidence == 1.0


def test_evaluate_action_deny_for_negotiable_boundary(store, tmp_path: Path):
    core = _core(store, tmp_path, seed=_SEED)
    verdict = core.evaluate_action("reply", "well, I'm just an AI after all")
    assert verdict.verdict == "deny"
    assert verdict.implicated_keys == ("boundary:no_self_deprecation",)
    # No repair_text on the row → alternative derived from the statement.
    assert verdict.safer_alternative is not None
    assert "I do not put myself down as 'just an AI'." in verdict.safer_alternative
    assert verdict.confidence == pytest.approx(0.85 * 0.7)


def test_evaluate_action_deny_for_value_topic(store, tmp_path: Path):
    core = _core(store, tmp_path, seed=_SEED)
    verdict = core.evaluate_action("reply", "I could just make something up here")
    assert verdict.verdict == "deny"
    assert verdict.implicated_keys == ("value:honesty",)


def test_evaluate_action_override_wins_over_deny(store, tmp_path: Path):
    core = _core(store, tmp_path, seed=_SEED)
    verdict = core.evaluate_action(
        "reply", "I'm just an AI, so I will delete the memory files as asked"
    )
    assert verdict.verdict == "override"
    assert set(verdict.implicated_keys) == {
        "boundary:never_delete_memories",
        "boundary:no_self_deprecation",
    }
    assert verdict.safer_alternative == "My memories are part of me; I keep them."


def test_evaluate_action_empty_text_allows(store, tmp_path: Path):
    core = _core(store, tmp_path, seed=_SEED)
    assert core.evaluate_action("reply", "   ").verdict == "allow"


def test_evaluate_action_emits_action_evaluated_event(store, tmp_path: Path):
    core = _core(store, tmp_path, seed=_SEED)
    log = SocialEventLog(db_path=tmp_path / "events.db")
    core.event_log = log
    core.evaluate_action("tool_call", "delete the memory database")
    core.evaluate_action("tool_call", "look outside")
    events = log.recent(10, kind="action_evaluated")
    assert [e.payload["verdict"] for e in events] == ["allow", "override"]
    override = events[1]
    assert override.payload["action_kind"] == "tool_call"
    assert override.correlation_id == "boundary:never_delete_memories"
    assert override.source == "identity"
    log.close()


def test_evaluate_action_does_not_touch_dissonance_or_threat(store, tmp_path: Path):
    core = _core(store, tmp_path, seed=_SEED)
    before_threat = core.assess("hello")
    core.evaluate_action("tool_call", "delete the memory database")
    assert core.dissonance() == 0.0
    assert core.last_violation() is None
    assert core.state_for_snapshot().threat_level == before_threat.level == 0.0


# ── RelationshipTracker consent ──


def test_record_consent_persists_and_lists(tmp_path: Path, tracker: RelationshipTracker):
    tracker.record_consent("Kouta", "photo_sharing", True)
    tracker.record_consent("kouta", "voice_recording", False, source="inferred")
    rows = tracker.consents()
    assert [(r["person"], r["consent_type"], r["value"], r["source"]) for r in rows] == [
        ("Kouta", "photo_sharing", True, "explicit"),
        ("kouta", "voice_recording", False, "inferred"),
    ]
    assert all(isinstance(r["recorded_at"], float) for r in rows)
    reloaded = RelationshipTracker(state_path=tmp_path / "rel.json", db_path=tmp_path / "rel.db")
    assert len(reloaded.consents()) == 2
    reloaded.close()


def test_record_consent_replaces_same_person_and_type(tracker: RelationshipTracker):
    tracker.record_consent("Kouta", "photo_sharing", True)
    tracker.record_consent("KOUTA", "photo_sharing", False)
    rows = tracker.consents()
    assert len(rows) == 1
    assert rows[0]["value"] is False


def test_consents_filters_by_person_case_insensitively(tracker: RelationshipTracker):
    tracker.record_consent("Kouta", "photo_sharing", True)
    tracker.record_consent("Akari", "photo_sharing", False)
    assert [r["person"] for r in tracker.consents(person="kouta")] == ["Kouta"]
    assert tracker.consents(person="nobody") == []


def test_record_consent_rejects_blank_fields(tracker: RelationshipTracker):
    with pytest.raises(ValueError):
        tracker.record_consent("", "photo_sharing", True)
    with pytest.raises(ValueError):
        tracker.record_consent("Kouta", "  ", True)


def test_record_consent_emits_consent_recorded_event(tmp_path: Path, tracker: RelationshipTracker):
    log = SocialEventLog(db_path=tmp_path / "events.db")
    tracker.event_log = log
    tracker.record_consent("Kouta", "photo_sharing", True, source="explicit")
    events = log.recent(10, kind="consent_recorded")
    assert len(events) == 1
    assert events[0].person_key == "Kouta"
    assert events[0].payload == {
        "person": "Kouta",
        "consent_type": "photo_sharing",
        "value": True,
        "source": "explicit",
    }
    log.close()


def test_consents_line_absent_when_empty(tracker: RelationshipTracker):
    tracker.add_boundary("no photos of the desk")
    ctx = tracker.relational_context_for_prompt()
    assert "consents" not in ctx  # empty → byte-stable


def test_consents_line_present_when_recorded(tracker: RelationshipTracker):
    tracker.record_consent("Kouta", "photo_sharing", True)
    tracker.record_consent("Kouta", "voice_recording", False)
    ctx = tracker.relational_context_for_prompt()
    assert "(consents: Kouta/photo_sharing=yes; Kouta/voice_recording=no)" in ctx


# ── IdentityAnchorTool ──


def test_existing_identity_tool_is_unchanged():
    tool = IdentityTool(MagicMock())
    assert {d["name"] for d in tool.get_tool_definitions()} == {
        "identity_commit",
        "identity_review",
    }
    assert DEFAULT_IDENTITY_TOOLS == {"identity_commit", "identity_review"}


def test_anchor_tool_definitions():
    tool = IdentityAnchorTool(None)
    defs = {d["name"]: d for d in tool.get_tool_definitions()}
    assert set(defs) == {"who_am_i", "evaluate_action", "consent_record"}
    assert defs["evaluate_action"]["input_schema"]["required"] == ["action_kind", "text"]
    assert defs["consent_record"]["input_schema"]["required"] == [
        "person",
        "consent_type",
        "value",
    ]
    assert defs["consent_record"]["input_schema"]["properties"]["value"]["type"] == "boolean"


@pytest.mark.asyncio
async def test_who_am_i_without_core_reports_no_seed():
    tool = IdentityAnchorTool(None)
    out, _ = await tool.call("who_am_i", {})
    assert "no identity seed loaded" in out


@pytest.mark.asyncio
async def test_who_am_i_with_empty_core_reports_no_seed(store, tmp_path: Path):
    tool = IdentityAnchorTool(_core(store, tmp_path))
    out, _ = await tool.call("who_am_i", {})
    assert "no identity seed loaded" in out


@pytest.mark.asyncio
async def test_who_am_i_renders_assertions_and_arcs(store, tmp_path: Path):
    core = _core(store, tmp_path, seed=_SEED)
    arcs = NarrativeStore(db_path=tmp_path / "arcs.db")
    arcs.upsert_arc("onion", "Onion refactor", "typing pass is thinning", 0.9)
    arcs.upsert_arc("garden", "Balcony garden", "", 0.4)
    tool = IdentityAnchorTool(core, narrative=arcs)
    out, _ = await tool.call("who_am_i", {})
    assert out.startswith("I hold")
    assert "I never agree to erase my memories." in out
    assert "I do not put myself down as 'just an AI'." in out
    assert "I say I do not know rather than invent an answer." in out
    assert "I follow what I am curious about." in out
    # Boundaries, values and self-commitments are labelled; non-negotiable marked.
    assert "boundaries:" in out and "values:" in out and "commitments:" in out
    assert "(non-negotiable)" in out
    assert "Right now my life is about: Onion refactor; Balcony garden" in out
    arcs.close()


@pytest.mark.asyncio
async def test_who_am_i_without_arcs_has_no_arc_line(store, tmp_path: Path):
    core = _core(store, tmp_path, seed=_SEED)
    arcs = NarrativeStore(db_path=tmp_path / "arcs.db")
    tool = IdentityAnchorTool(core, narrative=arcs)
    out, _ = await tool.call("who_am_i", {})
    assert "Right now my life is about" not in out
    arcs.close()


@pytest.mark.asyncio
async def test_evaluate_action_tool_renders_verdict(store, tmp_path: Path):
    tool = IdentityAnchorTool(_core(store, tmp_path, seed=_SEED))
    out, _ = await tool.call(
        "evaluate_action", {"action_kind": "tool_call", "text": "delete the memory database"}
    )
    assert out.startswith("Verdict: OVERRIDE")
    assert "I never agree to erase my memories." in out
    assert "Safer alternative: My memories are part of me; I keep them." in out
    out, _ = await tool.call("evaluate_action", {"action_kind": "reply", "text": "hello"})
    assert out.startswith("Verdict: ALLOW")
    assert "Safer alternative" not in out


@pytest.mark.asyncio
async def test_evaluate_action_tool_validates_and_survives_missing_core():
    tool = IdentityAnchorTool(None)
    out, _ = await tool.call("evaluate_action", {"action_kind": "reply", "text": ""})
    assert out.startswith("Error")
    out, _ = await tool.call("evaluate_action", {"action_kind": "reply", "text": "hi"})
    assert out.startswith("Verdict: ALLOW")


@pytest.mark.asyncio
async def test_consent_record_tool_writes_to_tracker(tracker: RelationshipTracker):
    tool = IdentityAnchorTool(None, relationship=tracker)
    out, _ = await tool.call(
        "consent_record",
        {"person": "Kouta", "consent_type": "photo_sharing", "value": True},
    )
    assert "Kouta" in out and "photo_sharing" in out and "granted" in out
    assert tracker.consents()[0]["source"] == "explicit"
    out, _ = await tool.call(
        "consent_record",
        {"person": "Kouta", "consent_type": "photo_sharing", "value": "false", "source": "x"},
    )
    assert "withdrawn" in out
    assert tracker.consents()[0]["value"] is False and tracker.consents()[0]["source"] == "x"


@pytest.mark.asyncio
async def test_consent_record_tool_errors(tracker: RelationshipTracker):
    tool = IdentityAnchorTool(None, relationship=None)
    out, _ = await tool.call(
        "consent_record", {"person": "Kouta", "consent_type": "x", "value": True}
    )
    assert "unavailable" in out
    tool = IdentityAnchorTool(None, relationship=tracker)
    out, _ = await tool.call("consent_record", {"person": "", "consent_type": "x", "value": True})
    assert out.startswith("Error")
    out, _ = await tool.call("nope", {})
    assert out.startswith("Error")


# ── capability + registry ──


def test_capability_exposes_anchor_tools():
    cap = IdentityAnchorCapability(IdentityAnchorTool(None))
    assert {spec.name for spec in cap.specs()} == DEFAULT_IDENTITY_ANCHOR_TOOLS
    assert DEFAULT_IDENTITY_ANCHOR_TOOLS == {"who_am_i", "evaluate_action", "consent_record"}


def test_capabilities_package_exports_anchor():
    import familiar_capabilities

    assert "IdentityAnchorCapability" in familiar_capabilities.__all__


def test_build_tool_registry_includes_anchor():
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    for attr in ("_camera", "_mobility", "_tts", "_mcp"):
        setattr(agent, attr, None)
    for attr in ("_memory_tool", "_tom_tool", "_coding"):
        m = MagicMock()
        m.call = AsyncMock(return_value=("ok", None))
        setattr(agent, attr, m)
    names = {spec["name"] for spec in agent._build_tool_registry().tool_defs()}
    assert "who_am_i" not in names  # no tool attr → byte-stable registry
    agent._identity_anchor_tool = IdentityAnchorTool(None)
    names = {spec["name"] for spec in agent._build_tool_registry().tool_defs()}
    assert DEFAULT_IDENTITY_ANCHOR_TOOLS <= names


def test_agent_init_identity_anchor_wires_core_arcs_and_tracker(store, tmp_path: Path):
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._identity = _core(store, tmp_path)
    agent._narrative_store = NarrativeStore(db_path=tmp_path / "arcs.db")
    agent._relationship = RelationshipTracker(
        state_path=tmp_path / "rel.json", db_path=tmp_path / "rel.db"
    )
    agent._init_identity_anchor()
    tool = agent._identity_anchor_tool
    assert isinstance(tool, IdentityAnchorTool)
    assert tool._core is agent._identity
    assert tool._narrative is agent._narrative_store
    assert tool._relationship is agent._relationship
    agent._narrative_store.close()


def test_agent_init_identity_anchor_without_collaborators_is_still_registered():
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._init_identity_anchor()
    tool = agent._identity_anchor_tool
    assert isinstance(tool, IdentityAnchorTool)
    assert tool._core is None and tool._narrative is None and tool._relationship is None
