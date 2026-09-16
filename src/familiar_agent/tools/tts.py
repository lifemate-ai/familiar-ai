"""TTS tool - voice of the embodied agent (ElevenLabs + go2rtc camera speaker)."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import urllib.request
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ..tts_playback import AudioChunkRelay, PcmSink, PlaybackQueue
from ..voice_guard import VoiceLoopGuard, get_shared_voice_guard

logger = logging.getLogger(__name__)


def _write_pcm_as_wav(
    pcm_bytes: bytes, sample_rate: int = 16000, tmp_dir: str | None = None
) -> str:
    """Write raw 16-bit mono PCM bytes to a temp WAV file and return the path.

    Builds the 44-byte WAV/RIFF header without any external dependency.
    """
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = len(pcm_bytes)
    file_size = 36 + data_size  # RIFF chunk size = file_size - 8

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        file_size,
        b"WAVE",
        b"fmt ",
        16,  # fmt chunk size
        1,  # PCM format
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size,
    )

    suffix = ".wav"
    kwargs: dict = {"suffix": suffix, "delete": False}
    if tmp_dir:
        kwargs["dir"] = tmp_dir
    with tempfile.NamedTemporaryFile(**kwargs) as f:
        f.write(header)
        f.write(pcm_bytes)
        return f.name


def _write_tmp_audio(data: bytes, suffix: str = ".mp3") -> str:
    """Write raw audio bytes to a temp file and return the path."""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(data)
        return f.name


_GO2RTC_CACHE = Path.home() / ".cache" / "embodied-claude" / "go2rtc"
# On Windows the binary is go2rtc.exe; on other platforms there is no extension.
_GO2RTC_BIN = _GO2RTC_CACHE / ("go2rtc.exe" if sys.platform == "win32" else "go2rtc")
_GO2RTC_CONFIG = _GO2RTC_CACHE / "go2rtc.yaml"


def _ensure_go2rtc(api_url: str) -> None:
    """Start go2rtc if it's not already running."""
    try:
        urllib.request.urlopen(f"{api_url}/api", timeout=2)
        return  # already running
    except Exception:
        pass

    if not _GO2RTC_BIN.exists():
        logger.warning("go2rtc binary not found at %s", _GO2RTC_BIN)
        return
    if not _GO2RTC_CONFIG.exists():
        logger.warning("go2rtc config not found at %s", _GO2RTC_CONFIG)
        return

    logger.info("Starting go2rtc...")
    subprocess.Popen(
        [str(_GO2RTC_BIN), "-config", str(_GO2RTC_CONFIG)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    import time

    for _ in range(10):
        time.sleep(0.5)
        try:
            urllib.request.urlopen(f"{api_url}/api", timeout=1)
            logger.info("go2rtc started")
            return
        except Exception:
            continue
    logger.warning("go2rtc did not start in time")


class TTSTool:
    """Text-to-speech using ElevenLabs, played via go2rtc camera speaker and/or local speaker."""

    def __init__(
        self,
        api_key: str,
        voice_id: str,
        go2rtc_url: str = "http://localhost:1984",
        go2rtc_stream: str = "tapo_cam",
        output: str = "local",
        voice_guard: VoiceLoopGuard | None = None,
    ) -> None:
        self.api_key = api_key
        self.voice_id = voice_id
        self.go2rtc_url = go2rtc_url
        self.go2rtc_stream = go2rtc_stream
        # "local" = PC speaker only, "remote" = camera speaker only, "both" = both simultaneously
        self.output = output
        self._voice_guard = voice_guard or get_shared_voice_guard()
        # Serialize synthesis so consecutive say() calls enqueue in call order.
        self._lock = asyncio.Lock()
        # Playback runs on a single worker, one file at a time, off the turn.
        self._playback = PlaybackQueue()
        # Ensure go2rtc is running at startup
        _ensure_go2rtc(self.go2rtc_url)

    # ------------------------------------------------------------ playback

    def _queue(self) -> PlaybackQueue:
        """Lazily create the playback queue (instances built via __new__ lack it)."""
        queue = getattr(self, "_playback", None)
        if queue is None:
            queue = PlaybackQueue()
            self._playback = queue
        return queue

    @property
    def is_speaking(self) -> bool:
        """True while an utterance is playing or queued to play."""
        queue = getattr(self, "_playback", None)
        return bool(queue is not None and queue.is_speaking)

    async def wait_idle(self, timeout: float | None = None) -> bool:
        """Wait until queued speech has finished playing. False on timeout."""
        queue = getattr(self, "_playback", None)
        if queue is None:
            return True
        return await queue.wait_idle(timeout=timeout)

    async def close(self, timeout: float = 3.0) -> None:
        """Let in-flight speech finish (bounded), then stop the worker."""
        queue = getattr(self, "_playback", None)
        if queue is None:
            return
        await queue.wait_idle(timeout=timeout)
        await queue.stop()

    def _guard(self) -> VoiceLoopGuard:
        voice_guard = getattr(self, "_voice_guard", None)
        if voice_guard is None:
            voice_guard = get_shared_voice_guard()
            self._voice_guard = voice_guard
        return voice_guard

    async def _play_file(self, tmp_path: str, text: str, output: str) -> list[str]:
        """Play one synthesized file; runs on the queue worker.

        Owns the voice-guard boundaries so STT echo suppression tracks real
        playback rather than enqueue time.
        """
        voice_guard = self._guard()
        voice_guard.on_tts_start(text)
        played_via: list[str] = []
        try:
            played_via = await self._play_file_sinks(tmp_path, output)
            return played_via
        finally:
            voice_guard.on_tts_end(text, played=bool(played_via))

    async def _play_file_sinks(self, tmp_path: str, output: str) -> list[str]:
        """Route a file to camera and/or local speaker; returns the sinks used."""
        played_via: list[str] = []
        if output in ("remote", "both") and await self._play_camera(tmp_path):
            played_via.append("camera")

        # "remote" falls back to the local speaker when the camera is unavailable.
        if output in ("local", "both") or (output == "remote" and not played_via):
            if await _play_local(tmp_path):
                played_via.append("local")
        if not played_via:
            logger.warning("TTS playback failed (no working audio player found)")
        return played_via

    async def _play_camera(self, tmp_path: str) -> bool:
        ok, msg = await asyncio.to_thread(
            _play_via_go2rtc, tmp_path, self.go2rtc_url, self.go2rtc_stream
        )
        if not ok:
            logger.warning("go2rtc playback failed: %s", msg)
        return ok

    async def _play_stream(
        self, chunks: AsyncIterator[bytes], text: str, output: str, *, is_mp3: bool
    ) -> list[str]:
        """Play a synthesis stream as it arrives; runs on the queue worker.

        PCM + local output streams straight into a :class:`PcmSink`
        (``sounddevice``); the whole body is also buffered so the camera path
        can write a WAV after the download, and so a failed sink can fall back
        to file playback of the not-yet-played remainder. MP3 bodies (some
        models ignore ``pcm_16000``) are buffered whole and played via the
        file path. With ``output="both"`` the local speaker streams first and
        the camera plays the buffered file after it finishes — sequential, as
        the file path always was.
        """
        voice_guard = self._guard()
        voice_guard.on_tts_start(text)
        played_via: list[str] = []
        buffer = bytearray()
        sink: Any = None
        want_local = output in ("local", "both")
        try:
            if want_local and not is_mp3:
                try:
                    sink = open_pcm_sink(sample_rate=16000)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("streaming local playback unavailable (%s); buffering", exc)
            try:
                async for chunk in chunks:
                    buffer += chunk
                    if sink is not None:
                        sink.write(chunk)
            finally:
                if sink is not None and not await sink.close():
                    logger.warning("streaming local playback failed: %s", sink.error)

            if is_mp3:
                played_via = await self._play_tmp(
                    _write_tmp_audio(bytes(buffer), suffix=".mp3"), output
                )
                return played_via

            if sink is not None and sink.error is None:
                played_via.append("local")
            elif want_local:
                rest = bytes(buffer[sink.bytes_played if sink is not None else 0 :])
                if rest and await self._play_tmp(_write_pcm_as_wav(rest), "local"):
                    played_via.append("local")

            if output in ("remote", "both"):
                camera_mode = "remote" if "local" not in played_via else "camera_only"
                played_via.extend(
                    await self._play_tmp(_write_pcm_as_wav(bytes(buffer)), camera_mode)
                )
            if not played_via:
                logger.warning("TTS playback failed (no working audio player found)")
            return played_via
        finally:
            with contextlib.suppress(Exception):
                await chunks.aclose()  # type: ignore[attr-defined]
            voice_guard.on_tts_end(text, played=bool(played_via))

    async def _play_tmp(self, path: str, output: str) -> list[str]:
        """Play a temp file through the requested sinks, then delete it."""
        try:
            if output == "camera_only":
                return ["camera"] if await self._play_camera(path) else []
            return await self._play_file_sinks(path, output)
        finally:
            with contextlib.suppress(OSError):
                os.unlink(path)

    async def say(self, text: str, output: str | None = None) -> str:
        """Speak text aloud via ElevenLabs.

        output: "local" = PC speaker, "remote" = camera speaker (go2rtc), "both" = both.
                Defaults to self.output when not specified.

        Uses the streaming synthesis endpoint: the request is opened and the
        first audio chunk awaited here (~1 s); the rest of the body is drained
        in the background and played as it arrives by the playback queue, so
        say() returns long before synthesis or playback finish. Set
        ``FAMILIAR_TTS_BLOCKING=1`` to await playback as well.
        """
        import aiohttp

        if output is None:
            output = self.output
        if len(text) > 200:
            text = text[:197] + "..."

        base = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        query = "?output_format=pcm_16000"
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "model_id": "eleven_v3",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        async with self._lock:
            stack = contextlib.AsyncExitStack()
            try:
                session = await stack.enter_async_context(aiohttp.ClientSession())
                resp_stack = contextlib.AsyncExitStack()
                resp = await resp_stack.enter_async_context(
                    session.post(f"{base}/stream{query}", json=payload, headers=headers)
                )
                if resp.status in _STREAM_FALLBACK_STATUSES:
                    logger.info(
                        "ElevenLabs stream endpoint returned %s; retrying without /stream",
                        resp.status,
                    )
                    await resp_stack.aclose()
                    resp_stack = contextlib.AsyncExitStack()
                    resp = await resp_stack.enter_async_context(
                        session.post(f"{base}{query}", json=payload, headers=headers)
                    )
                stack.push_async_callback(resp_stack.aclose)
                if resp.status != 200:
                    err = await resp.text()
                    await stack.aclose()
                    return f"TTS API failed ({resp.status}): {err[:80]}"
                content_type = resp.headers.get("Content-Type", "")
                source = resp.content.iter_chunked(_STREAM_CHUNK_BYTES)
                try:
                    first = bytes(await source.__anext__())
                except StopAsyncIteration:
                    first = b""
            except BaseException:
                await stack.aclose()
                raise
            if not first:
                await stack.aclose()
                return "TTS API returned no audio"

            # ElevenLabs may return MP3 even when PCM was requested (model-dependent).
            is_mp3 = "mpeg" in content_type or first[:3] in (b"ID3", b"\xff\xfb", b"\xff\xf3")
            relay = AudioChunkRelay(source, head=first, close=stack.aclose)
            relay.start()

            async def play(chunks: AsyncIterator[bytes]) -> list[str]:
                return await self._play_stream(chunks, text, output, is_mp3=is_mp3)

            def cleanup(_played: list[str]) -> None:
                relay.cancel()  # no-op once drained; releases the HTTP session if dropped

            future = self._queue().enqueue_stream(
                relay, play=play, on_done=cleanup, label=text[:30]
            )

        if not _blocking_playback():
            return f"Said: {text[:50]}... (via {_output_label(output)})"

        played_via = await future
        if not played_via:
            if output == "remote":
                return "TTS remote playback failed (see log)"
            return "TTS playback failed (no working audio player found)"
        return f"Said: {text[:50]}... (via {', '.join(played_via)})"

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "say",
                "description": (
                    "Speak text aloud. Use this to communicate with people in the room."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to speak. Can include ElevenLabs audio tags like [cheerful], [warmly].",
                        },
                    },
                    "required": ["text"],
                },
            },
        ]

    async def call(self, tool_name: str, tool_input: dict) -> tuple[str, None]:
        if tool_name == "say":
            result = await self.say(tool_input["text"])
            return result, None
        return f"Unknown tool: {tool_name}", None


_STREAM_CHUNK_BYTES = 4096
# Older accounts / some voices have no streaming endpoint; retry once without it.
_STREAM_FALLBACK_STATUSES = (400, 404)


def open_pcm_sink(*, sample_rate: int = 16000) -> PcmSink:
    """Open the local streaming sink (patched in tests; raises when unavailable)."""
    return PcmSink(sample_rate=sample_rate)


def _blocking_playback() -> bool:
    """``FAMILIAR_TTS_BLOCKING=1`` restores fully synchronous say() (default: off)."""
    return os.environ.get("FAMILIAR_TTS_BLOCKING", "").strip().lower() in ("1", "true", "yes", "on")


_OUTPUT_LABELS = {"local": "local", "remote": "camera", "both": "camera, local"}


def _output_label(output: str) -> str:
    return _OUTPUT_LABELS.get(output, output)


def _pulse_env() -> dict[str, str] | None:
    """Build env dict with PULSE_SERVER/PULSE_SINK if set. Returns None if neither is set."""
    server = os.environ.get("PULSE_SERVER")
    sink = os.environ.get("PULSE_SINK")
    if not server and not sink:
        return None
    env = os.environ.copy()
    if server:
        env["PULSE_SERVER"] = server
    if sink:
        env["PULSE_SINK"] = sink
    return env


async def _play_via_sounddevice(audio_path: str) -> bool:
    """Play WAV or MP3 file using sounddevice (pure Python, no system dependency).

    WAV: decoded by soundfile directly.
    MP3: decoded frame-by-frame with PyAV (av package), then played via sounddevice.
    """

    def _play() -> bool:
        if audio_path.lower().endswith(".mp3"):
            # On Windows prefer MCI (reliable, built-in) over PyAV+sounddevice
            if sys.platform == "win32" and _play_mp3_mci(audio_path):
                return True
            return _play_mp3_via_pyav(audio_path)
        else:
            try:
                import sounddevice as sd
                import soundfile as sf
            except ImportError:
                return False
            try:
                data, samplerate = sf.read(audio_path)
                sd.play(data, samplerate)
                sd.wait()
                return True
            except Exception as e:
                logger.warning("sounddevice/soundfile WAV playback failed: %s", e)
                return False

    return await asyncio.to_thread(_play)


def _play_mp3_mci(mp3_path: str) -> bool:
    """Play MP3 using Windows MCI (Media Control Interface) via ctypes. Windows only.

    MCI is built into Windows — no extra dependencies, supports MP3 natively.
    """
    try:
        import ctypes

        winmm = ctypes.windll.winmm  # type: ignore[attr-defined]
        alias = "familiar_tts"
        abs_path = os.path.abspath(mp3_path)
        winmm.mciSendStringW(f"close {alias}", None, 0, None)  # clean up any prior
        ret = winmm.mciSendStringW(f'open "{abs_path}" type mpegvideo alias {alias}', None, 0, None)
        if ret != 0:
            logger.warning("MCI open failed (ret=%d)", ret)
            return False
        winmm.mciSendStringW(f"play {alias} wait", None, 0, None)
        winmm.mciSendStringW(f"close {alias}", None, 0, None)
        return True
    except Exception as e:
        logger.warning("MCI playback failed: %s", e)
        return False


def _play_mp3_via_pyav(mp3_path: str) -> bool:
    """Decode MP3 with PyAV to s16 PCM, play via sounddevice.

    Uses s16 interleaved stereo (simpler than fltp planar) for cross-platform reliability.
    """
    try:
        import av
        import numpy as np
        import sounddevice as sd
    except ImportError:
        logger.warning("PyAV, numpy, or sounddevice not available for MP3 decoding")
        return False
    try:
        TARGET_RATE = 44100
        container = av.open(mp3_path)
        audio_stream = next((s for s in container.streams if s.type == "audio"), None)
        if audio_stream is None:
            container.close()
            return False

        # Resample to s16p mono @ TARGET_RATE — planar mono avoids stereo packing ambiguity
        resampler = av.AudioResampler(format="s16p", layout="mono", rate=TARGET_RATE)
        chunks_nd: list = []

        for frame in container.decode(audio_stream):
            if not isinstance(frame, av.AudioFrame):
                continue
            for rf in resampler.resample(frame):
                chunks_nd.append(rf.to_ndarray())  # shape: (1, n_samples)

        # Flush resampler
        for rf in resampler.resample(None):
            chunks_nd.append(rf.to_ndarray())

        container.close()
        if not chunks_nd:
            return False

        # Concatenate along samples axis → (1, total_samples) → flatten to (total_samples,)
        audio = np.concatenate(chunks_nd, axis=1).flatten().astype(np.float32) / 32768.0
        sd.play(audio, TARGET_RATE)
        sd.wait()
        return True
    except Exception as e:
        logger.warning("PyAV MP3 playback failed: %s", e)
        return False


async def _play_local(tmp_path: str) -> bool:
    """Play audio file on the local PC speaker. Returns True on success.

    Try order:
    1. afplay (macOS built-in)
    2. paplay (PulseAudio native — most reliable on WSL2/WSLg when PULSE_SERVER is set)
    3. mpv (auto audio backend selection)
    4. sounddevice (pure Python fallback, no system tools required)

    Note: file is always WAV (pcm_16000) so paplay needs no ffmpeg conversion.
    """
    pulse_env = _pulse_env()

    # --- afplay (macOS built-in) ---
    if sys.platform == "darwin":
        afplay = shutil.which("afplay")
        if afplay:
            try:
                proc = await asyncio.create_subprocess_exec(
                    afplay,
                    tmp_path,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
                _, stderr = await proc.communicate()
                if proc.returncode == 0:
                    return True
                logger.warning(
                    "afplay failed (exit %d): %s",
                    proc.returncode,
                    stderr.decode(errors="replace")[:120],
                )
            except (FileNotFoundError, OSError) as e:
                logger.warning("Could not launch afplay: %s", e)

    # --- paplay (PulseAudio native, WAV only) ---
    paplay = shutil.which("paplay")
    if paplay and tmp_path.lower().endswith((".wav", ".wave")):
        try:
            proc = await asyncio.create_subprocess_exec(
                paplay,
                tmp_path,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
                env=pulse_env,
            )
            _, stderr = await proc.communicate()
            if proc.returncode == 0:
                return True
            err = stderr.decode(errors="replace").strip()
            logger.warning("paplay failed (exit %d): %s", proc.returncode, err[:120])
        except (FileNotFoundError, OSError) as e:
            logger.warning("Could not launch paplay: %s", e)

    # --- mpv ---
    mpv = shutil.which("mpv")
    if mpv:
        try:
            proc = await asyncio.create_subprocess_exec(
                mpv,
                "--no-terminal",
                tmp_path,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
                env=pulse_env,
            )
            _, stderr = await proc.communicate()
            if proc.returncode == 0:
                return True
            logger.warning(
                "mpv failed (exit %d): %s", proc.returncode, stderr.decode(errors="replace")[:120]
            )
        except (FileNotFoundError, OSError) as e:
            logger.warning("Could not launch mpv: %s", e)

    # --- sounddevice (pure Python, no system dependency) ---
    return await _play_via_sounddevice(tmp_path)


def _play_via_go2rtc(file_path: str, go2rtc_url: str, stream_name: str) -> tuple[bool, str]:
    """Play audio file through camera speaker via go2rtc backchannel (sync, run in thread)."""
    try:
        abs_path = os.path.abspath(file_path)
        src = f"ffmpeg:{abs_path}#audio=pcma#input=file"
        url = (
            f"{go2rtc_url}/api/streams?dst={quote(stream_name, safe='')}&src={quote(src, safe='')}"
        )
        req = urllib.request.Request(url, method="POST", data=b"")
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())

        # Check if a sender was established (camera supports backchannel)
        has_sender = any(consumer.get("senders") for consumer in body.get("consumers", []))
        if not has_sender:
            return False, "go2rtc: no audio sender (camera may not support backchannel)"

        # Find ffmpeg producer ID to poll for completion
        ffmpeg_producer_id = None
        for p in body.get("producers", []):
            if "ffmpeg" in p.get("source", ""):
                ffmpeg_producer_id = p.get("id")
                break

        if ffmpeg_producer_id:
            import time

            for _ in range(60):
                time.sleep(0.5)
                try:
                    with urllib.request.urlopen(f"{go2rtc_url}/api/streams", timeout=5) as r:
                        streams = json.loads(r.read())
                    stream = streams.get(stream_name, {})
                    still_playing = any(
                        p.get("id") == ffmpeg_producer_id for p in stream.get("producers", [])
                    )
                    if not still_playing:
                        break
                except Exception:
                    break

        return True, f"played via go2rtc → {stream_name}"
    except Exception as exc:
        return False, f"go2rtc error: {exc}"
