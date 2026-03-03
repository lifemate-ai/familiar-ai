#!/usr/bin/env python3
"""Generate a testflight .env with embedded API key for non-technical testers.

This script intentionally writes secrets to an output .env file for distribution,
but it does NOT commit secrets into source code.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import dotenv_values


TRUTHY = {"1", "true", "yes", "on"}


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in TRUTHY


def _pick(*values: str | None, default: str = "") -> str:
    for value in values:
        if value and str(value).strip():
            return str(value).strip()
    return default


def _quote_env(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_env_text(
    api_key: str,
    platform: str,
    model: str,
    elevenlabs_api_key: str,
    elevenlabs_voice_id: str,
) -> str:
    lines = [
        "# Auto-generated for testflight distribution",
        "TESTFLIGHT_MODE=true",
        "TESTFLIGHT_SETUP_DONE=false",
        "MOBILITY_ENABLED=false",
        f"PLATFORM={platform}",
        f"API_KEY={_quote_env(api_key)}",
        f"ELEVENLABS_API_KEY={_quote_env(elevenlabs_api_key)}",
        f"ELEVENLABS_VOICE_ID={_quote_env(elevenlabs_voice_id)}",
    ]
    if model:
        lines.append(f"MODEL={model}")
    lines.extend(
        [
            "",
            "# First-run setup dialog will ask testers to fill these:",
            "AGENT_NAME=AI",
            "COMPANION_NAME=",
            "CAMERA_HOST=",
            "CAMERA_USERNAME=admin",
            "CAMERA_PASSWORD=",
            "CAMERA_ONVIF_PORT=2020",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare .env for familiar-ai testflight builds")
    parser.add_argument(
        "--output",
        default=".testflight/.env",
        help="Output .env path (default: .testflight/.env)",
    )
    parser.add_argument(
        "--source-env",
        default=".env",
        help="Source .env path to read defaults from (default: .env)",
    )
    parser.add_argument(
        "--platform",
        default="",
        help="Override PLATFORM (default: from source env, fallback kimi)",
    )
    parser.add_argument(
        "--model",
        default="",
        help="Override MODEL (default: from source env)",
    )
    args = parser.parse_args()

    src_path = Path(args.source_env)
    src = dotenv_values(src_path) if src_path.exists() else {}

    api_key = _pick(os.environ.get("API_KEY"), src.get("API_KEY"), default="")
    if not api_key:
        raise SystemExit("API_KEY not found in environment or source .env")
    elevenlabs_api_key = _pick(
        os.environ.get("ELEVENLABS_API_KEY"), src.get("ELEVENLABS_API_KEY"), default=""
    )
    elevenlabs_voice_id = _pick(
        os.environ.get("ELEVENLABS_VOICE_ID"), src.get("ELEVENLABS_VOICE_ID"), default=""
    )

    platform = _pick(args.platform, os.environ.get("PLATFORM"), src.get("PLATFORM"), default="kimi")
    model = _pick(args.model, os.environ.get("MODEL"), src.get("MODEL"), default="")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        build_env_text(
            api_key=api_key,
            platform=platform,
            model=model,
            elevenlabs_api_key=elevenlabs_api_key,
            elevenlabs_voice_id=elevenlabs_voice_id,
        ),
        encoding="utf-8",
    )

    print(f"Wrote testflight env: {out_path}")
    if _bool_env("TESTFLIGHT_MODE", False):
        print("Note: TESTFLIGHT_MODE is currently enabled in your shell environment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
