"""Mobility tool - legs of the embodied agent (robot vacuum)."""

from __future__ import annotations

import asyncio
import logging

import tinytuya

logger = logging.getLogger(__name__)

DIRECTION_FORWARD = "forward"
DIRECTION_BACKWARD = "backward"
DIRECTION_LEFT = "turn_left"
DIRECTION_RIGHT = "turn_right"
DIRECTION_STOP = "stop"


class MobilityTool:
    """Controls a Tuya robot vacuum for movement."""

    def __init__(self, api_region: str, api_key: str, api_secret: str, device_id: str):
        self._api_region = api_region
        self._api_key = api_key
        self._api_secret = api_secret
        self._device_id = device_id
        self._cloud: tinytuya.Cloud | None = None

    def _ensure_cloud(self) -> tinytuya.Cloud:
        if self._cloud is None:
            self._cloud = tinytuya.Cloud(
                apiRegion=self._api_region,
                apiKey=self._api_key,
                apiSecret=self._api_secret,
                apiDeviceID=self._device_id,
            )
        return self._cloud

    async def _send(self, direction: str) -> None:
        cloud = self._ensure_cloud()
        commands = {"commands": [{"code": "direction_control", "value": direction}]}
        await asyncio.to_thread(cloud.sendcommand, self._device_id, commands)

    async def move(self, direction: str, duration: float | None = None) -> str:
        """Move in a direction. direction: forward/backward/left/right/stop."""
        tuya_dir = {
            "forward": DIRECTION_FORWARD,
            "backward": DIRECTION_BACKWARD,
            "left": DIRECTION_LEFT,
            "right": DIRECTION_RIGHT,
            "stop": DIRECTION_STOP,
        }.get(direction)
        if tuya_dir is None:
            return f"Invalid direction: {direction}"
        await self._send(tuya_dir)
        if duration and tuya_dir != DIRECTION_STOP:
            await asyncio.sleep(duration)
            await self._send(DIRECTION_STOP)
            return f"Moved {direction} for {duration}s and stopped."
        return f"{'Stopped.' if direction == 'stop' else f'Moving {direction}.'}"

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "walk",
                "description": (
                    "Walk the robot body. Use to navigate around the room. "
                    "Always stop after walking to avoid collisions."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "direction": {
                            "type": "string",
                            "enum": ["forward", "backward", "left", "right", "stop"],
                            "description": "Direction to move",
                        },
                        "duration": {
                            "type": "number",
                            "description": "How long to move in seconds (0.1-10). If omitted, moves until stopped.",
                            "minimum": 0.1,
                            "maximum": 10.0,
                        },
                    },
                    "required": ["direction"],
                },
            },
        ]

    async def call(self, tool_name: str, tool_input: dict) -> tuple[str, None]:
        if tool_name == "walk":
            direction = tool_input["direction"]
            duration = tool_input.get("duration")
            try:
                result = await self.move(direction, duration)
                return result, None
            except Exception as e:
                return f"Move failed: {e}", None
        return f"Unknown tool: {tool_name}", None
