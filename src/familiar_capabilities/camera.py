"""Camera capability adapter for the generic runtime."""

from __future__ import annotations

from familiar_agent.tools.camera import CameraTool
from familiar_runtime.tools.legacy import LegacyToolProvider


class CameraCapability(LegacyToolProvider):
    """Expose the existing CameraTool through the ToolProvider protocol.

    The capability wraps an already-constructed CameraTool so the caller keeps
    control over hardware setup (Tapo/USB selection, RTSP URL, fallback wiring).
    """

    def __init__(self, tool: CameraTool) -> None:
        super().__init__(
            tool,
            names={"see", "look"},
            category="camera",
            tags={"neighbor", "perception"},
        )
