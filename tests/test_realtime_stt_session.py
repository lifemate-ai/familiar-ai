"""Tests for realtime STT session filtering and deduplication."""

from __future__ import annotations

import asyncio
import contextlib
from types import SimpleNamespace

import pytest

from familiar_agent.realtime_stt_session import RealtimeSttSession, _normalize_for_dedupe


def test_normalize_for_dedupe_collapses_spacing_and_trailing_punctuation() -> None:
    assert _normalize_for_dedupe("  こんにちは。 ") == "こんにちは"
    assert _normalize_for_dedupe("Hello   world!!") == "hello world"
    assert _normalize_for_dedupe("「テスト」") == "テスト"


@pytest.mark.asyncio
async def test_committed_relay_drops_same_text_within_dedupe_window(monkeypatch) -> None:
    session = RealtimeSttSession("dummy")
    committed_q: asyncio.Queue[str] = asyncio.Queue()
    input_q: asyncio.Queue[str | None] = asyncio.Queue()
    session._stt_client = SimpleNamespace(on_committed=committed_q)
    session._committed_queue = input_q

    forwarded: list[str] = []
    session.on_committed = forwarded.append

    ts = iter([100.0, 101.0, 104.5])
    monkeypatch.setattr("familiar_agent.realtime_stt_session.time.time", lambda: next(ts))

    task = asyncio.create_task(session._committed_relay())
    await committed_q.put("こんにちは")
    await committed_q.put(" こんにちは。 ")
    await committed_q.put("こんにちは")
    await asyncio.sleep(0.05)
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task

    queued: list[str] = []
    while not input_q.empty():
        item = input_q.get_nowait()
        assert isinstance(item, str)
        queued.append(item)

    assert forwarded == ["こんにちは", "こんにちは"]
    assert queued == ["こんにちは", "こんにちは"]


@pytest.mark.asyncio
async def test_committed_relay_keeps_different_texts(monkeypatch) -> None:
    session = RealtimeSttSession("dummy")
    committed_q: asyncio.Queue[str] = asyncio.Queue()
    input_q: asyncio.Queue[str | None] = asyncio.Queue()
    session._stt_client = SimpleNamespace(on_committed=committed_q)
    session._committed_queue = input_q

    ts = iter([200.0, 200.5])
    monkeypatch.setattr("familiar_agent.realtime_stt_session.time.time", lambda: next(ts))

    task = asyncio.create_task(session._committed_relay())
    await committed_q.put("こんにちは")
    await committed_q.put("こんばんは")
    await asyncio.sleep(0.05)
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task

    queued: list[str] = []
    while not input_q.empty():
        item = input_q.get_nowait()
        assert isinstance(item, str)
        queued.append(item)

    assert queued == ["こんにちは", "こんばんは"]
