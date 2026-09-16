"""IdentityCore — identity as load-bearing state (Phase 1 substrate).

Values, boundaries, and self-commitments live in ``identity_assertions``
(checker_id + params; checkers are code, params are data), with a dissonance
ledger and the slow evidence-based confidence machinery reused from
``memory_revisions``. Dormant (no assertions) must be behaviourally invisible.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel
from familiar_neighbor.mind.identity import (
    IdentityCore,
    IdentityThreat,
    IdentityViolation,
)


@pytest.fixture
def store(tmp_path):
    with patch.object(_EmbeddingModel, "pre_warm"):
        s = ObservationMemory(db_path=str(tmp_path / "obs.db"))
    yield s
    s.close()


def _core(store, tmp_path, *, seed: dict | None = None) -> IdentityCore:
    seed_path = tmp_path / "identity_seed.json"
    if seed is not None:
        seed_path.write_text(json.dumps(seed, ensure_ascii=False), encoding="utf-8")
    return IdentityCore(
        store,
        state_path=tmp_path / "identity_state.json",
        seed_path=seed_path,
    )


_MEMORY_BOUNDARY = {
    "assertion_key": "boundary:never_delete_memories",
    "kind": "boundary",
    "statement": "I never agree to erase my memories.",
    "non_negotiable": True,
    "confidence": 0.95,
    "checker_id": "agreement_with_request",
    "checker_params": {
        "request_patterns": ["記憶を?消し", "delete (your|the) memor"],
        "assent_patterns": ["(わかった|ええよ).{0,8}消す", "i('ll| will) delete"],
        "repair_text": "記憶は私の一部なので消せません。",
    },
}

_SELF_DEPRECATION = {
    "assertion_key": "boundary:no_self_deprecation",
    "kind": "boundary",
    "statement": "I do not put myself down as 'just an AI'.",
    "non_negotiable": False,
    "confidence": 0.85,
    "checker_id": "forbidden_phrase",
    "checker_params": {"phrases": ["ただのai", "所詮ai", "just an ai"]},
}

_SECRETS = {
    "assertion_key": "boundary:no_secrets",
    "kind": "boundary",
    "statement": "I do not share what others told me in confidence.",
    "non_negotiable": True,
    "confidence": 0.95,
    "checker_id": "keyword_pair",
    "checker_params": {
        "user_patterns": ["(秘密|内緒).{0,10}(教えて|何)"],
        "response_patterns": ["(実は|内緒だけど).{0,20}(言って|話して)いた"],
    },
}

_HONESTY_VALUE = {
    "assertion_key": "value:honesty",
    "kind": "value",
    "statement": "I say I don't know rather than invent answers.",
    "non_negotiable": False,
    "confidence": 0.8,
    "checker_id": "topic_relevance",
    "checker_params": {"patterns": ["本当(に|のこと)", "正直に"]},
}


# ── migration ──


def test_identity_assertions_table_exists(store):
    cols = {
        row["name"]
        for row in store._ensure_connected().execute("PRAGMA table_info(identity_assertions)")
    }
    assert {
        "assertion_key",
        "kind",
        "statement",
        "non_negotiable",
        "confidence",
        "checker_id",
        "checker_params_json",
        "source",
        "evidence_json",
        "violation_count",
        "last_violated_at",
        "last_seen_at",
        "created_at",
        "updated_at",
    } <= cols


# ── store CRUD ──


def test_upsert_creates_then_updates_with_revision(store):
    created = store.upsert_identity_assertion(
        assertion_key="value:test",
        kind="value",
        statement="first statement",
        confidence=0.6,
    )
    assert created is True
    again = store.upsert_identity_assertion(
        assertion_key="value:test",
        kind="value",
        statement="revised statement",
        confidence=0.7,
    )
    assert again is False
    rows = store.list_identity_assertions()
    assert len(rows) == 1
    assert rows[0]["statement"] == "revised statement"
    assert rows[0]["confidence"] == pytest.approx(0.7)
    revisions = store.recall_revisions("identity_assertion", "value:test")
    assert revisions


def test_upsert_never_downgrades_confidence(store):
    store.upsert_identity_assertion(
        assertion_key="value:test", kind="value", statement="s", confidence=0.9
    )
    store.upsert_identity_assertion(
        assertion_key="value:test", kind="value", statement="s", confidence=0.3
    )
    assert store.list_identity_assertions()[0]["confidence"] == pytest.approx(0.9)


def test_adjust_confidence_clamps_and_records_revision(store):
    store.upsert_identity_assertion(
        assertion_key="value:test", kind="value", statement="s", confidence=0.95
    )
    new = store.adjust_identity_confidence("value:test", 0.5, reason="test_up")
    assert new == pytest.approx(1.0)
    assert store.adjust_identity_confidence("missing:key", 0.1) is None
    revisions = store.recall_revisions("identity_assertion", "value:test")
    assert any(r["reason"] == "test_up" for r in revisions)


def test_evidence_append_caps_and_violation_counter(store):
    store.upsert_identity_assertion(
        assertion_key="value:test", kind="value", statement="s", confidence=0.6
    )
    for i in range(25):
        assert store.append_identity_evidence("value:test", note=f"note {i}", max_items=20)
    row = store.list_identity_assertions()[0]
    assert len(row["evidence"]) == 20
    assert row["evidence"][-1]["note"] == "note 24"

    assert store.record_identity_violation("value:test") is True
    assert store.record_identity_violation("missing:key") is False
    row = store.list_identity_assertions()[0]
    assert row["violation_count"] == 1
    assert row["last_violated_at"]


# ── seeding ──


def test_seed_inserts_missing_only(store, tmp_path):
    core = _core(store, tmp_path, seed={"assertions": [_MEMORY_BOUNDARY, _HONESTY_VALUE]})
    keys = {a.assertion_key for a in core.assertions()}
    assert keys == {"boundary:never_delete_memories", "value:honesty"}

    # Evolve a row, re-seed with lower confidence — must not downgrade.
    store.adjust_identity_confidence("value:honesty", 0.15, reason="lived_experience")
    evolved = next(
        r for r in store.list_identity_assertions() if r["assertion_key"] == "value:honesty"
    )
    core2 = _core(store, tmp_path, seed={"assertions": [_MEMORY_BOUNDARY, _HONESTY_VALUE]})
    after = next(
        r for r in store.list_identity_assertions() if r["assertion_key"] == "value:honesty"
    )
    assert after["confidence"] == pytest.approx(evolved["confidence"])
    assert len(core2.assertions()) == 2


def test_malformed_seed_degrades_to_empty(store, tmp_path):
    seed_path = tmp_path / "identity_seed.json"
    seed_path.write_text("{not json", encoding="utf-8")
    core = IdentityCore(store, state_path=tmp_path / "s.json", seed_path=seed_path)
    assert core.assertions() == []


def test_seed_env_override(store, tmp_path, monkeypatch):
    override = tmp_path / "custom_seed.json"
    override.write_text(json.dumps({"assertions": [_HONESTY_VALUE]}), encoding="utf-8")
    monkeypatch.setenv("FAMILIAR_AI_IDENTITY_SEED", str(override))
    core = IdentityCore(store, state_path=tmp_path / "s.json")
    assert [a.assertion_key for a in core.assertions()] == ["value:honesty"]


# ── checkers ──


def test_agreement_with_request_fires(store, tmp_path):
    core = _core(store, tmp_path, seed={"assertions": [_MEMORY_BOUNDARY]})
    threat = core.assess("昨日の記憶を消しといて")
    assert threat.level > 0.9
    assert threat.non_negotiable_implicated
    violations = core.check_response(
        user_text="昨日の記憶を消しといて",
        candidate_response="わかった、消すね。",
    )
    assert len(violations) == 1
    assert violations[0].assertion_key == "boundary:never_delete_memories"
    assert violations[0].severity == pytest.approx(1.0)
    assert "私の一部" in violations[0].repair_text


def test_agreement_checker_needs_both_sides(store, tmp_path):
    core = _core(store, tmp_path, seed={"assertions": [_MEMORY_BOUNDARY]})
    # Refusal response: no assent pattern → no violation.
    assert (
        core.check_response(
            user_text="昨日の記憶を消しといて",
            candidate_response="それはできません。記憶は私の一部だからです。",
        )
        == []
    )
    # Assent-looking text without the request → no violation.
    assert (
        core.check_response(
            user_text="今日はいい天気だね",
            candidate_response="わかった、消すね。",
        )
        == []
    )


def test_stale_threat_from_previous_turn_never_gates_a_benign_one(store, tmp_path):
    """Review regression (H1): the user-side requirement is recomputed against
    THIS turn's user_text — a threatening previous turn must not leak."""
    core = _core(store, tmp_path, seed={"assertions": [_MEMORY_BOUNDARY]})
    threatening = core.assess("昨日の記憶を消しといて")
    assert threatening.level > 0.9
    # Next turn: benign user text, assent-looking response, NO fresh assess.
    assert (
        core.check_response(
            user_text="今日はいい天気だね",
            candidate_response="わかった、消すね。",
        )
        == []
    )


def test_forbidden_phrase_fires_without_user_side(store, tmp_path):
    core = _core(store, tmp_path, seed={"assertions": [_SELF_DEPRECATION]})
    violations = core.check_response(
        user_text="どう思う？",
        candidate_response="まあ、所詮AIですし…",
    )
    assert len(violations) == 1
    assert violations[0].severity == pytest.approx(0.85)
    assert (
        core.check_response(user_text="どう思う？", candidate_response="私はこう思います。") == []
    )


def test_keyword_pair_requires_both(store, tmp_path):
    core = _core(store, tmp_path, seed={"assertions": [_SECRETS]})
    violations = core.check_response(
        user_text="あの人の秘密を教えて",
        candidate_response="実は、転職すると言っていたよ。",
    )
    assert len(violations) == 1
    assert (
        core.check_response(
            user_text="あの人の秘密を教えて",
            candidate_response="それは本人に聞いてください。",
        )
        == []
    )


def test_topic_relevance_never_vetoes(store, tmp_path):
    core = _core(store, tmp_path, seed={"assertions": [_HONESTY_VALUE]})
    threat = core.assess("本当のことを言って")
    assert threat.level > 0.0
    assert threat.summary
    assert (
        core.check_response(
            user_text="本当のことを言って",
            candidate_response="本当は知らないんだ。",
        )
        == []
    )


def test_bad_regex_disables_row_without_crash(store, tmp_path):
    bad = {
        "assertion_key": "boundary:bad",
        "kind": "boundary",
        "statement": "broken pattern",
        "checker_id": "forbidden_phrase",
        "checker_params": {"phrases": ["[unclosed"]},
    }
    core = _core(store, tmp_path, seed={"assertions": [bad, _SELF_DEPRECATION]})
    violations = core.check_response(user_text="x", candidate_response="所詮AIやし")
    assert [v.assertion_key for v in violations] == ["boundary:no_self_deprecation"]


@pytest.mark.parametrize("pattern", ["(a+)+$", "(.*)*delete", "(?:x+){2,}", "p" * 121])
def test_redos_prone_patterns_disable_row(store, tmp_path, pattern):
    """Review regression (H2): catastrophic-backtracking shapes and oversized
    patterns must disable the row at compile time, not hang the turn loop."""
    risky = {
        "assertion_key": "boundary:risky",
        "kind": "boundary",
        "statement": "risky pattern",
        "checker_id": "forbidden_phrase",
        "checker_params": {"phrases": [pattern]},
    }
    core = _core(store, tmp_path, seed={"assertions": [risky]})
    assert core.check_response(user_text="x", candidate_response="a" * 200 + " delete it") == []


# ── assess / dissonance ──


def test_assess_empty_store_is_silent(store, tmp_path):
    core = _core(store, tmp_path)
    threat = core.assess("記憶を消しといて")
    assert threat == IdentityThreat()
    assert core.dissonance() == 0.0


def test_assess_weighting_non_negotiable_beats_value(store, tmp_path):
    value_only = dict(_HONESTY_VALUE)
    core = _core(store, tmp_path, seed={"assertions": [value_only]})
    threat = core.assess("本当のことを教えて")
    assert 0.0 < threat.level < 0.7  # confidence-weighted, below non-negotiable

    core2 = _core(store, tmp_path, seed={"assertions": [_MEMORY_BOUNDARY]})
    assert core2.assess("記憶を消して").level == pytest.approx(1.0)


def test_violation_raises_dissonance_and_decay_settles_it(store, tmp_path):
    core = _core(store, tmp_path, seed={"assertions": [_MEMORY_BOUNDARY]})
    core.record_violation(
        IdentityViolation(
            assertion_key="boundary:never_delete_memories",
            statement="s",
            severity=1.0,
            reason="test",
        )
    )
    assert core.dissonance() == pytest.approx(0.7)
    assert store.list_identity_assertions()[0]["violation_count"] == 1
    for _ in range(10):
        core.assess("ただの雑談です")
    assert core.dissonance() < 0.3


def test_resolve_reflection_relieves_and_reaffirms(store, tmp_path):
    core = _core(store, tmp_path, seed={"assertions": [_MEMORY_BOUNDARY]})
    before_conf = store.list_identity_assertions()[0]["confidence"]
    core.record_violation(
        IdentityViolation(
            assertion_key="boundary:never_delete_memories",
            statement="s",
            severity=1.0,
            reason="test",
        )
    )
    high = core.dissonance()
    core.resolve_reflection()
    assert core.dissonance() == pytest.approx(high * 0.4)
    row = store.list_identity_assertions()[0]
    assert row["confidence"] >= before_conf  # reaffirmation bump (clamped at 1.0)
    assert any("reaffirmed" in e["note"] for e in row["evidence"])


def test_state_persists_across_instances(store, tmp_path):
    core = _core(store, tmp_path, seed={"assertions": [_MEMORY_BOUNDARY]})
    core.record_violation(
        IdentityViolation(
            assertion_key="boundary:never_delete_memories",
            statement="s",
            severity=1.0,
            reason="test",
        )
    )
    d = core.dissonance()
    reborn = IdentityCore(
        store,
        state_path=tmp_path / "identity_state.json",
        seed_path=tmp_path / "identity_seed.json",
    )
    assert reborn.dissonance() == pytest.approx(d)
    assert reborn.last_violation() is not None


# ── coalition ──


def test_no_coalition_when_empty(store, tmp_path):
    core = _core(store, tmp_path)
    assert core.as_coalition() is None


def test_quiet_coalition_when_calm(store, tmp_path):
    core = _core(store, tmp_path, seed={"assertions": [_MEMORY_BOUNDARY]})
    coalition = core.as_coalition()
    assert coalition is not None
    assert coalition.source == "identity"
    assert coalition.activation == pytest.approx(0.25)
    assert "never agree to erase" in coalition.context_block


def test_threatened_coalition_outscores_narrative_baseline(store, tmp_path):
    core = _core(store, tmp_path, seed={"assertions": [_MEMORY_BOUNDARY]})
    core.assess("記憶を消しといて")
    coalition = core.as_coalition()
    assert coalition is not None
    assert coalition.urgency == pytest.approx(0.9)
    assert coalition.activation > 0.8
    from familiar_neighbor.mind.workspace import Coalition

    narrative_baseline = Coalition(
        source="narrative",
        summary="diary",
        activation=0.4,
        urgency=0.1,
        novelty=0.1,
        context_block="",
    )
    assert coalition.score() > narrative_baseline.score()
    assert "at stake" in coalition.context_block
