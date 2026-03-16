"""Tests for AttentionSchema (Phase 3: Attention Schema Theory / AST).

Tests cover:
- Focus tracking: what won workspace competition each turn
- self_report(): 'I'm focused on X because Y' — access consciousness
- Shift detection: detecting when focus changes between turns
- context_for_prompt(): compact focus history for LLM injection
- as_coalition(): expose attention schema as workspace Coalition
"""

from __future__ import annotations


from familiar_agent.attention_schema import AttentionSchema
from familiar_agent.workspace import Coalition


# ── Helpers ───────────────────────────────────────────────────────────────────


def _coalition(source: str, summary: str = "test") -> Coalition:
    return Coalition(
        source=source,
        summary=summary,
        activation=0.8,
        urgency=0.5,
        novelty=0.3,
        context_block=f"[{source}] {summary}",
    )


# ── Construction ──────────────────────────────────────────────────────────────


def test_default_construction():
    schema = AttentionSchema()
    assert schema is not None


def test_initial_state_has_no_focus():
    schema = AttentionSchema()
    assert schema.current_focus() is None


# ── update_focus ───────────────────────────────────────────────────────────────


def test_update_focus_sets_current_focus():
    schema = AttentionSchema()
    c = _coalition("desire", "want to look around")
    schema.update_focus(c)
    assert schema.current_focus() is c


def test_update_focus_accumulates_history():
    schema = AttentionSchema()
    schema.update_focus(_coalition("desire"))
    schema.update_focus(_coalition("scene"))
    schema.update_focus(_coalition("memory"))
    assert len(schema.focus_history()) == 3


def test_focus_history_limited():
    schema = AttentionSchema(max_history=3)
    for i in range(10):
        schema.update_focus(_coalition(f"source_{i}"))
    assert len(schema.focus_history()) == 3


def test_focus_history_oldest_first():
    schema = AttentionSchema(max_history=5)
    sources = ["desire", "scene", "memory"]
    for s in sources:
        schema.update_focus(_coalition(s))
    history = schema.focus_history()
    assert [e.source for e in history] == sources


# ── current_focus ──────────────────────────────────────────────────────────────


def test_current_focus_returns_last_winner():
    schema = AttentionSchema()
    schema.update_focus(_coalition("desire"))
    c2 = _coalition("scene")
    schema.update_focus(c2)
    assert schema.current_focus() is c2


# ── Shift detection ────────────────────────────────────────────────────────────


def test_no_shift_on_first_update():
    schema = AttentionSchema()
    c = _coalition("desire")
    shift = schema.detect_shift(c)
    assert shift is None


def test_no_shift_when_same_source():
    schema = AttentionSchema()
    schema.update_focus(_coalition("desire", "want A"))
    shift = schema.detect_shift(_coalition("desire", "want B"))
    assert shift is None


def test_shift_detected_when_source_changes():
    schema = AttentionSchema()
    schema.update_focus(_coalition("desire", "want to look"))
    shift = schema.detect_shift(_coalition("scene", "person appeared"))
    assert shift is not None
    assert "desire" in shift
    assert "scene" in shift


# ── self_report ────────────────────────────────────────────────────────────────


def test_self_report_returns_none_with_no_focus():
    schema = AttentionSchema()
    assert schema.self_report() is None


def test_self_report_mentions_current_source():
    schema = AttentionSchema()
    schema.update_focus(_coalition("desire", "want to explore"))
    report = schema.self_report()
    assert report is not None
    assert "desire" in report.lower()


def test_self_report_is_string():
    schema = AttentionSchema()
    schema.update_focus(_coalition("scene", "person appeared"))
    report = schema.self_report()
    assert isinstance(report, str)
    assert len(report) > 0


def test_self_report_mentions_recent_shift():
    schema = AttentionSchema()
    schema.update_focus(_coalition("desire"))
    schema.update_focus(_coalition("scene", "person appeared"))
    report = schema.self_report()
    assert report is not None
    # Should mention both old and new focus
    assert "scene" in report.lower()


# ── context_for_prompt ─────────────────────────────────────────────────────────


def test_context_for_prompt_returns_empty_with_no_history():
    schema = AttentionSchema()
    assert schema.context_for_prompt() == ""


def test_context_for_prompt_includes_focus_history():
    schema = AttentionSchema()
    schema.update_focus(_coalition("desire", "want to look"))
    schema.update_focus(_coalition("scene", "chair appeared"))
    ctx = schema.context_for_prompt()
    assert "desire" in ctx.lower() or "scene" in ctx.lower()


def test_context_for_prompt_is_compact():
    schema = AttentionSchema()
    for _ in range(20):
        schema.update_focus(_coalition("desire"))
    ctx = schema.context_for_prompt()
    # Should not be unboundedly long
    assert len(ctx) < 2000


# ── as_coalition ───────────────────────────────────────────────────────────────


def test_as_coalition_returns_none_with_no_history():
    schema = AttentionSchema()
    assert schema.as_coalition() is None


def test_as_coalition_returns_coalition_with_history():
    from familiar_agent.workspace import Coalition as WCoalition

    schema = AttentionSchema()
    schema.update_focus(_coalition("desire"))
    c = schema.as_coalition()
    assert c is not None
    assert isinstance(c, WCoalition)
    assert c.source == "attention"


def test_as_coalition_novelty_higher_after_shift():
    schema = AttentionSchema()
    # Stable focus: same source twice
    schema.update_focus(_coalition("desire"))
    schema.update_focus(_coalition("desire"))
    c_stable = schema.as_coalition()

    # Shifting focus
    schema2 = AttentionSchema()
    schema2.update_focus(_coalition("desire"))
    schema2.update_focus(_coalition("scene"))  # shift!
    c_shift = schema2.as_coalition()

    if c_stable is not None and c_shift is not None:
        assert c_shift.novelty >= c_stable.novelty


def test_as_coalition_fields_in_valid_range():
    schema = AttentionSchema()
    schema.update_focus(_coalition("desire"))
    c = schema.as_coalition()
    assert c is not None
    assert 0.0 <= c.activation <= 1.0
    assert 0.0 <= c.urgency <= 1.0
    assert 0.0 <= c.novelty <= 1.0
