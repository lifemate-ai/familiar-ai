#!/usr/bin/env python3
"""Build a standalone Windows executable for familiar-ai.

Usage (from repo root):
    build.bat
    build.bat --name familiar-ai --mode onedir
    uv run --with pyinstaller python scripts/build_windows.py

Outputs:
    dist/familiar-ai.exe          (onefile mode, default)
    dist/familiar-ai/             (onedir mode)
"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def _resolve_pyinstaller() -> list[str]:
    cli = shutil.which("pyinstaller")
    if cli:
        return [cli]
    if importlib.util.find_spec("PyInstaller") is not None:
        return [sys.executable, "-m", "PyInstaller"]
    raise SystemExit(
        "pyinstaller not found.\n"
        "Run via build.bat or: uv run --with pyinstaller python scripts/build_windows.py"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Build familiar-ai Windows package")
    ap.add_argument("--name", default="familiar-ai", help="Executable name (default: familiar-ai)")
    ap.add_argument(
        "--mode",
        choices=["onefile", "onedir"],
        default="onedir",
        help="Packaging mode (default: onedir — faster startup, easier to update)",
    )
    ap.add_argument(
        "--icon",
        default="assets/app.ico",
        help="Path to .ico icon (optional, skipped if not found)",
    )
    ap.add_argument(
        "--entry",
        default="scripts/familiar_entry.py",
        help="Entrypoint script (default: scripts/familiar_entry.py)",
    )
    ap.add_argument("--clean", action="store_true", help="Pass --clean to PyInstaller")
    ap.add_argument(
        "--no-onvif",
        action="store_true",
        help="Skip bundling onvif data (use when camera is not needed)",
    )
    args = ap.parse_args()

    root = Path.cwd()
    entry = (root / args.entry).resolve()
    icon = (root / args.icon).resolve()

    if not entry.exists():
        raise SystemExit(f"Entrypoint not found: {entry}")

    cmd = [
        *_resolve_pyinstaller(),
        "--noconfirm",
        "--windowed",
        "--name",
        args.name,
    ]

    if args.mode == "onefile":
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    if not args.no_onvif:
        cmd += ["--hidden-import", "onvif", "--collect-data", "onvif"]

    if args.clean:
        cmd.append("--clean")

    if icon.exists():
        cmd += ["--icon", str(icon)]
    else:
        print(f"Note: icon not found at {icon}, building without icon")

    cmd.append(str(entry))
    _run(cmd)

    dist = root / "dist"
    if args.mode == "onefile":
        out = dist / f"{args.name}.exe"
    else:
        out = dist / args.name

    if out.exists():
        print(f"\nBuild successful: {out}")
    else:
        raise SystemExit(f"Expected output not found: {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
