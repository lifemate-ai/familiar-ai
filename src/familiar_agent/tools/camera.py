"""Camera tool - the eyes and neck of the embodied agent."""

from __future__ import annotations

import asyncio
import base64
import logging
import tempfile
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

CAPTURE_DIR = Path.home() / ".familiar_ai" / "captures"


class CameraTool:
    """Controls a Tapo Wi-Fi PTZ camera via ONVIF + RTSP."""

    def __init__(self, host: str, username: str, password: str, port: int = 2020):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self._cam = None
        self._ptz = None
        self._profile_token: str | None = None

    async def _ensure_connected(self) -> bool:
        """Ensure ONVIF connection is established."""
        if self._cam is not None:
            return True
        try:
            import os
            import onvif
            from onvif import ONVIFCamera

            # onvif-zeep-async bug: wsdl_dir defaults to site-packages/wsdl/
            # instead of the correct site-packages/onvif/wsdl/
            onvif_dir = os.path.dirname(onvif.__file__)
            wsdl_dir = os.path.join(onvif_dir, "wsdl")
            if not os.path.isdir(wsdl_dir):
                wsdl_dir = os.path.join(os.path.dirname(onvif_dir), "wsdl")

            self._cam = ONVIFCamera(
                self.host,
                self.port,
                self.username,
                self.password,
                wsdl_dir=wsdl_dir,
            )
            await self._cam.update_xaddrs()

            media = await self._cam.create_media_service()
            profiles = await media.GetProfiles()
            if profiles:
                self._profile_token = profiles[0].token
            else:
                self._profile_token = "Profile_1"

            self._ptz = await self._cam.create_ptz_service()
            logger.info("Camera connected: %s (profile: %s)", self.host, self._profile_token)
            return True
        except Exception as e:
            logger.warning("Camera connection failed: %s", e)
            self._cam = None
            self._ptz = None
            self._profile_token = None
            return False

    async def capture(self) -> tuple[str | None, str | None]:
        """Capture image via RTSP. Returns (base64_jpeg, saved_path)."""
        stream_url = f"rtsp://{self.username}:{self.password}@{self.host}:554/stream1"
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            tmp_path = f.name
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg",
                # Low-latency RTSP transport
                "-rtsp_transport",
                "tcp",
                "-fflags",
                "nobuffer",
                "-flags",
                "low_delay",
                "-i",
                stream_url,
                # Grab first frame quickly
                "-vframes",
                "1",
                "-q:v",
                "3",
                "-vf",
                "scale=1280:-1",
                "-y",
                tmp_path,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.wait_for(proc.wait(), timeout=8.0)
            p = Path(tmp_path)
            if p.exists() and p.stat().st_size > 0:
                data = p.read_bytes()
                b64 = base64.b64encode(data).decode()

                # Save to disk for review
                CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = CAPTURE_DIR / f"capture_{timestamp}.jpg"
                save_path.write_bytes(data)

                return b64, str(save_path)
            return None, None
        except asyncio.TimeoutError:
            logger.warning("RTSP capture timed out")
            return None, None
        except Exception as e:
            logger.warning("Capture failed: %s", e)
            return None, None
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    async def move(self, direction: str, degrees: int = 30) -> str:
        """Move camera using RelativeMove. direction: left/right/up/down."""
        if not await self._ensure_connected():
            return "Camera not available."
        try:
            # Normalize to ONVIF range (-1.0 to +1.0)
            # Tapo C220: positive x = physical LEFT, positive y = physical DOWN
            pan_delta = 0.0
            tilt_delta = 0.0

            if direction == "left":
                pan_delta = degrees / 180.0
            elif direction == "right":
                pan_delta = -degrees / 180.0
            elif direction == "up":
                tilt_delta = -degrees / 90.0
            elif direction == "down":
                tilt_delta = degrees / 90.0

            await self._ptz.RelativeMove(
                {
                    "ProfileToken": self._profile_token,
                    "Translation": {
                        "PanTilt": {"x": pan_delta, "y": tilt_delta},
                    },
                }
            )
            await asyncio.sleep(0.4)
            return f"Looked {direction} by ~{degrees} degrees."
        except Exception as e:
            logger.warning("Camera move failed: %s", e)
            self._cam = None  # Force reconnect next time
            return f"Camera move failed: {e}"

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "camera_capture",
                "description": (
                    "Take a photo with your eyes (camera). "
                    "Use this to see what's in front of you. "
                    "Always capture after moving to see your new surroundings."
                ),
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "camera_look",
                "description": (
                    "Move your neck (camera) to look in a direction. "
                    "Use to explore different areas around you."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "direction": {
                            "type": "string",
                            "enum": ["left", "right", "up", "down"],
                            "description": "Direction to look",
                        },
                        "degrees": {
                            "type": "integer",
                            "description": "How many degrees to turn (1-90, default 30)",
                            "minimum": 1,
                            "maximum": 90,
                        },
                    },
                    "required": ["direction"],
                },
            },
        ]

    async def call(self, tool_name: str, tool_input: dict) -> tuple[str, str | None]:
        if tool_name == "camera_capture":
            b64, save_path = await self.capture()
            if b64:
                msg = "Image captured."
                if save_path:
                    msg += f" Saved to {save_path}"
                return msg, b64
            return "Camera not available or capture failed.", None
        elif tool_name == "camera_look":
            direction = tool_input["direction"]
            degrees = tool_input.get("degrees", 30)
            result = await self.move(direction, degrees)
            return result, None
        return f"Unknown tool: {tool_name}", None
