"""Generic prompt fragments shared across runtime profiles.

These S-expression chunks were originally inlined in
``familiar_neighbor/prompts/embodied_core.md``. They were extracted here so
that future profiles (task agent, headless tools) can reuse them without
copying neighbour-specific embodied content.

Each loader returns the fragment **without a trailing newline**; the neighbour
assembler reinserts the surrounding whitespace via its template substitutions.
``load_step_budget_template`` preserves the ``{max_steps}`` placeholder so the
final ``.format(max_steps=...)`` call resolves it just like the legacy
``SYSTEM_PROMPT.format(max_steps=...)`` did.
"""

from __future__ import annotations

import importlib.resources

__all__ = [
    "load_react_loop",
    "load_voice_rules_generic",
    "load_language_match",
    "load_gricean_maxims",
    "load_self_check",
    "load_step_budget_template",
    "load_tool_rules",
    "assemble_runtime_core",
]


def _read_fragment(name: str) -> str:
    text = importlib.resources.files(__package__).joinpath(name).read_text(encoding="utf-8")
    if text.endswith("\n"):
        text = text[:-1]
    return text


def load_react_loop() -> str:
    """Return the generic ``(loop :id react ...)`` S-expression block."""
    return _read_fragment("react_loop.md")


def load_voice_rules_generic() -> str:
    """Return the generic ``voice-only-from-say`` constraint."""
    return _read_fragment("voice_rules.md")


def load_language_match() -> str:
    """Return the generic ``language-match`` constraint."""
    return _read_fragment("language_match.md")


def load_gricean_maxims() -> str:
    """Return the generic ``gricean-maxims`` constraint."""
    return _read_fragment("gricean_maxims.md")


def load_self_check() -> str:
    """Return the generic ``self-check-before-respond`` constraint."""
    return _read_fragment("self_check.md")


def load_step_budget_template() -> str:
    """Return the ``step-budget`` constraint with ``{max_steps}`` unresolved.

    Callers are expected to resolve ``{max_steps}`` via ``.format`` after
    splicing this fragment into the final prompt.
    """
    return _read_fragment("step_budget.md")


def load_tool_rules() -> str:
    """Return the generic developer ``(tools ...)`` catalogue."""
    return _read_fragment("tool_rules.md")


def assemble_runtime_core(*, max_steps: int) -> str:
    """Return a generic ReAct + tool-rules prompt usable outside the embodied profile.

    Profiles that do not need the embodied body / social rules can use this as
    a starting point. The neighbour profile interleaves these fragments into
    ``embodied_core.md`` separately and does not call this assembler.
    """
    parts = [
        load_react_loop(),
        "",
        load_voice_rules_generic(),
        "",
        load_language_match(),
        "",
        load_gricean_maxims(),
        "",
        load_self_check(),
        "",
        load_step_budget_template(),
        "",
        load_tool_rules(),
    ]
    return "\n".join(parts).format(max_steps=max_steps)
