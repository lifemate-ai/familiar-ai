"""Tests for the STT (Speech-to-Text) tool and STTConfig."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from familiar_agent.config import STTConfig
from familiar_agent.tools.stt import STTTool


# ── STTConfig ─────────────────────────────────────────────────────────────────


class TestSTTConfig:
    """Test STTConfig dataclass defaults and overrides."""

    def test_defaults_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key-abc")
        monkeypatch.setenv("STT_LANGUAGE", "en")
        cfg = STTConfig()
        assert cfg.elevenlabs_api_key == "test-key-abc"
        assert cfg.language == "en"

    def test_defaults_when_env_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
        monkeypatch.delenv("STT_LANGUAGE", raising=False)
        cfg = STTConfig()
        assert cfg.elevenlabs_api_key == ""
        assert cfg.language == "ja"

    def test_custom_values_override_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ELEVENLABS_API_KEY", "env-key")
        cfg = STTConfig(elevenlabs_api_key="custom-key", language="ko")
        assert cfg.elevenlabs_api_key == "custom-key"
        assert cfg.language == "ko"


# ── STTTool._transcribe_elevenlabs ────────────────────────────────────────────


class TestTranscribeElevenlabs:
    """Test the ElevenLabs transcription API call."""

    @pytest.mark.asyncio
    async def test_success_returns_text(self) -> None:
        tool = STTTool(api_key="fake-key", language="ja")

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"text": "hello world"})

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_session_ctx)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("familiar_agent.tools.stt.aiohttp.ClientSession", return_value=mock_client_ctx):
            result = await tool._transcribe_elevenlabs(b"fake-audio-bytes")

        assert result == "hello world"

    @pytest.mark.asyncio
    async def test_api_error_returns_empty(self) -> None:
        tool = STTTool(api_key="fake-key", language="ja")

        mock_resp = AsyncMock()
        mock_resp.status = 401
        mock_resp.text = AsyncMock(return_value="Unauthorized")

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_session_ctx)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("familiar_agent.tools.stt.aiohttp.ClientSession", return_value=mock_client_ctx):
            result = await tool._transcribe_elevenlabs(b"fake-audio-bytes")

        assert result == ""

    @pytest.mark.asyncio
    async def test_empty_input_returns_empty(self) -> None:
        tool = STTTool(api_key="fake-key")
        result = await tool._transcribe_elevenlabs(b"")
        assert result == ""

    @pytest.mark.asyncio
    async def test_network_exception_returns_empty(self) -> None:
        tool = STTTool(api_key="fake-key")

        with patch(
            "familiar_agent.tools.stt.aiohttp.ClientSession",
            side_effect=Exception("connection refused"),
        ):
            result = await tool._transcribe_elevenlabs(b"fake-audio-bytes")

        assert result == ""

    @pytest.mark.asyncio
    async def test_missing_text_key_returns_empty(self) -> None:
        """API returns 200 but JSON has no 'text' field."""
        tool = STTTool(api_key="fake-key", language="ja")

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"status": "ok"})

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_session_ctx)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("familiar_agent.tools.stt.aiohttp.ClientSession", return_value=mock_client_ctx):
            result = await tool._transcribe_elevenlabs(b"fake-audio-bytes")

        assert result == ""

    @pytest.mark.asyncio
    async def test_language_field_sent_when_set(self) -> None:
        """When language is set, language_code field is added to form data."""
        tool = STTTool(api_key="fake-key", language="en")

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"text": "hi"})

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_session_ctx)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_form_cls = MagicMock()
        mock_form_instance = MagicMock()
        mock_form_cls.return_value = mock_form_instance

        with (
            patch("familiar_agent.tools.stt.aiohttp.ClientSession", return_value=mock_client_ctx),
            patch("familiar_agent.tools.stt.aiohttp.FormData", mock_form_cls),
        ):
            await tool._transcribe_elevenlabs(b"audio")

        # Check language_code was added
        calls = mock_form_instance.add_field.call_args_list
        lang_calls = [c for c in calls if c[0][0] == "language_code"]
        assert len(lang_calls) == 1
        assert lang_calls[0][0][1] == "en"

    @pytest.mark.asyncio
    async def test_no_language_field_when_empty(self) -> None:
        """When language is empty string, language_code field is NOT added."""
        tool = STTTool(api_key="fake-key", language="")

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"text": "hi"})

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_session_ctx)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_form_cls = MagicMock()
        mock_form_instance = MagicMock()
        mock_form_cls.return_value = mock_form_instance

        with (
            patch("familiar_agent.tools.stt.aiohttp.ClientSession", return_value=mock_client_ctx),
            patch("familiar_agent.tools.stt.aiohttp.FormData", mock_form_cls),
        ):
            await tool._transcribe_elevenlabs(b"audio")

        calls = mock_form_instance.add_field.call_args_list
        lang_calls = [c for c in calls if c[0][0] == "language_code"]
        assert len(lang_calls) == 0


# ── STTTool.record_and_transcribe ─────────────────────────────────────────────


class TestRecordAndTranscribe:
    """Test the main entry point orchestrating record + transcribe."""

    @pytest.mark.asyncio
    async def test_happy_path_mic_to_transcribe(self) -> None:
        """Mic returns audio bytes -> transcribe is called -> returns text."""
        tool = STTTool(api_key="fake-key")
        stop = asyncio.Event()

        with (
            patch.object(tool, "_record_mic", return_value=b"wav-data") as mock_mic,
            patch.object(
                tool, "_transcribe_elevenlabs", new_callable=AsyncMock, return_value="hello"
            ) as mock_tx,
        ):
            result = await tool.record_and_transcribe(stop)

        assert result == "hello"
        mock_mic.assert_called_once_with(stop)
        mock_tx.assert_awaited_once_with(b"wav-data")

    @pytest.mark.asyncio
    async def test_mic_none_with_rtsp_falls_back(self) -> None:
        """Mic returns None + rtsp_url set -> RTSP fallback is attempted."""
        tool = STTTool(api_key="fake-key", rtsp_url="rtsp://cam/stream")
        stop = asyncio.Event()

        with (
            patch.object(tool, "_record_mic", return_value=None),
            patch.object(
                tool, "_record_rtsp", new_callable=AsyncMock, return_value=b"rtsp-wav"
            ) as mock_rtsp,
            patch.object(
                tool, "_transcribe_elevenlabs", new_callable=AsyncMock, return_value="from camera"
            ) as mock_tx,
        ):
            result = await tool.record_and_transcribe(stop)

        assert result == "from camera"
        mock_rtsp.assert_awaited_once_with(stop)
        mock_tx.assert_awaited_once_with(b"rtsp-wav")

    @pytest.mark.asyncio
    async def test_mic_none_no_rtsp_returns_empty(self) -> None:
        """Mic returns None + no rtsp_url -> returns empty string."""
        tool = STTTool(api_key="fake-key")  # no rtsp_url
        stop = asyncio.Event()

        with patch.object(tool, "_record_mic", return_value=None):
            result = await tool.record_and_transcribe(stop)

        assert result == ""

    @pytest.mark.asyncio
    async def test_mic_returns_empty_bytes_returns_empty(self) -> None:
        """Mic returns b'' (empty) -> treated as no audio, returns empty."""
        tool = STTTool(api_key="fake-key")
        stop = asyncio.Event()

        with patch.object(tool, "_record_mic", return_value=b""):
            result = await tool.record_and_transcribe(stop)

        assert result == ""

    @pytest.mark.asyncio
    async def test_rtsp_also_empty_returns_empty(self) -> None:
        """Mic None + RTSP returns empty bytes -> returns empty."""
        tool = STTTool(api_key="fake-key", rtsp_url="rtsp://cam/stream")
        stop = asyncio.Event()

        with (
            patch.object(tool, "_record_mic", return_value=None),
            patch.object(tool, "_record_rtsp", new_callable=AsyncMock, return_value=b""),
        ):
            result = await tool.record_and_transcribe(stop)

        assert result == ""

    @pytest.mark.asyncio
    async def test_transcribe_returns_empty_string(self) -> None:
        """Audio captured but transcription returns empty -> returns empty."""
        tool = STTTool(api_key="fake-key")
        stop = asyncio.Event()

        with (
            patch.object(tool, "_record_mic", return_value=b"wav-data"),
            patch.object(tool, "_transcribe_elevenlabs", new_callable=AsyncMock, return_value=""),
        ):
            result = await tool.record_and_transcribe(stop)

        assert result == ""


# ── STTTool._record_mic ──────────────────────────────────────────────────────


class TestRecordMic:
    """Test microphone recording with sounddevice mocks."""

    def test_portaudio_error_returns_none(self) -> None:
        """When PortAudioError is raised, returns None gracefully."""
        stop = asyncio.Event()
        stop.set()  # stop immediately

        mock_sd = MagicMock()
        port_error = type("PortAudioError", (Exception,), {})
        mock_sd.PortAudioError = port_error
        mock_sd.InputStream = MagicMock(
            side_effect=port_error("no mic"),
        )

        with (
            patch.dict("sys.modules", {"sounddevice": mock_sd}),
            patch.dict("sys.modules", {"numpy": MagicMock()}),
            patch.dict("sys.modules", {"soundfile": MagicMock()}),
        ):
            # Need to reimport to pick up mocked modules
            import importlib

            import familiar_agent.tools.stt as stt_mod

            importlib.reload(stt_mod)
            reloaded_tool = stt_mod.STTTool(api_key="fake-key")
            result = reloaded_tool._record_mic(stop)

        assert result is None

    def test_import_error_returns_none(self) -> None:
        """When sounddevice is not installed, returns None."""
        stop = asyncio.Event()
        stop.set()

        # The method imports sounddevice inside the function body,
        # so we mock at the import level
        with patch.dict("sys.modules", {"sounddevice": None}):
            import importlib

            import familiar_agent.tools.stt as stt_mod

            importlib.reload(stt_mod)
            reloaded_tool = stt_mod.STTTool(api_key="fake-key")
            result = reloaded_tool._record_mic(stop)

        assert result is None

    def test_no_chunks_returns_none(self) -> None:
        """When stop_event is already set, no chunks recorded -> returns None."""
        stop = asyncio.Event()
        stop.set()  # already stopped

        mock_sd = MagicMock()
        mock_sd.PortAudioError = type("PortAudioError", (Exception,), {})

        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_sd.InputStream = MagicMock(return_value=mock_stream)

        mock_sf = MagicMock()

        # Use real numpy (already available) but mock sounddevice and soundfile
        # to avoid the PortAudio dependency. Don't patch numpy in sys.modules
        # because it causes reimport errors with C extensions.
        with (
            patch.dict("sys.modules", {"sounddevice": mock_sd, "soundfile": mock_sf}),
        ):
            import importlib

            import familiar_agent.tools.stt as stt_mod

            importlib.reload(stt_mod)
            reloaded_tool = stt_mod.STTTool(api_key="fake-key")
            result = reloaded_tool._record_mic(stop)

        assert result is None

    def test_successful_recording_returns_wav_bytes(self) -> None:
        """When mic works and chunks are recorded, returns WAV bytes."""
        stop = asyncio.Event()

        # Create a fake audio chunk (plain list, np.concatenate is mocked)
        fake_chunk = [[0.0]] * 1024

        mock_sd = MagicMock()
        mock_sd.PortAudioError = type("PortAudioError", (Exception,), {})

        call_count = 0

        def mock_read(n: int):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                stop.set()  # stop after a few reads
            return fake_chunk, None

        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_stream.read = mock_read
        mock_sd.InputStream = MagicMock(return_value=mock_stream)

        mock_np = MagicMock()
        mock_np.concatenate = MagicMock(return_value="fake-audio-array")

        mock_sf = MagicMock()

        # Mock sf.write to produce fake WAV bytes in the BytesIO buffer
        def fake_sf_write(buf, audio, sr, format, subtype):
            buf.write(b"RIFF-fake-wav-data")

        mock_sf.write = fake_sf_write

        with patch.dict(
            "sys.modules",
            {"sounddevice": mock_sd, "soundfile": mock_sf, "numpy": mock_np},
        ):
            import importlib

            import familiar_agent.tools.stt as stt_mod

            importlib.reload(stt_mod)
            reloaded_tool = stt_mod.STTTool(api_key="fake-key")
            result = reloaded_tool._record_mic(stop)

        assert result is not None
        assert len(result) > 0
        assert b"RIFF-fake-wav-data" in result


# ── STTTool._record_rtsp ─────────────────────────────────────────────────────


class TestRecordRtsp:
    """Test RTSP recording via ffmpeg."""

    @pytest.mark.asyncio
    async def test_rtsp_recording_returns_bytes(self) -> None:
        """Happy path: ffmpeg writes a file, we read it back."""
        tool = STTTool(api_key="fake-key", rtsp_url="rtsp://cam/stream")
        stop = asyncio.Event()

        mock_proc = AsyncMock()
        mock_proc.terminate = MagicMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))
        mock_proc.kill = MagicMock()

        async def set_stop_soon():
            await asyncio.sleep(0.05)
            stop.set()

        with (
            patch("asyncio.create_subprocess_exec", new_callable=AsyncMock, return_value=mock_proc),
            patch("pathlib.Path.read_bytes", return_value=b"rtsp-wav-data"),
            patch("pathlib.Path.unlink"),
        ):
            asyncio.get_event_loop().create_task(set_stop_soon())
            result = await tool._record_rtsp(stop)

        assert result == b"rtsp-wav-data"
        mock_proc.terminate.assert_called_once()

    @pytest.mark.asyncio
    async def test_rtsp_no_output_file_returns_empty(self) -> None:
        """ffmpeg produces no output file -> returns empty bytes."""
        tool = STTTool(api_key="fake-key", rtsp_url="rtsp://cam/stream")
        stop = asyncio.Event()
        stop.set()  # stop immediately

        mock_proc = AsyncMock()
        mock_proc.terminate = MagicMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))
        mock_proc.kill = MagicMock()

        with (
            patch("asyncio.create_subprocess_exec", new_callable=AsyncMock, return_value=mock_proc),
            patch("pathlib.Path.read_bytes", side_effect=FileNotFoundError("no file")),
            patch("pathlib.Path.unlink"),
        ):
            result = await tool._record_rtsp(stop)

        assert result == b""

    @pytest.mark.asyncio
    async def test_rtsp_communicate_timeout_kills_process(self) -> None:
        """If proc.communicate times out, process is killed."""
        tool = STTTool(api_key="fake-key", rtsp_url="rtsp://cam/stream")
        stop = asyncio.Event()
        stop.set()  # stop immediately

        mock_proc = AsyncMock()
        mock_proc.terminate = MagicMock()
        mock_proc.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
        mock_proc.kill = MagicMock()

        with (
            patch("asyncio.create_subprocess_exec", new_callable=AsyncMock, return_value=mock_proc),
            patch("pathlib.Path.read_bytes", return_value=b"data"),
            patch("pathlib.Path.unlink"),
        ):
            result = await tool._record_rtsp(stop)

        mock_proc.kill.assert_called_once()
        assert result == b"data"


# ── STTTool constructor ──────────────────────────────────────────────────────


class TestSTTToolInit:
    """Test STTTool initialization."""

    def test_default_values(self) -> None:
        tool = STTTool(api_key="key1")
        assert tool._api_key == "key1"
        assert tool._language == "ja"
        assert tool._rtsp_url == ""

    def test_custom_values(self) -> None:
        tool = STTTool(api_key="key2", language="en", rtsp_url="rtsp://host/stream")
        assert tool._api_key == "key2"
        assert tool._language == "en"
        assert tool._rtsp_url == "rtsp://host/stream"
