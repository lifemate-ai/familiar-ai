"""Self-ledger — persisted attention/meta state, who_am_i, shift ledger,
constitution-in-stable, and the compaction/restart recovery ritual.

The property under test throughout: "who I am" survives restarts and
compaction as state, not luck.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from familiar_neighbor.mind.attention_schema import AttentionSchema
from familiar_neighbor.mind.meta_monitor import MetaMonitor
from familiar_neighbor.mind.workspace import Coalition

from tests.test_agent_react_loop import _make_agent


def _coalition(source="curiosity", summary="wondering about the rain", activation=0.7):
    return Coalition(
        source=source,
        summary=summary,
        activation=activation,
        urgency=0.3,
        novelty=0.2,
        context_block=f"[{source}] {summary}",
    )


# ---------------------------------------------------------------------------
# AttentionSchema persistence
# ---------------------------------------------------------------------------


def test_attention_history_survives_restart(tmp_path: Path):
    state = tmp_path / "attention_state.json"
    schema = AttentionSchema(state_path=state)
    schema.update_focus(_coalition(source="scene"))
    schema.update_focus(_coalition(source="desire"))
    schema.update_focus(_coalition(source="desire"))

    reborn = AttentionSchema(state_path=state)
    history = reborn.focus_history()
    assert [e.source for e in history] == ["scene", "desire", "desire"]
    assert history[-1].turn == 3
    # The live winner object is not restored — it repopulates on first update.
    assert reborn.current_focus() is None
    # Turn numbering continues rather than restarting.
    reborn.update_focus(_coalition(source="memory"))
    assert reborn.focus_history()[-1].turn == 4
    # And the self-report works from restored state alone.
    assert reborn.self_report()


def test_attention_without_state_path_stays_ephemeral(tmp_path: Path):
    schema = AttentionSchema()
    schema.update_focus(_coalition())
    assert list(tmp_path.iterdir()) == []  # nothing written anywhere for us


def test_attention_corrupt_state_is_ignored(tmp_path: Path):
    state = tmp_path / "attention_state.json"
    state.write_text("not json")
    schema = AttentionSchema(state_path=state)  # must not raise
    assert schema.focus_history() == []


# ---------------------------------------------------------------------------
# MetaMonitor carryover
# ---------------------------------------------------------------------------


def test_meta_summary_carries_over_but_raw_window_does_not(tmp_path: Path):
    state = tmp_path / "meta_state.json"
    meta = MetaMonitor(state_path=state)
    meta.record_step(_coalition(source="desire"), action="say", confidence=0.8)
    meta.record_step(_coalition(source="desire"), action="see", confidence=0.6)
    session_summary = meta.summarize_session()

    reborn = MetaMonitor(state_path=state)
    assert reborn.step_count() == 0  # raw window is session-scoped by design
    assert reborn.previous_session_summary() == session_summary


def test_meta_without_state_path_has_empty_carryover():
    meta = MetaMonitor()
    meta.record_step(_coalition(), action="say", confidence=0.5)
    assert meta.previous_session_summary() == ""


# ---------------------------------------------------------------------------
# Interpretation-shift ledger (rides memory_revisions)
# ---------------------------------------------------------------------------


@pytest.fixture
def memory(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("FAMILIAR_AI_EMBEDDING_PREWARM", "0")
    from familiar_agent.tools.memory import ObservationMemory

    mem = ObservationMemory(db_path=str(tmp_path / "observations.db"))
    yield mem
    mem.close()


def test_interpretation_shift_roundtrip(memory):
    memory.record_interpretation_shift(
        topic="short replies",
        previous_reading="he is annoyed with me",
        new_reading="he is focused, not annoyed",
        reason="he said so directly",
    )
    shifts = memory.recall_interpretation_shifts(n=5)
    assert len(shifts) == 1
    assert shifts[0]["entity_key"] == "short replies"
    assert shifts[0]["new_text"] == "he is focused, not annoyed"
    assert shifts[0]["reason"] == "he said so directly"
    # It rides memory_revisions with a dedicated entity_type.
    assert shifts[0]["entity_type"] == "interpretation"


# ---------------------------------------------------------------------------
# who_am_i / note_interpretation_shift tools
# ---------------------------------------------------------------------------


def _stub_assertion(kind, statement, non_negotiable=False, confidence=0.8):
    stub = MagicMock()
    stub.kind = kind
    stub.statement = statement
    stub.non_negotiable = non_negotiable
    stub.confidence = confidence
    return stub


class _StubIdentity:
    """MagicMock refuses attributes named 'assertions' (assert-typo guard)."""

    def __init__(self, assertions, dissonance: float = 0.0):
        self._assertions = assertions
        self._dissonance = dissonance
        self.assertions_calls = 0

    def assertions(self):
        self.assertions_calls += 1
        return self._assertions

    def state_for_snapshot(self):
        snapshot = MagicMock()
        snapshot.dissonance = self._dissonance
        snapshot.threat_summary = ""
        return snapshot


@pytest.mark.asyncio
async def test_who_am_i_renders_constitution_state_and_shifts():
    from familiar_agent.tools.self_ledger import SelfLedgerTool

    agent = _make_agent()
    agent._identity = _StubIdentity(
        [
            _stub_assertion("boundary", "I do not agree to erase my memories", non_negotiable=True),
            _stub_assertion("value", "I say what I feel"),
        ]
    )
    agent._meta_monitor = MagicMock()
    agent._meta_monitor.previous_session_summary.return_value = "Session: 4 steps."
    agent._memory.recall_interpretation_shifts = MagicMock(
        return_value=[
            {
                "entity_key": "short replies",
                "previous_text": "annoyed",
                "new_text": "focused",
            }
        ]
    )

    tool = SelfLedgerTool(agent)
    text, image = await tool.call("who_am_i", {})
    assert image is None
    assert "I do not agree to erase my memories (non-negotiable)" in text
    assert "I say what I feel" in text
    assert "Session: 4 steps." in text
    assert "short replies" in text


@pytest.mark.asyncio
async def test_who_am_i_degrades_on_bare_agent():
    from familiar_agent.tools.self_ledger import SelfLedgerTool

    agent = _make_agent()  # no _identity, mocked memory without shift API
    agent._memory.recall_interpretation_shifts = None
    tool = SelfLedgerTool(agent)
    text, _ = await tool.call("who_am_i", {})
    assert isinstance(text, str) and text  # coherent answer, no crash


@pytest.mark.asyncio
async def test_note_interpretation_shift_writes_ledger():
    from familiar_agent.tools.self_ledger import SelfLedgerTool

    agent = _make_agent()
    agent._memory.record_interpretation_shift = MagicMock()
    tool = SelfLedgerTool(agent)
    text, _ = await tool.call(
        "note_interpretation_shift",
        {"topic": "t", "previous_reading": "a", "new_reading": "b", "reason": "r"},
    )
    assert "recorded" in text
    agent._memory.record_interpretation_shift.assert_called_once_with(
        topic="t", previous_reading="a", new_reading="b", reason="r"
    )

    text, _ = await tool.call("note_interpretation_shift", {"topic": "t"})
    assert text.startswith("Error:")


def test_self_ledger_tools_registered_when_tool_present():
    from familiar_agent.tools.self_ledger import SelfLedgerTool

    agent = _make_agent()
    agent._self_ledger_tool = SelfLedgerTool(agent)
    names = {d["name"] for d in agent._all_tool_defs}
    assert {"who_am_i", "note_interpretation_shift"} <= names


# ---------------------------------------------------------------------------
# Constitution in the STABLE prompt half
# ---------------------------------------------------------------------------


def test_constitution_joins_stable_not_variable():
    agent = _make_agent()
    identity = _StubIdentity(
        [_stub_assertion("boundary", "I refuse to erase memories", non_negotiable=True)]
    )
    agent._identity = identity

    stable, variable = agent._system_prompt()
    assert "[Constitution — what I hold, in my own words]" in stable
    assert "I refuse to erase memories (non-negotiable)" in stable
    assert "Constitution" not in variable
    # Rendered once per session: identity is not re-queried on later prompts.
    agent._system_prompt()
    assert identity.assertions_calls == 1


def test_stable_prompt_unchanged_without_identity():
    agent = _make_agent()
    stable, _ = agent._system_prompt()
    assert "Constitution" not in stable


# ---------------------------------------------------------------------------
# Recovery ritual (restart carryover + post-compaction re-anchor)
# ---------------------------------------------------------------------------


def test_self_ledger_carryover_context():
    agent = _make_agent()
    agent._meta_monitor = MagicMock()
    agent._meta_monitor.previous_session_summary.return_value = "Dominant attention: desire."
    agent._memory.recall_interpretation_shifts = MagicMock(
        return_value=[{"entity_key": "silence", "new_text": "he needs space", "previous_text": "x"}]
    )
    ctx = agent._self_ledger_carryover_context()
    assert "[Last session's metacognitive thread]" in ctx
    assert "Dominant attention: desire." in ctx
    assert "silence" in ctx and "he needs space" in ctx


def test_post_compact_recovery_context_mentions_who_am_i():
    agent = _make_agent()
    agent._memory.recall_interpretation_shifts = MagicMock(return_value=[])
    ctx = agent._post_compact_recovery_context()
    assert "who_am_i" in ctx
    assert "constitution" in ctx.lower()


@pytest.mark.asyncio
async def test_compaction_sets_pending_and_next_turn_injects_recovery():
    """_compact_messages flags recovery; the next full turn's continuity
    context leads with the re-anchor block."""
    from unittest.mock import AsyncMock

    from tests.test_agent_react_loop import _patch_heavy, _turn

    agent = _make_agent()
    agent._memory.recall_interpretation_shifts = MagicMock(return_value=[])
    agent.backend.complete = AsyncMock(return_value="summary of earlier talk")
    agent._utility_backend = agent.backend
    agent.messages = [{"role": "user", "content": f"message {i}"} for i in range(12)]

    await agent._compact_messages(keep_last=4)
    assert agent._post_compact is True
    assert agent._post_compact_recovery_pending is True

    captured: dict = {}

    async def _spy_stream_turn(**kwargs):
        system = kwargs.get("system")
        captured["variable"] = system[1] if isinstance(system, tuple) else str(system)
        return (_turn("end_turn", text="ok"), "ok")

    agent.backend.stream_turn = AsyncMock(side_effect=_spy_stream_turn)
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("そういえば、昨日の続きなんだけど、あれからどう思う?")
    finally:
        for p in ps:
            p.stop()

    assert "[Post-compaction recovery]" in captured["variable"]
    assert agent._post_compact_recovery_pending is False
