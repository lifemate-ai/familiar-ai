"""Context block primitives for runtime prompt assembly."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ContextBlock:
    """A budgetable block of context produced by runtime hooks."""

    source: str
    text: str
    priority: float
    stable: bool = False
    max_chars: int | None = None

    def rendered_text(self) -> str:
        """Return text clipped to the block-local budget."""
        if self.max_chars is None or len(self.text) <= self.max_chars:
            return self.text
        return self.text[: self.max_chars].rstrip()


def select_context_blocks(blocks: list[ContextBlock], *, max_chars: int) -> list[ContextBlock]:
    """Select context blocks by priority while preserving selected order."""
    ordered = sorted(enumerate(blocks), key=lambda item: item[1].priority, reverse=True)
    selected_indices: set[int] = set()
    used = 0
    for index, block in ordered:
        text = block.rendered_text()
        if not text:
            continue
        cost = len(text)
        if used + cost > max_chars and not block.stable:
            continue
        selected_indices.add(index)
        used += cost
    return [block for index, block in enumerate(blocks) if index in selected_indices]
