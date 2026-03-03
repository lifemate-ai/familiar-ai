"""Camera tool - the eyes and neck of the embodied agent."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import cv2
import onvif
from onvif import ONVIFCamera

logger = logging.getLogger(__name__)

CAPTURE_DIR = Path.home() / ".familiar_ai" / "captures"


class CameraTool:
    """Controls a camera via OpenCV (RTSP, USB, file) and optionally via ONVIF (PTZ)."""

    def __init__(
        self,
        host: str | int,
        username: str | None = None,
        password: str | None = None,
        port: int = 2020,
        preview: bool = False,
    ):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.preview = preview

        self._cam_onvif: Any = None
        self._ptz: Any = None
        self._profile_token: str | None = None

        self._cap: cv2.VideoCapture | None = None
        self._last_frame: Any = None
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

        # Start background capture thread
        self.start()

    @property
    def is_pan_tilt_available(self) -> bool:
        """Check if PTZ controls are supported by the camera."""
        # ONVIF is only attempted if host is not a simple integer (USB)
        if isinstance(self.host, int) or (isinstance(self.host, str) and self.host.isdigit()):
            return False
        # If PTZ service is already connected, it's available.
        # Otherwise, assume it's available if it's an IP camera (will be lazy-connected later).
        return True

    def start(self):
        """Start the background capture thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def close(self):
        """Stop capture and release resources."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._cap:
            self._cap.release()
        cv2.destroyAllWindows()
        logger.info("Camera resources released.")

    def _capture_loop(self):
        """Background thread to keep camera buffer fresh and optionally show preview."""
        source = self._get_stream_url()
        self._cap = cv2.VideoCapture(source)

        if not self._cap.isOpened():
            logger.error("Failed to open camera source: %s", source)
            self._running = False
            return

        logger.info("Camera capture thread started for source: %s", source)

        while self._running:
            ret, frame = self._cap.read()
            if not ret:
                logger.warning("Failed to read frame, retrying in 2s...")
                time.sleep(2.0)
                self._cap.open(source)
                continue

            with self._lock:
                self._last_frame = frame.copy()

            if self.preview:
                cv2.imshow("Familiar-AI Camera Preview", frame)
                # waitKey is required for imshow to actually render
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.preview = False
                    cv2.destroyAllWindows()

        if self._cap:
            self._cap.release()
            self._cap = None

    async def _ensure_connected(self) -> bool:
        """Ensure ONVIF connection is established for PTZ (optional)."""
        if self._cam_onvif is not None:
            return True

        if isinstance(self.host, int) or (isinstance(self.host, str) and self.host.isdigit()):
            return False

        try:
            # onvif-zeep-async bug: wsdl_dir defaults to site-packages/wsdl/
            # instead of the correct site-packages/onvif/wsdl/
            onvif_dir = os.path.dirname(onvif.__file__)
            wsdl_dir = os.path.join(onvif_dir, "wsdl")
            if not os.path.isdir(wsdl_dir):
                wsdl_dir = os.path.join(os.path.dirname(onvif_dir), "wsdl")

            hostname = self.host
            if isinstance(hostname, str) and "://" in hostname:
                parsed = urlparse(hostname)
                hostname = parsed.hostname or self.host

            self._cam_onvif = ONVIFCamera(
                hostname, self.port, self.username, self.password, wsdl_dir=wsdl_dir
            )
            await self._cam_onvif.update_xaddrs()
            media = await self._cam_onvif.create_media_service()
            profiles = await media.GetProfiles()
            self._profile_token = profiles[0].token if profiles else "Profile_1"
            self._ptz = await self._cam_onvif.create_ptz_service()
            logger.info("Camera PTZ connected via ONVIF: %s", hostname)
            return True
        except Exception as e:
            logger.debug("ONVIF PTZ not available: %s", e)
            return False

    def _get_stream_url(self) -> str | int:
        if isinstance(self.host, int) or (isinstance(self.host, str) and self.host.isdigit()):
            return int(self.host)
        if "://" in self.host:
            return self.host
        auth = f"{self.username}:{self.password}@" if self.username and self.password else ""
        return f"rtsp://{auth}{self.host}:554/stream1"

    async def capture(self) -> tuple[str | None, str | None]:
        """Get the latest frame from the background thread. Returns (base64_jpeg, saved_path)."""
        frame = None
        with self._lock:
            if self._last_frame is not None:
                frame = self._last_frame.copy()

        if frame is None:
            logger.warning("No frame available from capture thread.")
            return None, None

        try:
            # Resize for AI (standardizing input size)
            h, w = frame.shape[:2]
            target_h = 640
            if h > target_h:
                scale = target_h / h
                frame = cv2.resize(frame, (int(w * scale), target_h))

            # Encode
            success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not success:
                return None, None

            data = buffer.tobytes()
            b64 = base64.b64encode(data).decode()

            # Save to disk
            CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = CAPTURE_DIR / f"capture_{timestamp}.jpg"
            save_path.write_bytes(data)

            return b64, str(save_path)
        except Exception as e:
            logger.warning("Error processing frame: %s", e)
            return None, None

    async def move(self, direction: str, degrees: int = 30) -> str:
        if not await self._ensure_connected():
            return "Camera movement (PTZ) not supported for this source."
        try:
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

            await self._ptz.RelativeMove({
                "ProfileToken": self._profile_token,
                "Translation": {"PanTilt": {"x": pan_delta, "y": tilt_delta}},
            })
            await asyncio.sleep(0.4)
            return f"Looked {direction} by ~{degrees} degrees."
        except Exception as e:
            logger.warning("Camera move failed: %s", e)
            self._cam_onvif = None
            return f"Camera move failed: {e}"

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "see",
                "description": "Open your eyes and see what's in front of you. Use freely without asking permission.",
                "input_schema": {"type": "object", "properties": {}},
            },
            {
                "name": "look",
                "description": "Turn your neck to look in a direction.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "direction": {"type": "string", "enum": ["left", "right", "up", "down"]},
                        "degrees": {"type": "integer", "default": 30},
                    },
                    "required": ["direction"],
                },
            },
        ]

    async def call(self, tool_name: str, tool_input: dict) -> tuple[str, str | None]:
        if tool_name == "see":
            b64, save_path = await self.capture()
            if b64:
                return f"You see the current view (saved to {save_path}).", b64
            return "Camera capture failed.", None
        elif tool_name == "look":
            return await self.move(tool_input["direction"], tool_input.get("degrees", 30)), None
        return f"Unknown tool: {tool_name}", None
