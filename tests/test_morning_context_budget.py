"""Tests for morning reconstruction context selection under budget."""

from __future__ import annotations

from familiar_agent.agent import EmbodiedAgent


def test_select_context_blocks_prefers_higher_priority_within_budget() -> None:
    blocks = [
        ("low-a", 0.2),
        ("high-a", 0.9),
        ("mid-a", 0.5),
    ]
    selected = EmbodiedAgent._select_context_blocks(blocks, max_chars=len("high-a\n\nmid-a"))
    assert "high-a" in selected
    assert "mid-a" in selected
    assert "low-a" not in selected


def test_select_context_blocks_restores_original_order_after_selection() -> None:
    blocks = [
        ("first", 0.4),
        ("second", 0.9),
        ("third", 0.8),
    ]
    selected = EmbodiedAgent._select_context_blocks(blocks, max_chars=100)
    assert selected == ["first", "second", "third"]


def test_select_context_blocks_returns_all_when_budget_disabled() -> None:
    blocks = [("a", 0.1), ("b", 0.2)]
    selected = EmbodiedAgent._select_context_blocks(blocks, max_chars=0)
    assert selected == ["a", "b"]
