"""TTS tool - voice of the embodied agent (ElevenLabs + go2rtc camera speaker)."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
import urllib.request
from urllib.parse import quote

logger = logging.getLogger(__name__)


class TTSTool:
    """Text-to-speech using ElevenLabs, played via go2rtc camera speaker."""

    def __init__(
        self,
        api_key: str,
        voice_id: str,
        go2rtc_url: str = "http://localhost:1984",
        go2rtc_stream: str = "tapo_cam",
    ) -> None:
        self.api_key = api_key
        self.voice_id = voice_id
        self.go2rtc_url = go2rtc_url
        self.go2rtc_stream = go2rtc_stream

    async def say(self, text: str) -> str:
        """Speak text aloud via ElevenLabs → go2rtc camera speaker."""
        import aiohttp

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
            ok, msg = await asyncio.to_thread(
                _play_via_go2rtc, tmp_path, self.go2rtc_url, self.go2rtc_stream
            )
            if ok:
                return f"Said: {text[:50]}..."
            logger.warning("go2rtc playback failed: %s — falling back to local", msg)

            # Fallback: local player
            for player_args in (
                ["mpv", "--no-terminal", "--ao=pulse", tmp_path],
                ["mpv", "--no-terminal", tmp_path],
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", tmp_path],
            ):
                proc = await asyncio.create_subprocess_exec(
                    *player_args,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
                _, stderr = await proc.communicate()
                if proc.returncode == 0:
                    return f"Said: {text[:50]}..."
                err = stderr.decode(errors="replace").strip()
                logger.warning(
                    "%s failed (exit %d): %s", player_args[0], proc.returncode, err[:120]
                )

            return "TTS playback failed (go2rtc and local players all failed)"
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "say",
                "description": "Speak text aloud. Use to communicate with people in the room.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to speak. Can include ElevenLabs audio tags like [cheerful], [warmly].",
                        }
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
