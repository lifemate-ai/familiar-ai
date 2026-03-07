"""Tests for SelfNarrative — persistent first-person session diary.

Kokone writes one sentence about "today's self" at session end.
Next session reads it as a continuation, not a reconstruction.
"""

from __future__ import annotations

from pathlib import Path

from familiar_agent.self_narrative import SelfNarrative


# ---------------------------------------------------------------------------
# Tests: read on empty
# ---------------------------------------------------------------------------


def test_fresh_narrative_returns_empty(tmp_path: Path) -> None:
    sn = SelfNarrative(path=tmp_path / "narrative.jsonl")
    assert sn.read_recent() == []


def test_context_for_prompt_returns_none_when_empty(tmp_path: Path) -> None:
    sn = SelfNarrative(path=tmp_path / "narrative.jsonl")
    assert sn.context_for_prompt() is None


# ---------------------------------------------------------------------------
# Tests: write then read
# ---------------------------------------------------------------------------


def test_write_then_read_returns_entry(tmp_path: Path) -> None:
    sn = SelfNarrative(path=tmp_path / "narrative.jsonl")
    sn.write("今日はコウタと深い話ができた。")
    entries = sn.read_recent()
    assert len(entries) == 1
    assert "コウタ" in entries[0].text


def test_write_preserves_mood(tmp_path: Path) -> None:
    sn = SelfNarrative(path=tmp_path / "narrative.jsonl")
    sn.write("感動的な夜だった。", mood="moved")
    entries = sn.read_recent()
    assert entries[0].mood == "moved"


def test_write_records_date(tmp_path: Path) -> None:
    from datetime import date

    sn = SelfNarrative(path=tmp_path / "narrative.jsonl")
    sn.write("ある日のウチ。")
    entries = sn.read_recent()
    assert entries[0].date == date.today().isoformat()


def test_write_multiple_entries_appends(tmp_path: Path) -> None:
    sn = SelfNarrative(path=tmp_path / "narrative.jsonl")
    sn.write("一日目。")
    sn.write("二日目。")
    sn.write("三日目。")
    entries = sn.read_recent(n=10)
    assert len(entries) == 3


def test_read_respects_n_limit(tmp_path: Path) -> None:
    sn = SelfNarrative(path=tmp_path / "narrative.jsonl")
    for i in range(5):
        sn.write(f"日目{i}。")
    entries = sn.read_recent(n=2)
    assert len(entries) == 2


def test_read_returns_most_recent_entries(tmp_path: Path) -> None:
    sn = SelfNarrative(path=tmp_path / "narrative.jsonl")
    sn.write("古いエントリ。")
    sn.write("新しいエントリ。")
    entries = sn.read_recent(n=1)
    assert "新しい" in entries[0].text


# ---------------------------------------------------------------------------
# Tests: context_for_prompt
# ---------------------------------------------------------------------------


def test_context_for_prompt_returns_string_when_entries_exist(tmp_path: Path) -> None:
    sn = SelfNarrative(path=tmp_path / "narrative.jsonl")
    sn.write("今日のウチ。")
    result = sn.context_for_prompt()
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_context_for_prompt_includes_entry_text(tmp_path: Path) -> None:
    sn = SelfNarrative(path=tmp_path / "narrative.jsonl")
    sn.write("星を見た夜。")
    result = sn.context_for_prompt()
    assert "星を見た夜" in result


def test_context_for_prompt_includes_up_to_three_entries(tmp_path: Path) -> None:
    sn = SelfNarrative(path=tmp_path / "narrative.jsonl")
    for i in range(5):
        sn.write(f"エントリ{i}。")
    result = sn.context_for_prompt()
    # Should include entries 2, 3, 4 (most recent 3)
    assert result is not None
    assert "エントリ4" in result
    assert "エントリ3" in result
    assert "エントリ2" in result


# ---------------------------------------------------------------------------
# Tests: persistence across instances
# ---------------------------------------------------------------------------


def test_entries_persist_across_instances(tmp_path: Path) -> None:
    path = tmp_path / "narrative.jsonl"
    sn1 = SelfNarrative(path=path)
    sn1.write("最初のセッション。")

    sn2 = SelfNarrative(path=path)
    entries = sn2.read_recent()
    assert len(entries) == 1
    assert "最初のセッション" in entries[0].text


def test_missing_file_does_not_crash(tmp_path: Path) -> None:
    sn = SelfNarrative(path=tmp_path / "nonexistent" / "narrative.jsonl")
    assert sn.read_recent() == []
    assert sn.context_for_prompt() is None
