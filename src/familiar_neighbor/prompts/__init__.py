"""Prompt assets and assemblers for the neighbour profile.

The historical ``SYSTEM_PROMPT`` lived inline in ``familiar_agent.agent``;
this package owns the static text now. ``assemble_neighbor_system_prompt``
applies the per-run ``{max_steps}`` substitution and returns exactly the
string the runtime used to compute by ``SYSTEM_PROMPT.format(...)``.
"""

from __future__ import annotations

import importlib.resources

NEIGHBOR_PROFILE = "neighbor"

__all__ = [
    "NEIGHBOR_PROFILE",
    "assemble_neighbor_system_prompt",
    "load_embodied_core_template",
]


def _read_resource(name: str) -> str:
    return importlib.resources.files(__package__).joinpath(name).read_text(encoding="utf-8")


def load_embodied_core_template() -> str:
    """Return the raw embodied-core prompt template (with ``{max_steps}``)."""
    return _read_resource("embodied_core.md")


def assemble_neighbor_system_prompt(*, max_steps: int) -> str:
    """Materialise the neighbour profile system prompt for one run.

    Equivalent to the legacy ``SYSTEM_PROMPT.format(max_steps=max_steps)``
    call site in ``familiar_agent.agent``.
    """
    return load_embodied_core_template().format(max_steps=max_steps)
