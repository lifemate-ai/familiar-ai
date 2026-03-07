"""TTS tool - voice of the embodied agent (ElevenLabs + go2rtc camera speaker)."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import quote

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
    ) -> None:
        self.api_key = api_key
        self.voice_id = voice_id
        self.go2rtc_url = go2rtc_url
        self.go2rtc_stream = go2rtc_stream
        # "local" = PC speaker only, "remote" = camera speaker only, "both" = both simultaneously
        self.output = output
        # Serialize concurrent say() calls so audio never overlaps
        self._lock = asyncio.Lock()
        # Ensure go2rtc is running at startup
        _ensure_go2rtc(self.go2rtc_url)

    async def say(self, text: str, output: str | None = None) -> str:
        """Speak text aloud via ElevenLabs.

        output: "local" = PC speaker, "remote" = camera speaker (go2rtc), "both" = both.
                Defaults to self.output when not specified.

        Concurrent calls are serialized via self._lock so audio never overlaps.
        """
        import aiohttp

        if output is None:
            output = self.output
        if len(text) > 200:
            text = text[:197] + "..."

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "model_id": "eleven_v3",
            "output_format": "pcm_16000",  # raw 16-bit mono PCM — no ffmpeg conversion needed
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        async with self._lock:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        err = await resp.text()
                        return f"TTS API failed ({resp.status}): {err[:80]}"
                    content_type = resp.headers.get("Content-Type", "")
                    audio_data = await resp.read()

            # ElevenLabs may return MP3 even when PCM was requested (model-dependent).
            # Detect by content-type and save to the correct format.
            is_mp3 = "mpeg" in content_type or audio_data[:3] in (b"ID3", b"\xff\xfb", b"\xff\xf3")
            if is_mp3:
                tmp_path = _write_tmp_audio(audio_data, suffix=".mp3")
            else:
                tmp_path = _write_pcm_as_wav(audio_data, sample_rate=16000)

            try:
                played_via: list[str] = []

                if output in ("remote", "both"):
                    ok, msg = await asyncio.to_thread(
                        _play_via_go2rtc, tmp_path, self.go2rtc_url, self.go2rtc_stream
                    )
                    if ok:
                        played_via.append("camera")
                    else:
                        logger.warning("go2rtc playback failed: %s", msg)
                        if output == "remote":
                            return f"TTS remote playback failed: {msg}"

                if output in ("local", "both") or (output == "remote" and not played_via):
                    local_ok = await _play_local(tmp_path)
                    if local_ok:
                        played_via.append("local")

                if not played_via:
                    return "TTS playback failed (no working audio player found)"
                return f"Said: {text[:50]}... (via {', '.join(played_via)})"
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

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
        try:
            import sounddevice as sd
        except ImportError:
            return False

        if audio_path.lower().endswith(".mp3"):
            return _play_mp3_via_pyav(audio_path)
        else:
            try:
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

        # Resample to s16 stereo @ 44100 Hz — single plane, easy to convert to numpy
        resampler = av.AudioResampler(format="s16", layout="stereo", rate=TARGET_RATE)
        raw_chunks: list[bytes] = []

        for frame in container.decode(audio_stream):
            if not isinstance(frame, av.AudioFrame):
                continue
            for rf in resampler.resample(frame):
                raw_chunks.append(bytes(rf.planes[0]))

        # Flush resampler
        for rf in resampler.resample(None):
            raw_chunks.append(bytes(rf.planes[0]))

        container.close()
        if not raw_chunks:
            return False

        raw = b"".join(raw_chunks)
        # s16 stereo interleaved: L0 R0 L1 R1 … → shape (N, 2), float32 for sounddevice
        audio = np.frombuffer(raw, dtype=np.int16).reshape(-1, 2).astype(np.float32) / 32768.0
        sd.play(audio, TARGET_RATE)
        sd.wait()
        return True
    except Exception as e:
        logger.warning("PyAV MP3 playback failed: %s", e)
        return False


async def _play_local(tmp_path: str) -> bool:
    """Play audio file on the local PC speaker. Returns True on success.

    Try order:
    1. paplay (PulseAudio native — most reliable on WSL2/WSLg when PULSE_SERVER is set)
    2. mpv (auto audio backend selection)
    3. sounddevice (pure Python fallback, no system tools required)

    Note: file is always WAV (pcm_16000) so paplay needs no ffmpeg conversion.
    """
    pulse_env = _pulse_env()

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
