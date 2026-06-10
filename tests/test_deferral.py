"""Deferred-topic detection: "あとで話す" must not be lost.

When the companion defers a topic ("後で話すわ", "また今度説明する"), the agent
records it as unfinished business so it can naturally bring the topic back up
later — and the model can resolve it via the new resolve_unfinished_business
tool once the conversation returns to it.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from familiar_agent.tools.memory import MemoryTool, ObservationMemory, _EmbeddingModel
from familiar_neighbor.mind.deferral import detect_deferral


class TestDetectDeferral:
    @pytest.mark.parametrize(
        "text",
        [
            "その話はあとで話すわ",
            "詳しくは後で説明するから",
            "また今度ゆっくり話そう",
            "その件は後日相談させて",
            "I'll tell you later, promise",
            "let's talk about it another time",
        ],
    )
    def test_deferrals_detected(self, text):
        snippet = detect_deferral(text)
        assert snippet is not None
        assert snippet in text or len(snippet) <= 120

    @pytest.mark.parametrize(
        "text",
        [
            "おはよう",
            "今日は疲れたわ",
            "あとでお風呂入る",  # doing something later, not deferring a topic
            "これ直しといて",
            "やったー！うまくいった",
            "",
        ],
    )
    def test_non_deferrals_ignored(self, text):
        assert detect_deferral(text) is None

    def test_snippet_is_bounded(self):
        long = "また今度話すわ。" + "あ" * 300
        snippet = detect_deferral(long)
        assert snippet is not None
        assert len(snippet) <= 120


# ── resolve_unfinished_business tool ──


@pytest.fixture
def memory_tool(tmp_path):
    with patch.object(_EmbeddingModel, "pre_warm"):
        store = ObservationMemory(db_path=str(tmp_path / "obs.db"))
    tool = MemoryTool(store)
    yield tool, store
    store.close()


def test_resolve_tool_is_defined(memory_tool):
    tool, _store = memory_tool
    names = {d["name"] for d in tool.get_tool_definitions()}
    assert "resolve_unfinished_business" in names


@pytest.mark.asyncio
async def test_resolve_tool_resolves_entry(memory_tool):
    tool, store = memory_tool
    business_id = store.open_unfinished_business(summary="deferred: 旅行の話")
    assert any(b["id"] == business_id for b in store.list_unfinished_business())

    text, image = await tool.call("resolve_unfinished_business", {"id": business_id})
    assert image is None
    assert "resolved" in text.lower() or "✓" in text
    assert not any(b["id"] == business_id for b in store.list_unfinished_business())


@pytest.mark.asyncio
async def test_resolve_tool_unknown_id(memory_tool):
    tool, _store = memory_tool
    text, _ = await tool.call("resolve_unfinished_business", {"id": "nope"})
    assert "not" in text.lower() or "error" in text.lower()
