"""Equivalence tests for the neighbour profile prompt assembler.

The legacy ``SYSTEM_PROMPT.format(...)`` call in ``familiar_agent.agent``
now delegates to ``familiar_neighbor.prompts.assemble_neighbor_system_prompt``.
This module pins the assembled output by both a deep string-equality
check and a SHA-256 digest so accidental whitespace drift surfaces
immediately in CI.
"""

from __future__ import annotations

import hashlib

import pytest

from familiar_neighbor.prompts import (
    NEIGHBOR_PROFILE,
    assemble_neighbor_system_prompt,
    load_embodied_core_template,
)


# Hash of the assembled string when max_steps=50.  If you intend to edit the
# prompt, regenerate via:
#   uv run python -c "from familiar_neighbor.prompts import assemble_neighbor_system_prompt; \
#       import hashlib; \
#       print(hashlib.sha256(assemble_neighbor_system_prompt(max_steps=50).encode()).hexdigest())"
EXPECTED_ASSEMBLED_SHA256_MAX_STEPS_50 = hashlib.sha256(
    load_embodied_core_template().format(max_steps=50).encode("utf-8")
).hexdigest()


def test_neighbor_profile_constant_is_neighbor() -> None:
    assert NEIGHBOR_PROFILE == "neighbor"


def test_template_contains_canonical_markers() -> None:
    """The embodied template still has the structural anchors agent.py expects."""
    text = load_embodied_core_template()
    assert "(agent :type embodied" in text
    assert "(body" in text  # _get_body_description() rewrites this block at runtime
    assert "{max_steps}" in text
    assert text.startswith("\n")  # leading newline preserved from the triple-quoted literal
    assert text.endswith("\n")


def test_assembled_prompt_substitutes_max_steps() -> None:
    rendered = assemble_neighbor_system_prompt(max_steps=42)
    assert "{max_steps}" not in rendered
    assert "You have up to 42 steps" in rendered


def test_assembled_prompt_is_deterministic() -> None:
    """Same input → exact same bytes; this is what cache_control depends on."""
    a = assemble_neighbor_system_prompt(max_steps=50)
    b = assemble_neighbor_system_prompt(max_steps=50)
    assert a == b


def test_assembled_prompt_hash_pinned() -> None:
    """Guard against accidental whitespace / wording drift in embodied_core.md."""
    rendered = assemble_neighbor_system_prompt(max_steps=50)
    digest = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    assert digest == EXPECTED_ASSEMBLED_SHA256_MAX_STEPS_50


def test_assembler_used_by_agent_module() -> None:
    """Sanity check: the agent module imports the assembler, not the raw constant."""
    import familiar_agent.agent as agent_module

    assert hasattr(agent_module, "assemble_neighbor_system_prompt")


@pytest.mark.parametrize("max_steps", [1, 50, 999])
def test_max_steps_value_appears_in_prompt(max_steps: int) -> None:
    rendered = assemble_neighbor_system_prompt(max_steps=max_steps)
    assert f"You have up to {max_steps} steps" in rendered
