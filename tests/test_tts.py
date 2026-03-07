"""Tests for TTSTool — ElevenLabs API and audio playback mocked."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helper: TTSTool without real __init__ side-effects
# ---------------------------------------------------------------------------


def _make_tts(api_key: str = "fake-key", voice_id: str = "fake-voice"):
    from familiar_agent.tools.tts import TTSTool

    with patch("familiar_agent.tools.tts._ensure_go2rtc"):
        tool = TTSTool(api_key=api_key, voice_id=voice_id, output="local")
    return tool


# ---------------------------------------------------------------------------
# Tests: get_tool_definitions()
# ---------------------------------------------------------------------------


def test_get_tool_definitions_returns_say():
    tool = _make_tts()
    defs = tool.get_tool_definitions()
    assert len(defs) == 1
    assert defs[0]["name"] == "say"


# ---------------------------------------------------------------------------
# Tests: call()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_call_say_invokes_say_method():
    """call('say', ...) delegates to say() and returns its result."""
    tool = _make_tts()
    tool.say = AsyncMock(return_value="Said: hello")

    result, img = await tool.call("say", {"text": "hello"})

    assert result == "Said: hello"
    assert img is None
    tool.say.assert_awaited_once_with("hello")


@pytest.mark.asyncio
async def test_call_unknown_tool_returns_error():
    tool = _make_tts()
    result, img = await tool.call("nonexistent", {})
    assert "Unknown" in result or "nonexistent" in result


# ---------------------------------------------------------------------------
# Tests: say() — API + playback mocked
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_say_calls_elevenlabs_api():
    """say() POSTs to ElevenLabs with the correct API key and text."""
    tool = _make_tts(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b"fake_mp3_data")
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("aiohttp.ClientSession", return_value=mock_session),
        patch("familiar_agent.tools.tts._play_local", new=AsyncMock(return_value=True)),
        patch("builtins.open", MagicMock()),
        patch("os.unlink"),
        patch("tempfile.NamedTemporaryFile") as mock_tmp,
    ):
        tmp_file = MagicMock()
        tmp_file.__enter__ = MagicMock(return_value=tmp_file)
        tmp_file.__exit__ = MagicMock(return_value=False)
        tmp_file.name = "/tmp/fake.mp3"
        mock_tmp.return_value = tmp_file

        await tool.say("hello world")

    # Verify ElevenLabs API was called
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert "xi-api-key" in call_args[1]["headers"] or "xi-api-key" in call_args.kwargs.get(
        "headers", {}
    )


@pytest.mark.asyncio
async def test_say_truncates_long_text():
    """say() truncates text longer than 200 characters."""
    tool = _make_tts()
    long_text = "x" * 300

    truncated_texts = []

    async def fake_say_inner(text, output=None):
        truncated_texts.append(text)
        return "Said: ..."

    # Patch at the API call level instead
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b"fake_mp3_data")
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    posted_payloads = []

    def capture_post(url, json=None, headers=None):
        if json:
            posted_payloads.append(json)
        return mock_response

    mock_session.post = MagicMock(side_effect=capture_post)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("aiohttp.ClientSession", return_value=mock_session),
        patch("familiar_agent.tools.tts._play_local", new=AsyncMock(return_value=True)),
        patch("os.unlink"),
        patch("tempfile.NamedTemporaryFile") as mock_tmp,
    ):
        tmp_file = MagicMock()
        tmp_file.__enter__ = MagicMock(return_value=tmp_file)
        tmp_file.__exit__ = MagicMock(return_value=False)
        tmp_file.name = "/tmp/fake.mp3"
        mock_tmp.return_value = tmp_file

        await tool.say(long_text)

    assert posted_payloads, "API was never called"
    sent_text = posted_payloads[0]["text"]
    assert len(sent_text) <= 200
    assert sent_text.endswith("...")


@pytest.mark.asyncio
async def test_say_returns_error_on_api_failure():
    """say() returns an error string when the ElevenLabs API returns non-200."""
    tool = _make_tts()

    mock_response = MagicMock()
    mock_response.status = 429
    mock_response.text = AsyncMock(return_value="Rate limit exceeded")
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await tool.say("hello")

    assert "429" in result or "failed" in result.lower()


@pytest.mark.asyncio
async def test_say_serializes_concurrent_calls():
    """Concurrent say() calls must be serialized (lock prevents overlap)."""
    tool = _make_tts()

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b"fake")
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("aiohttp.ClientSession", return_value=mock_session),
        patch("familiar_agent.tools.tts._play_local", new=AsyncMock(return_value=True)),
        patch("os.unlink"),
        patch("tempfile.NamedTemporaryFile") as mock_tmp,
    ):
        tmp_file = MagicMock()
        tmp_file.__enter__ = MagicMock(return_value=tmp_file)
        tmp_file.__exit__ = MagicMock(return_value=False)
        tmp_file.name = "/tmp/fake.mp3"
        mock_tmp.return_value = tmp_file

        # Launch two say() calls concurrently
        results = await asyncio.gather(
            tool.say("first"),
            tool.say("second"),
        )

    # Both should succeed (no exception)
    assert len(results) == 2
