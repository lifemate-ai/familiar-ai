"""Startup/bootstrap helpers for familiar-ai."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from .setup import migrate_legacy_env_file


def resolve_env_path() -> Path:
    """Resolve the app `.env` path.

    Prefer the repository root when running from source, otherwise fall back to
    the current working directory.
    """
    root_env = Path(__file__).resolve().parents[2] / ".env"
    if root_env.exists():
        return root_env
    return Path.cwd() / ".env"


@dataclass
class AppBootstrap:
    env_path: Path
    configured: bool
    needs_setup: bool
    legacy_config_detected: bool
    migrated: bool = False
    messages: list[str] = field(default_factory=list)


def load_app_bootstrap(env_path: Path | None = None) -> AppBootstrap:
    """Load `.env`, migrate legacy Anthropic keys, and report startup status."""
    path = env_path or resolve_env_path()

    legacy_detected = False
    migrated = False
    messages: list[str] = []

    if path.exists():
        raw = path.read_text(encoding="utf-8")
        legacy_detected = "ANTHROPIC_API_KEY=" in raw or "ANTHROPIC_MODEL=" in raw
        migrated, messages = migrate_legacy_env_file(path)
        load_dotenv(path, override=True)

    api_key = (os.environ.get("API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    configured = bool(api_key)
    return AppBootstrap(
        env_path=path,
        configured=configured,
        needs_setup=not configured,
        legacy_config_detected=legacy_detected,
        migrated=migrated,
        messages=messages,
    )
