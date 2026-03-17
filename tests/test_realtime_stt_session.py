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
    session._incoming_committed = committed_q
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
    session._incoming_committed = committed_q
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


@pytest.mark.asyncio
async def test_ensure_connected_replaces_disconnected_client(monkeypatch) -> None:
    class _StaleClient:
        def __init__(self) -> None:
            self.connected = False
            self.closed = False

        async def close(self) -> None:
            self.closed = True

    class _FreshClient:
        instances: list["_FreshClient"] = []

        def __init__(self, api_key: str) -> None:
            self.api_key = api_key
            self.connected = False
            self.closed = False
            self.on_committed = None
            self.on_partial = None
            _FreshClient.instances.append(self)

        async def connect(self) -> None:
            self.connected = True

        async def close(self) -> None:
            self.closed = True
            self.connected = False

    monkeypatch.setattr("familiar_agent.tools.realtime_stt.RealtimeSttClient", _FreshClient)

    session = RealtimeSttSession("dummy")
    stale = _StaleClient()
    session._stt_client = stale  # type: ignore[assignment]

    reconnected = await session._ensure_connected()

    assert reconnected is True
    assert stale.closed is True
    assert len(_FreshClient.instances) == 1
    fresh = _FreshClient.instances[0]
    assert session._stt_client is fresh
    assert fresh.on_committed is session._incoming_committed
    assert fresh.on_partial is session._incoming_partial


@pytest.mark.asyncio
async def test_ensure_connected_noop_when_client_is_alive(monkeypatch) -> None:
    session = RealtimeSttSession("dummy")
    session._stt_client = SimpleNamespace(connected=True)

    called = False

    async def _unexpected_connect() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(session, "_connect_client", _unexpected_connect)

    reconnected = await session._ensure_connected()

    assert reconnected is False
    assert called is False


@pytest.mark.asyncio
async def test_send_audio_uses_latest_client_reference() -> None:
    class _Client:
        def __init__(self) -> None:
            self.sent: list[bytes] = []

        async def send_audio(self, data: bytes) -> None:
            self.sent.append(data)

    session = RealtimeSttSession("dummy")
    first = _Client()
    second = _Client()

    session._stt_client = first  # type: ignore[assignment]
    await session._send_audio(b"first")
    session._stt_client = second  # type: ignore[assignment]
    await session._send_audio(b"second")

    assert first.sent == [b"first"]
    assert second.sent == [b"second"]
