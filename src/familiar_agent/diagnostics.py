"""GUI diagnostics and connection-test helpers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .realtime_stt_session import RealtimeSttSession
from .setup import validate_camera_connection

if TYPE_CHECKING:
    from .config import AgentConfig


@dataclass(frozen=True)
class GuiDiagnosticsSnapshot:
    """Compact runtime view for GUI support/debug output."""

    phase: str
    headline: str
    detail: str
    readiness: str
    queue_backlog: int
    last_error: str
    platform_summary: str
    utility_summary: str
    scene_summary: str
    embedding_ready: bool
    mcp_ready: bool
    realtime_stt_connected: bool
    realtime_stt_gated: bool


def _backend_summary(platform: str, model: str) -> str:
    plat = (platform or "unset").strip() or "unset"
    mdl = (model or "default").strip() or "default"
    return f"{plat} / {mdl}"


def build_gui_diagnostics(window: Any) -> GuiDiagnosticsSnapshot:
    """Collect a best-effort diagnostics snapshot from a FamiliarWindow-like object."""
    agent = getattr(window, "_agent", None)
    config = getattr(window, "_config", None) or getattr(agent, "config", None)
    realtime_stt = getattr(window, "_realtime_stt", None)
    startup_status = getattr(window, "_startup_status", "") or "Starting familiar-ai..."
    agent_ready = bool(getattr(window, "_agent_ready", False))
    agent_running = bool(getattr(window, "_agent_running", False))
    agent_init_failed = bool(getattr(window, "_agent_init_failed", False))
    last_error = str(getattr(window, "_last_error", "") or "")
    queue = getattr(window, "_input_queue", None)
    queue_backlog = int(queue.qsize()) if queue is not None else 0
    embedding_ready = bool(getattr(agent, "is_embedding_ready", False))
    mcp_ready = bool(getattr(getattr(agent, "_mcp", None), "is_started", False))
    stt_connected = bool(getattr(realtime_stt, "connected", False))
    stt_gated = bool(getattr(realtime_stt, "gated", False))

    if agent_init_failed:
        phase = "error"
        headline = "Initialization failed"
        detail = startup_status
    elif not agent_ready:
        phase = "startup"
        headline = "Starting up"
        detail = startup_status
    elif agent_running:
        phase = "thinking"
        headline = "Thinking"
        detail = "The agent is processing the current turn."
    elif stt_gated:
        phase = "stt_gated"
        headline = "STT gated by TTS"
        detail = "Realtime STT is temporarily ignoring self-echo while voice playback settles."
    else:
        phase = "ready"
        headline = "Ready"
        detail = "Waiting for input."

    readiness_bits = [
        "agent=ready" if agent_ready else "agent=starting",
        "embedding=ready" if embedding_ready else "embedding=warming",
        "mcp=ready" if mcp_ready else "mcp=connecting",
        "stt=connected" if stt_connected else "stt=idle",
    ]
    if stt_gated:
        readiness_bits.append("stt=gated")
    readiness = ", ".join(readiness_bits)

    if config is None:
        platform_summary = "unset / default"
        utility_summary = "unset / default"
        scene_summary = "unset / default"
    else:
        platform_summary = _backend_summary(
            getattr(config, "platform", ""),
            getattr(config, "model", ""),
        )
        utility_summary = _backend_summary(
            getattr(config, "utility_platform", ""),
            getattr(config, "utility_model", ""),
        )
        scene_summary = _backend_summary(
            getattr(config, "scene_platform", ""),
            getattr(config, "scene_model", ""),
        )

    return GuiDiagnosticsSnapshot(
        phase=phase,
        headline=headline,
        detail=detail,
        readiness=readiness,
        queue_backlog=queue_backlog,
        last_error=last_error,
        platform_summary=platform_summary,
        utility_summary=utility_summary,
        scene_summary=scene_summary,
        embedding_ready=embedding_ready,
        mcp_ready=mcp_ready,
        realtime_stt_connected=stt_connected,
        realtime_stt_gated=stt_gated,
    )


def format_gui_diagnostics(snapshot: GuiDiagnosticsSnapshot) -> str:
    """Render a diagnostics snapshot as clipboard-friendly text."""
    lines = [
        "familiar-ai diagnostics",
        f"phase: {snapshot.phase}",
        f"headline: {snapshot.headline}",
        f"detail: {snapshot.detail}",
        f"readiness: {snapshot.readiness}",
        f"platform/model: {snapshot.platform_summary}",
        f"utility: {snapshot.utility_summary}",
        f"scene: {snapshot.scene_summary}",
        f"queue_backlog: {snapshot.queue_backlog}",
        f"embedding_ready: {snapshot.embedding_ready}",
        f"mcp_ready: {snapshot.mcp_ready}",
        f"realtime_stt_connected: {snapshot.realtime_stt_connected}",
        f"realtime_stt_gated: {snapshot.realtime_stt_gated}",
        f"last_error: {snapshot.last_error or 'none'}",
    ]
    return "\n".join(lines)


async def test_backend_connection(config: "AgentConfig") -> tuple[bool, str]:
    """Best-effort LLM backend smoke test."""
    from .backend import create_backend  # noqa: PLC0415

    if not config.api_key and config.platform != "cli":
        return False, "API_KEY is not set."

    try:
        backend = create_backend(config)
        reply = await asyncio.wait_for(
            backend.complete("Reply with OK.", max_tokens=8), timeout=20.0
        )
    except Exception as exc:
        return False, str(exc)

    text = (reply or "").strip()
    if not text:
        return False, "Backend returned an empty reply."
    return True, text[:120]


async def test_camera_connection_from_config(config: "AgentConfig") -> tuple[bool, str]:
    """Validate ONVIF connectivity from the current config."""
    camera = config.camera
    if not camera.host:
        return False, "CAMERA_HOST is not set."
    return await validate_camera_connection(
        host=camera.host,
        username=camera.username,
        password=camera.password,
        port=camera.port,
    )


async def test_realtime_stt_connection_from_config(config: "AgentConfig") -> tuple[bool, str]:
    """Open and close the realtime STT websocket without starting microphone capture."""
    if not config.realtime_stt:
        return False, "REALTIME_STT is disabled."
    if not config.tts.elevenlabs_api_key:
        return False, "ELEVENLABS_API_KEY is not set."

    session = RealtimeSttSession(
        config.tts.elevenlabs_api_key,
        language_code=config.stt.language,
    )
    try:
        await asyncio.wait_for(session._connect_client(), timeout=15.0)
    except Exception as exc:
        return False, str(exc)
    finally:
        await session.stop()
    return True, "Realtime STT websocket connected."
