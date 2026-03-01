"""Configuration management."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from ._i18n import _t

load_dotenv()


def _default_companion_name() -> str:
    return _t("default_companion_name")


@dataclass
class CameraConfig:
    host: str = field(
        default_factory=lambda: os.environ.get(
            "CAMERA_HOST", os.environ.get("TAPO_CAMERA_HOST", "")
        )
    )
    username: str = field(
        default_factory=lambda: os.environ.get(
            "CAMERA_USERNAME", os.environ.get("TAPO_USERNAME", "admin")
        )
    )
    password: str = field(
        default_factory=lambda: os.environ.get(
            "CAMERA_PASSWORD", os.environ.get("TAPO_PASSWORD", "")
        )
    )
    port: int = field(
        default_factory=lambda: int(
            os.environ.get("CAMERA_ONVIF_PORT", os.environ.get("TAPO_ONVIF_PORT", "2020"))
        )
    )


@dataclass
class MobilityConfig:
    api_region: str = field(default_factory=lambda: os.environ.get("TUYA_REGION", "us"))
    api_key: str = field(default_factory=lambda: os.environ.get("TUYA_API_KEY", ""))
    api_secret: str = field(default_factory=lambda: os.environ.get("TUYA_API_SECRET", ""))
    device_id: str = field(default_factory=lambda: os.environ.get("TUYA_DEVICE_ID", ""))


@dataclass
class TTSConfig:
    elevenlabs_api_key: str = field(
        default_factory=lambda: os.environ.get("ELEVENLABS_API_KEY", "")
    )
    voice_id: str = field(
        default_factory=lambda: os.environ.get("ELEVENLABS_VOICE_ID", "cgSgspJ2msm6clMCkdW9")
    )
    go2rtc_url: str = field(
        default_factory=lambda: os.environ.get("GO2RTC_URL", "http://localhost:1984")
    )
    go2rtc_stream: str = field(default_factory=lambda: os.environ.get("GO2RTC_STREAM", "tapo_cam"))
    # Audio output routing: "local" = PC speaker only, "remote" = camera speaker only,
    # "both" = camera speaker + PC speaker simultaneously.
    output: str = field(default_factory=lambda: os.environ.get("TTS_OUTPUT", "local"))


@dataclass
class MemoryConfig:
    db_path: str = field(
        default_factory=lambda: os.environ.get(
            "MEMORY_DB_PATH",
            str(Path.home() / ".claude" / "memories"),
        )
    )


@dataclass
class STTConfig:
    # Reuses ELEVENLABS_API_KEY — no separate key needed
    elevenlabs_api_key: str = field(
        default_factory=lambda: os.environ.get("ELEVENLABS_API_KEY", "")
    )
    language: str = field(default_factory=lambda: os.environ.get("STT_LANGUAGE", "ja"))


@dataclass
class CodingConfig:
    workdir: str = field(default_factory=lambda: os.environ.get("CODING_WORKDIR", ""))
    bash_enabled: bool = field(
        default_factory=lambda: os.environ.get("CODING_BASH", "false").lower() == "true"
    )


@dataclass
class AgentConfig:
    # Agent display name shown in TUI
    agent_name: str = field(default_factory=lambda: os.environ.get("AGENT_NAME", "AI"))

    # Name of the companion/user shown in TUI and ToM tool
    companion_name: str = field(
        default_factory=lambda: os.environ.get("COMPANION_NAME", _default_companion_name())
    )

    # Platform: "anthropic" | "gemini" | "openai" | "kimi" | "glm"
    platform: str = field(default_factory=lambda: os.environ.get("PLATFORM", "anthropic"))

    # Unified API key (used for whichever platform is selected)
    api_key: str = field(default_factory=lambda: os.environ.get("API_KEY", ""))

    # Model name — platform-specific defaults applied in create_backend()
    model: str = field(default_factory=lambda: os.environ.get("MODEL", ""))

    # OpenAI-compatible only: base URL and tool-calling mode
    # TOOLS_MODE: "native" = use function-calling API, "prompt" = inject into system prompt
    base_url: str = field(
        default_factory=lambda: os.environ.get("BASE_URL", "http://localhost:11434/v1")
    )
    tools_mode: str = field(default_factory=lambda: os.environ.get("TOOLS_MODE", "prompt"))

    # Thinking mode: "auto" | "adaptive" | "extended" | "disabled"
    # "auto" = adaptive for claude-sonnet-4/opus-4, disabled for others
    thinking_mode: str = field(default_factory=lambda: os.environ.get("THINKING_MODE", "auto"))

    # Budget tokens for "extended" thinking mode (ignored in "adaptive" / "disabled")
    thinking_budget: int = field(
        default_factory=lambda: int(os.environ.get("THINKING_BUDGET_TOKENS", "10000"))
    )

    # Effort level for adaptive thinking: "high" (default) | "medium" | "low" | "max"
    # "max" is Opus 4.6 only. Ignored unless THINKING_MODE=adaptive (or auto on supported models).
    thinking_effort: str = field(default_factory=lambda: os.environ.get("THINKING_EFFORT", "high"))

    # ── Utility backend (optional) ─────────────────────────────────────
    # Separate backend for non-conversation LLM calls (day summaries, emotion
    # inference, self-model updates, etc.).  Falls back to the main backend
    # when not configured.
    utility_platform: str = field(
        default_factory=lambda: os.environ.get("UTILITY_PLATFORM", "")
    )
    utility_api_key: str = field(
        default_factory=lambda: os.environ.get("UTILITY_API_KEY", "")
    )
    utility_model: str = field(
        default_factory=lambda: os.environ.get("UTILITY_MODEL", "")
    )

    max_tokens: int = 4096
    camera: CameraConfig = field(default_factory=CameraConfig)
    mobility: MobilityConfig = field(default_factory=MobilityConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    stt: STTConfig = field(default_factory=STTConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    coding: CodingConfig = field(default_factory=CodingConfig)
