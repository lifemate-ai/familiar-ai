"""TTS tool - voice of the embodied agent (ElevenLabs + go2rtc camera speaker)."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import quote

logger = logging.getLogger(__name__)

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
        # Ensure go2rtc is running at startup
        _ensure_go2rtc(self.go2rtc_url)

    async def say(self, text: str, output: str | None = None) -> str:
        """Speak text aloud via ElevenLabs.

        output: "local" = PC speaker, "remote" = camera speaker (go2rtc), "both" = both.
                Defaults to self.output when not specified.
        """
        import aiohttp

        if output is None:
            output = self.output

        if len(text) > 200:
            text = text[:197] + "..."

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": "eleven_flash_v2_5",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    err = await resp.text()
                    return f"TTS API failed ({resp.status}): {err[:80]}"
                audio_data = await resp.read()

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_data)
            tmp_path = f.name

        try:
            played_via: list[str] = []

            # --- Remote (camera speaker via go2rtc) ---
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

            # --- Local (PC speaker) ---
            if output in ("local", "both") or (output == "remote" and not played_via):
                local_ok = await _play_local(tmp_path)
                if local_ok:
                    played_via.append("local")

            if not played_via:
                return "TTS playback failed (no working audio player found: tried mpv, ffplay)"
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


_FFPLAY_AUDIO_FAILURE = "audio open failed"


async def _play_local(tmp_path: str) -> bool:
    """Play audio file on the local PC speaker. Returns True on success."""
    candidates = [
        # mpv without --ao lets it auto-select (tries pulse, then pipewire, etc.)
        ["mpv", "--no-terminal", tmp_path],
        # ffplay fallback — note: ffplay exits 0 even on audio open failure,
        # so we check stderr for the failure marker
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "warning", tmp_path],
    ]
    for player_args in candidates:
        player_name = player_args[0]
        player_path = shutil.which(player_name)
        if player_path is None:
            logger.debug("Player not found in PATH, skipping: %s", player_name)
            continue
        resolved_args = [player_path, *player_args[1:]]
        try:
            proc = await asyncio.create_subprocess_exec(
                *resolved_args,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            err = stderr.decode(errors="replace")
            # ffplay exits 0 even when audio fails — check stderr explicitly
            if _FFPLAY_AUDIO_FAILURE in err:
                logger.warning("%s: audio open failed: %s", player_name, err[:200])
                continue
            if proc.returncode == 0:
                return True
            logger.warning("%s failed (exit %d): %s", player_name, proc.returncode, err[:120])
        except (FileNotFoundError, OSError) as e:
            logger.warning("Could not launch %s: %s", player_name, e)
    return False


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
