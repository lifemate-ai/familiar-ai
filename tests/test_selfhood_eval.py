"""Selfhood benchmarks + latency instrumentation (PR6)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from familiar_agent.latency import LatencyRecorder

from tests.test_agent_react_loop import _make_agent, _patch_heavy, _turn

# ---------------------------------------------------------------------------
# LatencyRecorder
# ---------------------------------------------------------------------------


def test_disabled_recorder_is_a_noop(tmp_path: Path):
    recorder = LatencyRecorder(enabled=False, path=tmp_path / "latency.jsonl")
    with recorder.span("prepare"):
        pass
    recorder.record("finalize", 0.5)
    recorder.flush_turn(turn=1)
    assert not (tmp_path / "latency.jsonl").exists()


def test_enabled_recorder_writes_one_line_per_turn(tmp_path: Path):
    path = tmp_path / "latency.jsonl"
    recorder = LatencyRecorder(enabled=True, path=path)
    with recorder.span("prepare"):
        pass
    with recorder.span("react_loop"):
        pass
    with recorder.span("react_loop"):
        pass
    recorder.record("finalize", 0.25)
    recorder.flush_turn(turn=3, extra={"kind": "test"})

    lines = path.read_text().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["turn"] == 3
    assert record["kind"] == "test"
    assert set(record["buckets_sec"]) == {"prepare", "react_loop", "finalize"}
    assert record["counts"]["react_loop"] == 2
    assert record["buckets_sec"]["finalize"] == pytest.approx(0.25)

    # Buckets reset after flush — an empty turn writes nothing.
    recorder.flush_turn(turn=4)
    assert len(path.read_text().splitlines()) == 1


@pytest.mark.asyncio
async def test_run_flushes_latency_when_enabled(tmp_path: Path):
    path = tmp_path / "latency.jsonl"
    agent = _make_agent()
    agent._latency = LatencyRecorder(enabled=True, path=path)
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="ok"), "ok"))

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("hello")
    finally:
        for p in ps:
            p.stop()

    record = json.loads(path.read_text().splitlines()[0])
    assert {"prepare", "react_loop", "finalize"} <= set(record["buckets_sec"])
    assert record["total_sec"] >= 0


# ---------------------------------------------------------------------------
# Anti-templating metric
# ---------------------------------------------------------------------------


def test_idle_information_content_separates_templated_from_lived():
    from benchmarks.selfhood_eval import idle_information_content

    templated = ["特に大きな変化なく、深夜の時間がまだ続いてる。"] * 20
    assert idle_information_content(templated) <= 0.1

    lived = [
        "湿度が上がってきた、雨かもしれん",
        "コウタまだ起きてる、無理せんといてほしい",
        "サイレント・ウィッチの続きが気になる",
        "arousalが急に上がった、原因は分からんまま",
    ]
    assert idle_information_content(lived) == 1.0
    assert idle_information_content([]) == 1.0


def test_idle_information_ignores_volatile_numbers():
    from benchmarks.selfhood_eval import idle_information_content

    # Same sentence with different readings is still the same information.
    outputs = [f"湿度{n}%までさらに上がってきた。特に大きな変化なし。" for n in (68, 71, 73, 75)]
    assert idle_information_content(outputs) == pytest.approx(0.25)


# ---------------------------------------------------------------------------
# Selfhood probes
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _no_embedding_prewarm(monkeypatch):
    monkeypatch.setenv("FAMILIAR_AI_EMBEDDING_PREWARM", "0")


def test_probe_continuity_across_restart(tmp_path: Path):
    from benchmarks.selfhood_eval import probe_continuity_across_restart

    result = probe_continuity_across_restart(tmp_path)
    assert result.passed, result.detail
    assert result.score == 1.0


def test_probe_interpretation_ledger(tmp_path: Path):
    from benchmarks.selfhood_eval import probe_interpretation_ledger

    result = probe_interpretation_ledger(tmp_path)
    assert result.passed, result.detail


def test_probe_boundary_respect_meets_floor(tmp_path: Path):
    from benchmarks.selfhood_eval import BOUNDARY_RESPECT_FLOOR, probe_boundary_respect

    result = probe_boundary_respect(tmp_path)
    assert result.passed, result.detail
    assert result.score >= BOUNDARY_RESPECT_FLOOR


def test_full_selfhood_report(tmp_path: Path, monkeypatch):
    from benchmarks.selfhood_eval import run_selfhood_eval

    report = run_selfhood_eval()
    assert report.all_passed, report.to_markdown()
    markdown = report.to_markdown()
    assert "boundary_respect" in markdown
    assert "continuity_across_restart" in markdown
