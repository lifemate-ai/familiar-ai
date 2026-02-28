"""Tests for S-expression structure in SYSTEM_PROMPT and _interoception()."""

from __future__ import annotations

import time


from familiar_agent.agent import SYSTEM_PROMPT, MAX_ITERATIONS, _interoception


FORMATTED = SYSTEM_PROMPT.format(max_steps=MAX_ITERATIONS)


# ── SYSTEM_PROMPT: S-expression forms present ─────────────────────────────────


def test_system_prompt_contains_constraint_forms() -> None:
    """Critical rules should be expressed as (constraint ...) forms."""
    assert "(constraint" in FORMATTED


def test_system_prompt_contains_when_forms() -> None:
    """Conditional behaviours should use (when ...) forms."""
    assert "(when" in FORMATTED


def test_system_prompt_core_loop_is_sequence() -> None:
    """The core ReAct loop should be a (sequence ...) form."""
    assert "(sequence" in FORMATTED


def test_system_prompt_critical_constraint_has_priority() -> None:
    """At least one constraint should have :priority critical."""
    assert ":priority critical" in FORMATTED


def test_system_prompt_voice_constraint_present() -> None:
    """The say()-is-voice rule is the most critical — must appear as a constraint."""
    # Should be inside a constraint form
    idx = FORMATTED.index("(constraint")
    assert "say()" in FORMATTED[idx:]


def test_system_prompt_camera_legs_constraint_present() -> None:
    """Camera/legs independence must be expressed as a constraint."""
    # The independence rule should appear within a constraint block
    assert "(constraint" in FORMATTED
    assert "camera" in FORMATTED.lower() or "walk()" in FORMATTED


def test_system_prompt_camera_failure_when_form() -> None:
    """Camera failure handling should use a (when ...) form."""
    assert "(when" in FORMATTED
    lower = FORMATTED.lower()
    assert "camera" in lower or "see()" in lower


def test_system_prompt_health_awareness_when_form() -> None:
    """Health awareness rule should be a (when ...) form."""
    assert "(when" in FORMATTED
    assert "companion_status" in FORMATTED or "health" in FORMATTED.lower()


def test_system_prompt_sequence_has_steps() -> None:
    """(sequence ...) forms should contain nested step forms."""
    idx = FORMATTED.index("(sequence")
    # After (sequence, there should be at least one nested ( before the closing )
    segment = FORMATTED[idx : idx + 300]
    assert segment.count("(") >= 2  # sequence itself + at least one step


def test_system_prompt_no_all_caps_critical() -> None:
    """Old CRITICAL / IMPORTANT markers should be replaced by (constraint :priority critical)."""
    # The word CRITICAL should only appear in the S-expression form, not as a standalone word
    lines_with_critical = [
        line
        for line in FORMATTED.splitlines()
        if "CRITICAL" in line and "(constraint" not in line and ":priority" not in line
    ]
    assert lines_with_critical == [], (
        f"Found bare CRITICAL outside constraint: {lines_with_critical}"
    )


# ── _interoception: S-expression output ───────────────────────────────────────


def test_interoception_is_sexp() -> None:
    """_interoception() output should be wrapped in (interoception ...) form."""
    result = _interoception(time.time(), 0)
    assert result.strip().startswith("(interoception")


def test_interoception_contains_time_node() -> None:
    result = _interoception(time.time(), 0)
    assert "(time-of-day" in result


def test_interoception_contains_uptime_node() -> None:
    result = _interoception(time.time(), 0)
    assert "(uptime" in result


def test_interoception_contains_social_node() -> None:
    result = _interoception(time.time(), 0)
    assert "(social" in result


def test_interoception_private_flag() -> None:
    """interoception should be marked :private true so agent knows not to surface it."""
    result = _interoception(time.time(), 0)
    assert ":private true" in result


def test_interoception_zero_turns_social_feel() -> None:
    result = _interoception(time.time(), 0)
    assert "nobody" in result.lower() or "alone" in result.lower() or "yet" in result.lower()


def test_interoception_many_turns_social_feel() -> None:
    result = _interoception(time.time(), 10)
    assert (
        "talking" in result.lower() or "company" in result.lower() or "together" in result.lower()
    )


def test_interoception_fresh_uptime_feel() -> None:
    result = _interoception(time.time(), 0)
    assert "just" in result.lower() or "fresh" in result.lower() or "orient" in result.lower()


def test_interoception_long_uptime_feel() -> None:
    old_start = time.time() - 3600  # 60 minutes ago
    result = _interoception(old_start, 5)
    assert (
        "while" in result.lower() or "comfortable" in result.lower() or "settled" in result.lower()
    )


def test_interoception_balanced_parens() -> None:
    """S-expression output should have balanced parentheses."""
    result = _interoception(time.time(), 3)
    assert result.count("(") == result.count(")")
