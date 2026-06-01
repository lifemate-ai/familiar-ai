"""Prompt assets and assemblers for the neighbour profile.

The historical ``SYSTEM_PROMPT`` lived inline in ``familiar_agent.agent``.
This package owns the neighbour-specific text (body, social rules, embodied
constraints). Generic ReAct / tool / language fragments live in
``familiar_runtime.prompts`` and are spliced into ``embodied_core.md`` at the
``{react_loop}``, ``{voice_rules_generic}``, ``{language_match}``,
``{gricean_maxims}``, ``{self_check}``, ``{step_budget}`` and ``{tool_rules}``
placeholders.

``assemble_neighbor_system_prompt`` is byte-for-byte equivalent to the legacy
``SYSTEM_PROMPT.format(max_steps=...)`` call site; the equivalence is pinned
by SHA-256 hash in ``tests/test_prompt_assembly.py``.
"""

from __future__ import annotations

import importlib.resources

from familiar_runtime import prompts as runtime_prompts

NEIGHBOR_PROFILE = "neighbor"

__all__ = [
    "NEIGHBOR_PROFILE",
    "assemble_neighbor_system_prompt",
    "load_embodied_core_template",
]


def _read_resource(name: str) -> str:
    return importlib.resources.files(__package__).joinpath(name).read_text(encoding="utf-8")


def load_embodied_core_template() -> str:
    """Return the raw embodied-core prompt template.

    The template still contains ``{react_loop}`` etc. runtime placeholders and
    the ``{max_steps}`` step-budget placeholder; resolve them via
    ``assemble_neighbor_system_prompt``.
    """
    return _read_resource("embodied_core.md")


def assemble_neighbor_system_prompt(*, max_steps: int) -> str:
    """Materialise the neighbour profile system prompt for one run.

    Equivalent to the legacy ``SYSTEM_PROMPT.format(max_steps=max_steps)`` call
    site in ``familiar_agent.agent``. The output is byte-for-byte stable and is
    pinned by ``tests/test_prompt_assembly.py``.
    """
    text = load_embodied_core_template()
    text = text.replace("{react_loop}", runtime_prompts.load_react_loop())
    text = text.replace("{voice_rules_generic}", runtime_prompts.load_voice_rules_generic())
    text = text.replace("{language_match}", runtime_prompts.load_language_match())
    text = text.replace("{gricean_maxims}", runtime_prompts.load_gricean_maxims())
    text = text.replace("{self_check}", runtime_prompts.load_self_check())
    text = text.replace("{step_budget}", runtime_prompts.load_step_budget_template())
    text = text.replace("{tool_rules}", runtime_prompts.load_tool_rules())
    return text.format(max_steps=max_steps)
