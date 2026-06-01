"""Tests for the generic runtime prompt fragments.

These pin the shape (no trailing newline, no surprise placeholders) and the
contents of each fragment loader in ``familiar_runtime.prompts``.  They also
sanity-check ``assemble_runtime_core`` so a future task-only profile can use
it without surprises.
"""

from __future__ import annotations

import hashlib

import pytest

from familiar_runtime import prompts as runtime_prompts


_LOADERS = [
    "load_react_loop",
    "load_voice_rules_generic",
    "load_language_match",
    "load_gricean_maxims",
    "load_self_check",
    "load_step_budget_template",
    "load_tool_rules",
]


@pytest.mark.parametrize("loader_name", _LOADERS)
def test_loader_returns_non_empty_string_without_trailing_newline(loader_name: str) -> None:
    loader = getattr(runtime_prompts, loader_name)
    text = loader()
    assert isinstance(text, str)
    assert text  # non-empty
    assert not text.endswith("\n"), (
        f"{loader_name} must not end with a trailing newline; the embodied template "
        f"already supplies the newline at the placeholder line."
    )


def test_react_loop_contains_react_anchor() -> None:
    text = runtime_prompts.load_react_loop()
    assert "(loop :id react" in text
    assert "(think" in text
    assert "(decide" in text


def test_voice_rules_generic_marks_silent_text() -> None:
    text = runtime_prompts.load_voice_rules_generic()
    assert "voice-only-from-say" in text
    assert "Text output is SILENT" in text


def test_language_match_constraint() -> None:
    text = runtime_prompts.load_language_match()
    assert "language-match" in text
    assert "same language the user used" in text


def test_gricean_maxims_lists_all_four() -> None:
    text = runtime_prompts.load_gricean_maxims()
    assert "gricean-maxims" in text
    for maxim in ("quantity", "quality", "relation", "manner"):
        assert f":id {maxim}" in text


def test_self_check_targets_structured_activity() -> None:
    text = runtime_prompts.load_self_check()
    assert "self-check-before-respond" in text
    assert "shiritori" in text


def test_step_budget_template_keeps_placeholder_unresolved() -> None:
    """The fragment must still contain ``{max_steps}`` so callers can ``.format`` it."""
    text = runtime_prompts.load_step_budget_template()
    assert "{max_steps}" in text
    assert "step-budget" in text


def test_step_budget_template_resolves_via_format() -> None:
    rendered = runtime_prompts.load_step_budget_template().format(max_steps=7)
    assert "{max_steps}" not in rendered
    assert "You have up to 7 steps" in rendered


def test_tool_rules_lists_developer_tools() -> None:
    text = runtime_prompts.load_tool_rules()
    assert "(tools" in text
    for tool_id in ("read_file", "write_file", "edit_file", "bash"):
        assert f":id {tool_id}" in text


def test_assemble_runtime_core_is_deterministic() -> None:
    a = runtime_prompts.assemble_runtime_core(max_steps=50)
    b = runtime_prompts.assemble_runtime_core(max_steps=50)
    assert a == b
    assert "{max_steps}" not in a
    assert "You have up to 50 steps" in a


def test_assemble_runtime_core_pinned_hash() -> None:
    """Guard against accidental drift in the generic prompt skeleton.

    Regenerate via:
      uv run python -c "from familiar_runtime.prompts import assemble_runtime_core; \\
          import hashlib; \\
          print(hashlib.sha256(assemble_runtime_core(max_steps=50).encode()).hexdigest())"
    """
    rendered = runtime_prompts.assemble_runtime_core(max_steps=50)
    digest = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    # Pinned after the initial extraction from embodied_core.md.
    expected = "1a51de62f078ce347e0d1f41933c49bc1f6f2e7e3b1dd390c4ab809c516d10bc"
    assert digest == expected
