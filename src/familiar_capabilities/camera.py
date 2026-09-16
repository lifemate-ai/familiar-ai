"""Camera capability adapter for the generic runtime."""

from __future__ import annotations

from familiar_agent.tools.camera import CameraTool
from familiar_runtime.tools.legacy import BeforeToolCall, LegacyToolProvider


class CameraCapability(LegacyToolProvider):
    """Expose the existing CameraTool through the ToolProvider protocol.

    The capability wraps an already-constructed CameraTool so the caller keeps
    control over hardware setup (Tapo/USB selection, RTSP URL, fallback wiring).
    An optional ``before_call`` hook lets neighbour mode record exploration
    state when ``look`` fires.
    """

    def __init__(self, tool: CameraTool, *, before_call: BeforeToolCall | None = None) -> None:
        super().__init__(
            tool,
            names={"see", "look"},
            category="camera",
            tags={"neighbor", "perception"},
            before_call=before_call,
        )
