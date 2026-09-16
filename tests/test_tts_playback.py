"""Tests for the TTS playback queue — say() must not stall the turn.

Synthesis (HTTP) is awaited inline; playback is handed to a single worker that
plays files one after another. The voice guard's start/end hooks fire at real
playback boundaries, from the worker, not at enqueue time.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from familiar_agent.tts_playback import PlaybackQueue

# ---------------------------------------------------------------------------
# PlaybackQueue unit tests
# ---------------------------------------------------------------------------


def _gated_player(gate: asyncio.Event, log: list[str]):
    async def play(path: str) -> list[str]:
        log.append(f"start:{path}")
        await gate.wait()
        log.append(f"end:{path}")
        return ["local"]

    return play


@pytest.mark.asyncio
async def test_enqueue_returns_before_playback_completes():
    gate = asyncio.Event()
    log: list[str] = []
    queue = PlaybackQueue(play=_gated_player(gate, log))

    fut = queue.enqueue("a.wav")
    await asyncio.sleep(0)  # let the worker pick the item up

    assert not fut.done()
    assert queue.is_speaking is True
    assert log == ["start:a.wav"]

    gate.set()
    assert await fut == ["local"]
    await queue.wait_idle()
    assert queue.is_speaking is False
    assert log == ["start:a.wav", "end:a.wav"]


@pytest.mark.asyncio
async def test_two_items_play_sequentially_never_overlap():
    gate = asyncio.Event()
    log: list[str] = []
    queue = PlaybackQueue(play=_gated_player(gate, log))

    f1 = queue.enqueue("one.wav")
    f2 = queue.enqueue("two.wav")
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    # Second item must not start while the first is still playing.
    assert log == ["start:one.wav"]

    gate.set()
    await asyncio.gather(f1, f2)
    await queue.wait_idle()
    assert log == ["start:one.wav", "end:one.wav", "start:two.wav", "end:two.wav"]


@pytest.mark.asyncio
async def test_on_done_fires_after_playback_with_played_via():
    done: list[list[str]] = []
    queue = PlaybackQueue(play=AsyncMock(return_value=["camera", "local"]))

    queue.enqueue("x.wav", on_done=lambda played: done.append(played))
    await queue.wait_idle()

    assert done == [["camera", "local"]]


@pytest.mark.asyncio
async def test_player_exception_does_not_kill_worker():
    calls: list[str] = []

    async def play(path: str) -> list[str]:
        calls.append(path)
        if path == "bad.wav":
            raise RuntimeError("boom")
        return ["local"]

    queue = PlaybackQueue(play=play)
    f_bad = queue.enqueue("bad.wav")
    f_ok = queue.enqueue("ok.wav")
    assert await f_bad == []
    assert await f_ok == ["local"]
    assert calls == ["bad.wav", "ok.wav"]


@pytest.mark.asyncio
async def test_wait_idle_timeout_returns_false_while_still_speaking():
    gate = asyncio.Event()
    queue = PlaybackQueue(play=_gated_player(gate, []))
    queue.enqueue("slow.wav")

    assert await queue.wait_idle(timeout=0.01) is False
    gate.set()
    assert await queue.wait_idle(timeout=1.0) is True


@pytest.mark.asyncio
async def test_wait_idle_on_fresh_queue_is_immediate():
    queue = PlaybackQueue(play=AsyncMock(return_value=["local"]))
    assert await queue.wait_idle(timeout=0.01) is True
    assert queue.is_speaking is False


@pytest.mark.asyncio
async def test_stop_cancels_current_and_drops_pending():
    gate = asyncio.Event()
    log: list[str] = []
    done: list[list[str]] = []
    queue = PlaybackQueue(play=_gated_player(gate, log))

    f1 = queue.enqueue("cur.wav", on_done=done.append)
    f2 = queue.enqueue("pending.wav", on_done=done.append)
    await asyncio.sleep(0)

    await queue.stop()

    assert f1.cancelled() or f1.done()
    assert f2.cancelled()
    # Cleanup callbacks still run for both so temp files never leak.
    assert len(done) == 2
    assert "start:pending.wav" not in log
    assert queue.is_speaking is False


@pytest.mark.asyncio
async def test_per_item_play_override():
    default = AsyncMock(return_value=["local"])
    override = AsyncMock(return_value=["camera"])
    queue = PlaybackQueue(play=default)

    assert await queue.enqueue("a.wav", play=override) == ["camera"]
    default.assert_not_awaited()
    override.assert_awaited_once_with("a.wav")


# ---------------------------------------------------------------------------
# TTSTool integration: say() + queue + voice guard
# ---------------------------------------------------------------------------


def _make_tts(monkeypatch, blocking: bool | None = None):
    from familiar_agent.tools.tts import TTSTool

    if blocking is None:
        monkeypatch.delenv("FAMILIAR_TTS_BLOCKING", raising=False)
    else:
        monkeypatch.setenv("FAMILIAR_TTS_BLOCKING", "1" if blocking else "0")
    with patch("familiar_agent.tools.tts._ensure_go2rtc"):
        tool = TTSTool(api_key="k", voice_id="v", output="local")
    tool._voice_guard = MagicMock()
    return tool


def _mock_session(payload: bytes = b"fake_mp3_data"):
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "audio/mpeg"}
    mock_response.read = AsyncMock(return_value=payload)
    mock_response.content = _FakeChunks([payload])
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    return mock_session


@pytest.mark.asyncio
async def test_say_returns_before_playback_finishes(monkeypatch, tmp_path):
    tool = _make_tts(monkeypatch)
    gate = asyncio.Event()
    started = asyncio.Event()

    async def slow_play(path: str) -> bool:
        started.set()
        await gate.wait()
        return True

    with (
        patch("aiohttp.ClientSession", return_value=_mock_session()),
        patch("familiar_agent.tools.tts._play_local", new=slow_play),
        patch("familiar_agent.tools.tts._write_tmp_audio", return_value=str(tmp_path / "a.mp3")),
    ):
        (tmp_path / "a.mp3").write_bytes(b"x")
        result = await tool.say("hello there")

        assert result.startswith("Said: hello there")
        assert tool.is_speaking is True
        # Guard hooks fire at real playback start, from the worker.
        await asyncio.wait_for(started.wait(), 1.0)
        tool._voice_guard.on_tts_start.assert_called_once_with("hello there")
        tool._voice_guard.on_tts_end.assert_not_called()

        gate.set()
        assert await tool.wait_idle(timeout=1.0) is True

    tool._voice_guard.on_tts_end.assert_called_once_with("hello there", played=True)
    assert tool.is_speaking is False
    assert not (tmp_path / "a.mp3").exists()  # cleaned up after playback


@pytest.mark.asyncio
async def test_two_says_play_sequentially(monkeypatch, tmp_path):
    tool = _make_tts(monkeypatch)
    order: list[str] = []
    paths = iter([str(tmp_path / "1.mp3"), str(tmp_path / "2.mp3")])

    async def play(path: str) -> bool:
        order.append(f"start:{path}")
        await asyncio.sleep(0.01)
        order.append(f"end:{path}")
        return True

    with (
        patch("aiohttp.ClientSession", return_value=_mock_session()),
        patch("familiar_agent.tools.tts._play_local", new=play),
        patch("familiar_agent.tools.tts._write_tmp_audio", side_effect=lambda *a, **k: next(paths)),
    ):
        await tool.say("first")
        await tool.say("second")
        assert await tool.wait_idle(timeout=1.0) is True

    p1, p2 = str(tmp_path / "1.mp3"), str(tmp_path / "2.mp3")
    assert order == [f"start:{p1}", f"end:{p1}", f"start:{p2}", f"end:{p2}"]
    assert [c.args[0] for c in tool._voice_guard.on_tts_start.call_args_list] == [
        "first",
        "second",
    ]


@pytest.mark.asyncio
async def test_blocking_mode_awaits_playback(monkeypatch, tmp_path):
    tool = _make_tts(monkeypatch, blocking=True)
    finished = False

    async def play(path: str) -> bool:
        nonlocal finished
        await asyncio.sleep(0.01)
        finished = True
        return True

    with (
        patch("aiohttp.ClientSession", return_value=_mock_session()),
        patch("familiar_agent.tools.tts._play_local", new=play),
        patch("familiar_agent.tools.tts._write_tmp_audio", return_value=str(tmp_path / "b.mp3")),
    ):
        result = await tool.say("blocking")

    assert finished is True
    assert result == "Said: blocking... (via local)"
    tool._voice_guard.on_tts_end.assert_called_once_with("blocking", played=True)


@pytest.mark.asyncio
async def test_blocking_mode_reports_playback_failure(monkeypatch, tmp_path):
    tool = _make_tts(monkeypatch, blocking=True)
    with (
        patch("aiohttp.ClientSession", return_value=_mock_session()),
        patch("familiar_agent.tools.tts._play_local", new=AsyncMock(return_value=False)),
        patch("familiar_agent.tools.tts._write_tmp_audio", return_value=str(tmp_path / "c.mp3")),
    ):
        result = await tool.say("nope")
    assert "failed" in result.lower()
    tool._voice_guard.on_tts_end.assert_called_once_with("nope", played=False)


@pytest.mark.asyncio
async def test_tts_close_waits_for_idle_then_stops(monkeypatch, tmp_path):
    tool = _make_tts(monkeypatch)
    played: list[str] = []

    async def play(path: str) -> bool:
        await asyncio.sleep(0.01)
        played.append(path)
        return True

    with (
        patch("aiohttp.ClientSession", return_value=_mock_session()),
        patch("familiar_agent.tools.tts._play_local", new=play),
        patch("familiar_agent.tools.tts._write_tmp_audio", return_value=str(tmp_path / "d.mp3")),
    ):
        await tool.say("またね")
        await tool.close(timeout=1.0)

    assert played == [str(tmp_path / "d.mp3")]
    assert tool.is_speaking is False


@pytest.mark.asyncio
async def test_agent_close_waits_for_tts_idle():
    """agent.close() drains queued speech (short timeout) so the goodbye is not cut."""
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    tts = MagicMock()
    tts.close = AsyncMock()
    calls: list[str] = []

    async def fake_close(timeout: float = 0.0) -> None:
        calls.append(f"tts:{timeout}")

    tts.close = fake_close
    agent._tts = tts
    await EmbodiedAgent._drain_tts(agent)
    assert len(calls) == 1
    assert calls[0].startswith("tts:")


# ---------------------------------------------------------------------------
# Streaming synthesis: say() returns on the first chunk, audio plays as it lands
# ---------------------------------------------------------------------------


class _FakeChunks:
    """aiohttp-like ``content`` whose iter_chunked yields chunks gated by an event."""

    def __init__(self, chunks: list[bytes], gate: asyncio.Event | None = None):
        self.chunks = chunks
        self.gate = gate
        self.exhausted = False

    async def iter_chunked(self, _size: int):
        for i, chunk in enumerate(self.chunks):
            if i > 0 and self.gate is not None:
                await self.gate.wait()
            yield chunk
        self.exhausted = True

    iter_any = iter_chunked


def _stream_response(
    chunks: list[bytes],
    gate: asyncio.Event | None = None,
    *,
    status: int = 200,
    content_type: str = "audio/pcm",
):
    resp = MagicMock()
    resp.status = status
    resp.headers = {"Content-Type": content_type}
    resp.content = _FakeChunks(chunks, gate)
    resp.text = AsyncMock(return_value="nope")
    resp.read = AsyncMock(return_value=b"".join(chunks))
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=False)
    return resp


def _stream_session(responder):
    session = MagicMock()
    session.post = MagicMock(side_effect=responder)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    return session


class _FakeSink:
    """Stands in for the sounddevice-backed PcmSink."""

    instances: list["_FakeSink"] = []

    def __init__(self, *, fail: bool = False) -> None:
        self.writes: list[bytes] = []
        self.closed = False
        self.error: Exception | None = RuntimeError("no device") if fail else None
        self.bytes_played = 0
        _FakeSink.instances.append(self)

    def write(self, chunk: bytes) -> None:
        if self.error is None:
            self.writes.append(chunk)
            self.bytes_played += len(chunk)

    async def close(self) -> bool:
        self.closed = True
        return self.error is None


@pytest.fixture
def fake_sink(monkeypatch):
    _FakeSink.instances = []
    monkeypatch.setattr("familiar_agent.tools.tts.open_pcm_sink", lambda **_kw: _FakeSink())
    return _FakeSink


@pytest.mark.asyncio
async def test_say_returns_after_first_chunk_and_streams_in_order(monkeypatch, fake_sink):
    tool = _make_tts(monkeypatch)
    gate = asyncio.Event()
    resp = _stream_response([b"\x01\x02", b"\x03\x04", b"\x05\x06"], gate)
    session = _stream_session(lambda *a, **k: resp)

    with patch("aiohttp.ClientSession", return_value=session):
        result = await asyncio.wait_for(tool.say("stream me"), 1.0)

        assert result.startswith("Said: stream me")
        assert resp.content.exhausted is False  # returned before the body finished
        assert "/stream?" in session.post.call_args.args[0]
        assert tool.is_speaking is True

        gate.set()
        assert await tool.wait_idle(timeout=1.0) is True

    assert resp.content.exhausted is True
    (sink,) = fake_sink.instances
    assert b"".join(sink.writes) == b"\x01\x02\x03\x04\x05\x06"
    assert sink.closed is True
    tool._voice_guard.on_tts_start.assert_called_once_with("stream me")
    tool._voice_guard.on_tts_end.assert_called_once_with("stream me", played=True)
    resp.__aexit__.assert_awaited()  # HTTP response released after the stream drained
    session.__aexit__.assert_awaited()


@pytest.mark.asyncio
async def test_say_camera_path_buffers_full_stream_to_wav(monkeypatch, fake_sink, tmp_path):
    tool = _make_tts(monkeypatch)
    tool.output = "remote"
    resp = _stream_response([b"\x01\x02\x03", b"\x04"])
    session = _stream_session(lambda *a, **k: resp)
    seen: list[bytes] = []

    def fake_go2rtc(path: str, url: str, stream: str) -> tuple[bool, str]:
        seen.append(Path(path).read_bytes()[44:])
        return True, "ok"

    with (
        patch("aiohttp.ClientSession", return_value=session),
        patch("familiar_agent.tools.tts._play_via_go2rtc", side_effect=fake_go2rtc),
        patch("familiar_agent.tools.tts._play_local", new=AsyncMock(return_value=False)),
    ):
        result = await tool.say("to the camera")
        assert await tool.wait_idle(timeout=1.0) is True

    assert result == "Said: to the camera... (via camera)"
    assert seen == [b"\x01\x02\x03\x04"]
    assert fake_sink.instances == []  # no local sink on the remote-only path
    tool._voice_guard.on_tts_end.assert_called_once_with("to the camera", played=True)


@pytest.mark.asyncio
async def test_say_both_streams_locally_then_plays_camera_from_buffer(monkeypatch, fake_sink):
    tool = _make_tts(monkeypatch)
    tool.output = "both"
    resp = _stream_response([b"\xaa\xbb", b"\xcc\xdd"])
    session = _stream_session(lambda *a, **k: resp)
    order: list[str] = []

    def fake_go2rtc(path: str, url: str, stream: str) -> tuple[bool, str]:
        order.append("camera:" + Path(path).read_bytes()[44:].hex())
        return True, "ok"

    with (
        patch("aiohttp.ClientSession", return_value=session),
        patch("familiar_agent.tools.tts._play_via_go2rtc", side_effect=fake_go2rtc),
    ):
        await tool.say("both")
        assert await tool.wait_idle(timeout=1.0) is True

    (sink,) = fake_sink.instances
    assert sink.closed is True  # local finished before the camera started
    assert order == ["camera:aabbccdd"]


@pytest.mark.asyncio
async def test_say_falls_back_to_file_playback_when_sink_unavailable(monkeypatch, tmp_path):
    tool = _make_tts(monkeypatch)

    def no_sink(**_kw):
        raise ImportError("No module named 'sounddevice'")

    monkeypatch.setattr("familiar_agent.tools.tts.open_pcm_sink", no_sink)
    resp = _stream_response([b"\x01\x02", b"\x03\x04"])
    session = _stream_session(lambda *a, **k: resp)
    played: list[bytes] = []

    async def fake_play_local(path: str) -> bool:
        played.append(Path(path).read_bytes()[44:])
        return True

    with (
        patch("aiohttp.ClientSession", return_value=session),
        patch("familiar_agent.tools.tts._play_local", new=fake_play_local),
    ):
        await tool.say("fallback")
        assert await tool.wait_idle(timeout=1.0) is True

    assert played == [b"\x01\x02\x03\x04"]
    tool._voice_guard.on_tts_end.assert_called_once_with("fallback", played=True)


@pytest.mark.asyncio
async def test_say_sink_error_midway_plays_the_rest_from_file(monkeypatch):
    tool = _make_tts(monkeypatch)
    _FakeSink.instances = []

    class _DiesAfterFirst(_FakeSink):
        def write(self, chunk: bytes) -> None:
            super().write(chunk)
            self.error = RuntimeError("device vanished")

    monkeypatch.setattr("familiar_agent.tools.tts.open_pcm_sink", lambda **_kw: _DiesAfterFirst())
    resp = _stream_response([b"\x01\x02", b"\x03\x04", b"\x05\x06"])
    session = _stream_session(lambda *a, **k: resp)
    played: list[bytes] = []

    async def fake_play_local(path: str) -> bool:
        played.append(Path(path).read_bytes()[44:])
        return True

    with (
        patch("aiohttp.ClientSession", return_value=session),
        patch("familiar_agent.tools.tts._play_local", new=fake_play_local),
    ):
        await tool.say("partial")
        assert await tool.wait_idle(timeout=1.0) is True

    assert played == [b"\x03\x04\x05\x06"]  # only the unplayed remainder


@pytest.mark.asyncio
async def test_say_blocking_mode_awaits_whole_stream(monkeypatch, fake_sink):
    tool = _make_tts(monkeypatch, blocking=True)
    resp = _stream_response([b"\x01\x02", b"\x03\x04"])
    session = _stream_session(lambda *a, **k: resp)

    with patch("aiohttp.ClientSession", return_value=session):
        result = await tool.say("blocking stream")

    assert result == "Said: blocking stream... (via local)"
    assert resp.content.exhausted is True
    (sink,) = fake_sink.instances
    assert sink.closed is True
    assert tool.is_speaking is False


@pytest.mark.asyncio
async def test_say_retries_without_stream_endpoint_on_404(monkeypatch, fake_sink):
    tool = _make_tts(monkeypatch)
    urls: list[str] = []

    def responder(url: str, **_kw):
        urls.append(url)
        if "/stream" in url:
            return _stream_response([], status=404)
        return _stream_response([b"\x01\x02"])

    session = _stream_session(responder)
    with patch("aiohttp.ClientSession", return_value=session):
        result = await tool.say("old account")
        assert await tool.wait_idle(timeout=1.0) is True

    assert result.startswith("Said: old account")
    assert len(urls) == 2 and "/stream" in urls[0] and "/stream" not in urls[1]
    (sink,) = fake_sink.instances
    assert sink.writes == [b"\x01\x02"]


@pytest.mark.asyncio
async def test_say_stream_error_status_returns_error_string(monkeypatch, fake_sink):
    tool = _make_tts(monkeypatch)
    session = _stream_session(lambda *a, **k: _stream_response([], status=429))
    with patch("aiohttp.ClientSession", return_value=session):
        result = await tool.say("limited")
    assert "429" in result
    assert tool.is_speaking is False
    assert fake_sink.instances == []


@pytest.mark.asyncio
async def test_say_mp3_stream_is_buffered_to_file(monkeypatch, fake_sink, tmp_path):
    tool = _make_tts(monkeypatch)
    resp = _stream_response([b"ID3abc", b"def"], content_type="audio/mpeg")
    session = _stream_session(lambda *a, **k: resp)
    played: list[bytes] = []

    async def fake_play_local(path: str) -> bool:
        played.append(Path(path).read_bytes())
        return True

    with (
        patch("aiohttp.ClientSession", return_value=session),
        patch("familiar_agent.tools.tts._play_local", new=fake_play_local),
    ):
        await tool.say("mp3")
        assert await tool.wait_idle(timeout=1.0) is True

    assert played == [b"ID3abcdef"]
    assert fake_sink.instances == []


# ---------------------------------------------------------------------------
# PcmSink: thread-backed sounddevice writer with remainder carry
# ---------------------------------------------------------------------------


class _FakeRawStream:
    def __init__(self, *, fail_after: int | None = None) -> None:
        self.writes: list[bytes] = []
        self.started = self.stopped = self.closed = False
        self.fail_after = fail_after

    def start(self) -> None:
        self.started = True

    def write(self, data: bytes) -> None:
        if self.fail_after is not None and len(self.writes) >= self.fail_after:
            raise RuntimeError("PortAudio error")
        self.writes.append(bytes(data))

    def stop(self) -> None:
        self.stopped = True

    def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_pcm_sink_carries_odd_byte_remainder_across_chunks():
    from familiar_agent.tts_playback import PcmSink

    stream = _FakeRawStream()
    sink = PcmSink(sample_rate=16000, stream_factory=lambda: stream)
    sink.write(b"\x01\x02\x03")  # 1.5 frames → write 1 frame, carry 1 byte
    sink.write(b"\x04\x05")  # carry + 2 → 1.5 frames again
    sink.write(b"\x06")  # completes the pending frame
    assert await sink.close() is True

    assert b"".join(stream.writes) == b"\x01\x02\x03\x04\x05\x06"
    assert all(len(w) % 2 == 0 for w in stream.writes)
    assert sink.bytes_played == 6
    assert stream.started and stream.stopped and stream.closed


@pytest.mark.asyncio
async def test_pcm_sink_reports_write_errors_and_bytes_played():
    from familiar_agent.tts_playback import PcmSink

    stream = _FakeRawStream(fail_after=1)
    sink = PcmSink(sample_rate=16000, stream_factory=lambda: stream)
    sink.write(b"\x01\x02")
    sink.write(b"\x03\x04")
    assert await sink.close() is False
    assert sink.error is not None
    assert sink.bytes_played == 2
    assert stream.closed


def test_pcm_sink_raises_when_sounddevice_missing(monkeypatch):
    import builtins

    from familiar_agent.tts_playback import PcmSink

    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "sounddevice":
            raise ImportError("no sounddevice")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ImportError):
        PcmSink(sample_rate=16000)


@pytest.mark.asyncio
async def test_enqueue_stream_keeps_fifo_with_file_items():
    from familiar_agent.tts_playback import AudioChunkRelay

    log: list[str] = []

    async def gen():
        yield b"a"
        yield b"b"

    async def play_file(path: str) -> list[str]:
        log.append(f"file:{path}")
        return ["local"]

    async def play_stream(chunks) -> list[str]:
        got = [c async for c in chunks]
        log.append("stream:" + b"".join(got).decode())
        return ["local"]

    queue = PlaybackQueue(play=play_file)
    relay = AudioChunkRelay(gen())
    relay.start()
    f1 = queue.enqueue("one.wav")
    f2 = queue.enqueue_stream(relay, play=play_stream)
    f3 = queue.enqueue("three.wav")
    assert await asyncio.gather(f1, f2, f3) == [["local"], ["local"], ["local"]]
    assert log == ["file:one.wav", "stream:ab", "file:three.wav"]


@pytest.mark.asyncio
async def test_audio_chunk_relay_prepends_head_and_closes_source():
    from familiar_agent.tts_playback import AudioChunkRelay

    closed = asyncio.Event()

    async def gen():
        yield b"2"
        yield b"3"

    async def close() -> None:
        closed.set()

    relay = AudioChunkRelay(gen(), head=b"1", close=close)
    relay.start()
    assert [c async for c in relay] == [b"1", b"2", b"3"]
    await asyncio.wait_for(closed.wait(), 1.0)
    assert relay.error is None
