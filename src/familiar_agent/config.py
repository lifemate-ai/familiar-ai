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
    anthropic_api_key: str = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", ""))
    model: str = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    )
    max_tokens: int = 4096
    camera: CameraConfig = field(default_factory=CameraConfig)
    mobility: MobilityConfig = field(default_factory=MobilityConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
