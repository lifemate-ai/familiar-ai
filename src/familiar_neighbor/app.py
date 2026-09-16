"""Neighbor profile descriptors.

The existing `familiar_agent.EmbodiedAgent` remains the compatibility entry point in this PR.
This module gives the new runtime architecture an explicit neighbor profile boundary without
moving cognition modules prematurely.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class NeighborProfile:
    """Configuration for the embodied companion specialization."""

    name: str = "neighbor"
    tool_tags: set[str] = field(default_factory=lambda: {"neighbor"})
    context_budget_chars: int = 6000
