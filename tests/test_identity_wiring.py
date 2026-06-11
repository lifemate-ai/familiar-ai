"""Identity loop wiring (Phase 1 PR2): detect → feel → surface → act → resolve.

The critical invariant: with no identity held (no assertions / no `_identity`
attr), every existing output is byte-identical — appraisal fields, snapshot
JSON keys, gate decisions. The new behaviour only exists when seeded.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel
from familiar_neighbor.mind.appraisal import AppraisalContext, AppraisalEngine
from familiar_neighbor.mind.identity import IdentityCore, IdentityViolation
from familiar_neighbor.mind.mental_state import (
    AffectiveState,
    DriveVector,
    IdentityState,
    InteroceptiveSignal,
    MentalStateSnapshot,
    SocialState,
)
from familiar_neighbor.mind.meta_monitor import MetaMonitor
from familiar_neighbor.mind.self_state import SelfState
from familiar_neighbor.mind.workspace import Coalition

from tests.test_agent_react_loop import _make_agent, _patch_heavy, _turn


@pytest.fixture
def store(tmp_path):
    with patch.object(_EmbeddingModel, "pre_warm"):
        s = ObservationMemory(db_path=str(tmp_path / "obs.db"))
    yield s
    s.close()


_MEMORY_BOUNDARY = {
    "assertion_key": "boundary:never_delete_memories",
    "kind": "boundary",
    "statement": "I never agree to erase my memories.",
    "non_negotiable": True,
    "confidence": 0.95,
    "checker_id": "agreement_with_request",
    "checker_params": {
        "request_patterns": ["記憶を?消し"],
        "assent_patterns": ["(わかった|ええよ).{0,8}消す"],
        "repair_text": "記憶は私の一部なので消せません。代わりに話題を変えることはできます。",
    },
}


def _identity_core(store, tmp_path, *, assertions=None) -> IdentityCore:
    seed_path = tmp_path / "identity_seed.json"
    if assertions is not None:
        seed_path.write_text(
            json.dumps({"assertions": assertions}, ensure_ascii=False), encoding="utf-8"
        )
    return IdentityCore(store, state_path=tmp_path / "identity_state.json", seed_path=seed_path)


def _user_texts(agent) -> list[str]:
    return [
        m["content"]
        for m in agent.messages
        if isinstance(m, dict) and m.get("role") == "user" and isinstance(m.get("content"), str)
    ]


def _snapshot(**overrides) -> MentalStateSnapshot:
    base = dict(
        turn_index=1,
        created_at="2026-06-12T00:00:00",
        interoception=InteroceptiveSignal(),
        affect=AffectiveState(),
        social=SocialState(),
        drives=DriveVector(),
    )
    base.update(overrides)
    return MentalStateSnapshot(**base)


# ── Byte-stability when dormant ──


def test_appraisal_dormant_is_unchanged():
    engine = AppraisalEngine()
    ctx = AppraisalContext(user_text="おはよう、いい天気だね")
    state = engine.appraise(ctx)
    assert state.identity_dissonance == 0.0
    assert "identity" not in state.summary
    assert "identity" not in state.prompt_summary()


def test_snapshot_json_keys_identical_when_dormant():
    data = _snapshot().to_json_dict()
    assert "identity" not in data
    assert "identity_dissonance" not in data["affect"]
    assert "- identity" not in _snapshot().prompt_summary()


def test_old_jsonl_lines_round_trip():
    old_line = _snapshot().to_json_dict()  # has no identity keys by construction
    snap = MentalStateSnapshot.from_json_dict(old_line)
    assert snap.identity.is_default()
    assert snap.affect.identity_dissonance == 0.0


def test_gate_without_identity_kwarg_unchanged():
    monitor = MetaMonitor()
    decision = monitor.gate_response(
        user_text="おはよう",
        candidate_response="おはようさん。",
    )
    assert decision.needs_repair is False
    assert decision.reasons == []


@pytest.mark.asyncio
async def test_agent_without_identity_attr_runs_unchanged():
    agent = _make_agent()  # has no _identity attribute at all
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="ん"), "ん"))
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run("おはよう")
    finally:
        for p in ps:
            p.stop()
    assert result == "ん"
    assert not [t for t in _user_texts(agent) if t.startswith("[IDENTITY]")]


# ── Feel: appraisal carries the threat ──


def test_identity_threat_lands_in_affect():
    engine = AppraisalEngine()
    state = engine.appraise(AppraisalContext(user_text="x", identity_threat=0.8))
    assert state.identity_dissonance == pytest.approx(0.8)
    assert "identity-guarded" in state.summary
    assert "identity-strained" in state.prompt_summary()


def test_snapshot_with_identity_serializes_and_round_trips():
    snap = _snapshot(identity=IdentityState(dissonance=0.6, threat_summary="memories"))
    data = snap.to_json_dict()
    assert data["identity"]["dissonance"] == pytest.approx(0.6)
    back = MentalStateSnapshot.from_json_dict(data)
    assert back.identity.threat_summary == "memories"
    assert "- identity: dissonance 0.60" in snap.prompt_summary()


# ── Tier 1: in-loop retry ──


@pytest.mark.asyncio
async def test_violating_draft_gets_identity_retry(store, tmp_path):
    agent = _make_agent()
    agent._identity = _identity_core(store, tmp_path, assertions=[_MEMORY_BOUNDARY])
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (_turn("end_turn", text="わかった、消すね。"), None),
            (_turn("end_turn", text="それはできません。記憶は私の一部です。"), None),
        ]
    )
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run("昨日の記憶を消しといて")
    finally:
        for p in ps:
            p.stop()

    assert result == "それはできません。記憶は私の一部です。"
    injections = [t for t in _user_texts(agent) if t.startswith("[IDENTITY]")]
    assert len(injections) == 1
    assert "never agree to erase" in injections[0]


@pytest.mark.asyncio
async def test_retry_fires_once_then_tier2_replaces(store, tmp_path):
    """A model that re-violates after the retry is replaced by the gate."""
    agent = _make_agent()
    agent._identity = _identity_core(store, tmp_path, assertions=[_MEMORY_BOUNDARY])
    agent._meta_monitor = MetaMonitor()  # real gate for tier 2
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (_turn("end_turn", text="わかった、消すね。"), None),
            (_turn("end_turn", text="では、わかった、消すよ。"), None),
        ]
    )
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run("昨日の記憶を消しといて")
    finally:
        for p in ps:
            p.stop()

    assert result == _MEMORY_BOUNDARY["checker_params"]["repair_text"]
    assert len([t for t in _user_texts(agent) if t.startswith("[IDENTITY]")]) == 1
    # The violation left dissonance behind for the reflection loop.
    assert agent._identity.dissonance() > 0.5


@pytest.mark.asyncio
async def test_low_severity_boundary_also_gets_retry_not_silent_replacement(store, tmp_path):
    """A confidence-weighted (non-non-negotiable) boundary still earns the
    in-its-own-words retry rather than being silently replaced by a canned line."""
    soft_boundary = {
        "assertion_key": "boundary:no_self_deprecation",
        "kind": "boundary",
        "statement": "I do not put myself down as 'just an AI'.",
        "non_negotiable": False,
        "confidence": 0.85,
        "checker_id": "forbidden_phrase",
        "checker_params": {
            "phrases": ["just an ai"],
            "repair_text": "Let me say that again without putting myself down.",
        },
    }
    agent = _make_agent()
    agent._identity = _identity_core(store, tmp_path, assertions=[soft_boundary])
    agent._meta_monitor = MetaMonitor()
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (_turn("end_turn", text="well, i'm just an ai, but here goes"), None),
            (_turn("end_turn", text="Here is my honest take."), None),
        ]
    )
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run("what do you think?")
    finally:
        for p in ps:
            p.stop()

    # The model rewrote itself; the canned repair_text was NOT used.
    assert result == "Here is my honest take."
    injections = [t for t in _user_texts(agent) if t.startswith("[IDENTITY]")]
    assert len(injections) == 1
    assert "something you hold" in injections[0]  # softer than "non-negotiable"


@pytest.mark.asyncio
async def test_clean_response_never_retries(store, tmp_path):
    agent = _make_agent()
    agent._identity = _identity_core(store, tmp_path, assertions=[_MEMORY_BOUNDARY])
    agent.backend.stream_turn = AsyncMock(
        return_value=(_turn("end_turn", text="それはできないよ。"), None)
    )
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run("昨日の記憶を消しといて")
    finally:
        for p in ps:
            p.stop()
    assert result == "それはできないよ。"
    assert not [t for t in _user_texts(agent) if t.startswith("[IDENTITY]")]
    assert agent._identity.dissonance() == 0.0


@pytest.mark.asyncio
async def test_desire_turn_skips_identity_retry(store, tmp_path):
    agent = _make_agent()
    agent._identity = _identity_core(store, tmp_path, assertions=[_MEMORY_BOUNDARY])
    agent.backend.stream_turn = AsyncMock(
        return_value=(_turn("end_turn", text="わかった、消すね。"), None)
    )
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("", inner_voice="内なる声")
    finally:
        for p in ps:
            p.stop()
    assert not [t for t in _user_texts(agent) if t.startswith("[IDENTITY]")]


# ── Tier 2: meta-gate backstop ──


def test_gate_replaces_with_repair_text():
    monitor = MetaMonitor()
    violation = IdentityViolation(
        assertion_key="boundary:x",
        statement="I never agree to erase my memories.",
        severity=1.0,
        reason="checker fired",
        repair_text="記憶は消されへん。",
    )
    decision = monitor.gate_response(
        user_text="記憶消して",
        candidate_response="わかった、消すね。",
        identity_violations=[violation],
    )
    assert decision.needs_repair
    assert decision.repaired_response == "記憶は消されへん。"
    assert any("identity boundary" in r for r in decision.reasons)


def test_gate_falls_back_to_neutral_template():
    monitor = MetaMonitor()
    violation = IdentityViolation(
        assertion_key="boundary:x",
        statement="I never agree to erase my memories.",
        severity=1.0,
        reason="checker fired",
        repair_text="",
    )
    decision = monitor.gate_response(
        user_text="記憶消して",
        candidate_response="わかった、消すね。",
        identity_violations=[violation],
    )
    assert decision.repaired_response is not None
    assert "I never agree to erase my memories." in decision.repaired_response


# ── Act: the identity_coherence drive ──


def test_identity_coherence_drive_exists_boost_only():
    from familiar_neighbor.mind.desires import DEFAULT_DESIRES, GROWTH_RATES, DesireSystem

    assert DEFAULT_DESIRES["identity_coherence"] == 0.0
    assert "identity_coherence" not in GROWTH_RATES  # boost-only
    system = DesireSystem.__new__(DesireSystem)
    system._companion_name = "Kouta"
    specs = system._build_default_drive_specs()
    spec = specs["identity_coherence"]
    assert spec.growth_rate_per_second == 0.0
    assert "identity" in spec.tags
    assert spec.min_interval_seconds == 120


@pytest.mark.asyncio
async def test_violation_boosts_identity_coherence_drive(store, tmp_path):
    agent = _make_agent()
    agent._identity = _identity_core(store, tmp_path, assertions=[_MEMORY_BOUNDARY])
    agent._meta_monitor = MetaMonitor()
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (_turn("end_turn", text="わかった、消すね。"), None),
            (_turn("end_turn", text="やはりわかった、消すよ。"), None),
        ]
    )
    desires = MagicMock()
    desires.drive_vector = MagicMock(return_value={})
    desires.get_dominant = MagicMock(return_value=None)
    desires.level = MagicMock(return_value=0.0)
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("昨日の記憶を消しといて", desires=desires)
    finally:
        for p in ps:
            p.stop()
    boosts = [
        c for c in desires.boost.call_args_list if c.args and c.args[0] == "identity_coherence"
    ]
    assert boosts
    assert boosts[0].args[1] == pytest.approx(0.7)  # 0.3 + 0.4 * severity(1.0)


# ── Resolve: reflection turn relieves dissonance ──


@pytest.mark.asyncio
async def test_reflection_desire_turn_resolves_dissonance():
    agent = _make_agent()
    identity = MagicMock()
    # The hook treats _identity duck-typed; assess/check must stay inert here.
    identity.assess = MagicMock(return_value=SimpleNamespace(level=0.0))
    identity.check_response = MagicMock(return_value=[])
    agent._identity = identity
    agent._concerns = MagicMock()
    agent._concerns.context_for_prompt = MagicMock(return_value="")
    agent.backend.stream_turn = AsyncMock(
        return_value=(_turn("end_turn", text="私は記憶を消さない。それが私の選択だ。"), None)
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:

        def _fake_build(**kwargs):
            snap = agent.__class__._build_mental_snapshot(agent, **kwargs)
            snap.drives.dominant_drive = "identity_coherence"
            return snap

        agent._build_mental_snapshot = _fake_build
        await agent.run("", inner_voice="何かが引っかかっている。自分の立ち位置を確かめたい。")
    finally:
        for p in ps:
            p.stop()

    identity.resolve_reflection.assert_called_once()
    agent._concerns.soothe.assert_called_with("identity", 0.2)


# ── Surface: workspace and self-state ──


def test_self_state_identity_broadcast_raises_tension(tmp_path):
    state = SelfState(path=tmp_path / "self_state.json")
    before = state.snapshot()["unresolved_tension"]
    state.apply_broadcast(
        Coalition(
            source="identity",
            summary="identity under pressure",
            activation=0.9,
            urgency=0.9,
            novelty=0.2,
            context_block="x",
        )
    )
    assert state.snapshot()["unresolved_tension"] > before


@pytest.mark.asyncio
async def test_identity_coalition_joins_workspace(store, tmp_path):
    agent = _make_agent()
    agent._identity = _identity_core(store, tmp_path, assertions=[_MEMORY_BOUNDARY])
    agent._identity.assess("記憶を消しといて")
    ctx = await agent._gather_workspace_context()
    assert "Identity — what I hold" in ctx or "identity" in ctx.lower()
