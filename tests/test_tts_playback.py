"""Tests for the TTS playback queue — say() must not stall the turn.

Synthesis (HTTP) is awaited inline; playback is handed to a single worker that
plays files one after another. The voice guard's start/end hooks fire at real
playback boundaries, from the worker, not at enqueue time.
"""

from __future__ import annotations

import asyncio
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
