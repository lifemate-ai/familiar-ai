"""Configuration management."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


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


@dataclass
class MemoryConfig:
    db_path: str = field(
        default_factory=lambda: os.environ.get(
            "MEMORY_DB_PATH",
            str(Path.home() / ".claude" / "memories"),
        )
    )


@dataclass
class AgentConfig:
    # Anthropic settings (used when llm_backend == "anthropic")
    anthropic_api_key: str = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", ""))
    model: str = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    )

    # OpenAI-compatible backend settings (used when llm_backend == "openai")
    # Example: LLM_BACKEND=openai LLM_BASE_URL=http://localhost:11434/v1 LLM_MODEL=qwen2.5vl:7b
    llm_backend: str = field(default_factory=lambda: os.environ.get("LLM_BACKEND", "anthropic"))
    llm_base_url: str = field(
        default_factory=lambda: os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
    )
    llm_api_key: str = field(default_factory=lambda: os.environ.get("LLM_API_KEY", ""))
    llm_model: str = field(default_factory=lambda: os.environ.get("LLM_MODEL", ""))
    # "native" = use OpenAI function-calling API (fails if model doesn't support it)
    # "prompt" = inject tools into system prompt, parse <tool_call> JSON from output
    llm_tools_mode: str = field(default_factory=lambda: os.environ.get("LLM_TOOLS_MODE", "prompt"))

    max_tokens: int = 4096
    camera: CameraConfig = field(default_factory=CameraConfig)
    mobility: MobilityConfig = field(default_factory=MobilityConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
