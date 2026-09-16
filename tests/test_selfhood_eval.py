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


@pytest.mark.asyncio
async def test_run_records_loop_buckets_when_enabled(tmp_path: Path, monkeypatch):
    """Inside the react loop: one ``model_call`` per backend call, one
    ``tool:<name>`` per tool execution, and a counted ``retry:<kind>`` per
    re-ask — plus per-turn token sums in the flushed record."""
    from familiar_runtime.models.base import ToolCall

    monkeypatch.setenv("FAMILIAR_COHERENCE_CHECK", "1")
    path = tmp_path / "latency.jsonl"
    agent = _make_agent()
    agent._latency = LatencyRecorder(enabled=True, path=path)
    agent._check_response_coherence = AsyncMock(side_effect=["contradiction", None])

    tc = ToolCall(id="tc1", name="remember", input={"content": "x"})
    turn1 = _turn("tool_use", tool_calls=[tc])
    turn1.cache_read_tokens = 40
    turn1.cache_creation_tokens = 5
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (turn1, None),
            (_turn("end_turn", text="draft"), "draft"),
            (_turn("end_turn", text="fixed"), "fixed"),
        ]
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run("hello")
    finally:
        for p in ps:
            p.stop()

    assert result == "fixed"
    record = json.loads(path.read_text().splitlines()[0])
    counts = record["counts"]
    assert counts["model_call"] == 3
    assert counts["tool:remember"] == 1
    assert counts["retry:coherence"] == 1
    assert record["buckets_sec"]["model_call"] >= 0
    assert record["buckets_sec"]["tool:remember"] >= 0
    assert record["model_calls"] == 3
    assert record["input_tokens"] == 300
    assert record["output_tokens"] == 150
    assert record["cache_read_tokens"] == 40
    assert record["cache_creation_tokens"] == 5


@pytest.mark.asyncio
async def test_run_disabled_recorder_passes_backend_through(tmp_path: Path):
    """With the recorder off, the loop sees the raw backend (no proxy) and
    nothing is written."""
    from unittest.mock import patch

    from familiar_agent import agent as agent_mod

    path = tmp_path / "latency.jsonl"
    agent = _make_agent()
    agent._latency = LatencyRecorder(enabled=False, path=path)
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="ok"), "ok"))

    seen: list[object] = []
    real_loop = agent_mod.ReActLoop

    def _spy(*args, **kwargs):
        seen.append(kwargs["backend"])
        return real_loop(*args, **kwargs)

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        with patch.object(agent_mod, "ReActLoop", _spy):
            await agent.run("hello")
    finally:
        for p in ps:
            p.stop()

    assert seen == [agent.backend]
    assert not path.exists()


@pytest.mark.asyncio
async def test_retry_kinds_are_counted(tmp_path: Path):
    """Each RetryDecision site records its own zero-duration bucket."""
    from familiar_agent.latency import record_retry

    recorder = LatencyRecorder(enabled=True, path=tmp_path / "latency.jsonl")

    class _Agent:
        _latency = recorder

    for kind in ("identity", "reality", "voice", "coherence"):
        record_retry(_Agent(), kind)
    record_retry(object(), "identity")  # no recorder attribute: silently ignored

    recorder.flush_turn(turn=1)
    record = json.loads((tmp_path / "latency.jsonl").read_text().splitlines()[0])
    assert record["counts"] == {
        "retry:identity": 1,
        "retry:reality": 1,
        "retry:voice": 1,
        "retry:coherence": 1,
    }


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


def test_total_sec_counts_top_level_buckets_only(tmp_path: Path):
    """``model_call`` / ``tool:*`` live inside ``react_loop`` — nested spans
    must not inflate ``total_sec`` (it is the sum of the three top-level
    buckets, per-bucket fields kept as-is)."""
    path = tmp_path / "latency.jsonl"
    recorder = LatencyRecorder(enabled=True, path=path)
    recorder.record("prepare", 1.0)
    recorder.record("react_loop", 10.0)
    recorder.record("model_call", 4.0)
    recorder.record("tool:say", 5.0)
    recorder.record("retry:coherence", 0.0)
    recorder.record("finalize", 0.5)
    recorder.flush_turn(turn=1)

    record = json.loads(path.read_text().splitlines()[0])
    assert record["total_sec"] == pytest.approx(11.5)
    assert record["buckets_sec"]["model_call"] == pytest.approx(4.0)
    assert record["buckets_sec"]["tool:say"] == pytest.approx(5.0)


def test_total_sec_falls_back_to_all_buckets_without_top_level(tmp_path: Path):
    path = tmp_path / "latency.jsonl"
    recorder = LatencyRecorder(enabled=True, path=path)
    recorder.record("model_call", 2.0)
    recorder.flush_turn(turn=1)
    record = json.loads(path.read_text().splitlines()[0])
    assert record["total_sec"] == pytest.approx(2.0)
