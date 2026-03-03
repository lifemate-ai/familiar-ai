#!/usr/bin/env python3
"""Build Windows testflight package (onefile/onedir) with optional icon and external .env."""

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


def _resolve_pyinstaller_cmd() -> list[str]:
    cli = shutil.which("pyinstaller")
    if cli:
        return [cli]
    if importlib.util.find_spec("PyInstaller") is not None:
        return [sys.executable, "-m", "PyInstaller"]
    raise SystemExit(
        "pyinstaller not found. Run via build.bat/build.sh "
        "or use: uv run --with pyinstaller python scripts/release_testflight_windows.py ..."
    )


def _write_quickstart(path: Path, exe_name: str) -> None:
    text = (
        "familiar-ai Testflight\n"
        "======================\n\n"
        "1) Open .env and keep values as-is (API key is already embedded).\n"
        "2) Launch the app executable.\n"
        "3) On first run, fill setup wizard (Persona page + Camera page).\n"
        "4) If icon is not shown, keep app.ico beside the executable.\n\n"
        f"Executable: {exe_name}\n"
    )
    path.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Windows testflight package")
    ap.add_argument("--name", default="familiar-testflight", help="Executable name")
    ap.add_argument(
        "--mode",
        choices=["onefile", "onedir"],
        default="onefile",
        help="Packaging mode (default: onefile)",
    )
    ap.add_argument("--icon", default="assets/app.ico", help="Path to .ico icon")
    ap.add_argument("--env", default=".testflight/.env", help="Path to distributable .env")
    ap.add_argument(
        "--entry", default="scripts/familiar_testflight_entry.py", help="Entrypoint script"
    )
    ap.add_argument("--clean", action="store_true", help="Run pyinstaller with --clean")
    args = ap.parse_args()

    root = Path.cwd()
    icon = (root / args.icon).resolve()
    env_path = (root / args.env).resolve()
    entry = (root / args.entry).resolve()

    if not entry.exists():
        raise SystemExit(f"Entrypoint not found: {entry}")
    if not env_path.exists():
        raise SystemExit(f"Env file not found: {env_path}")

    cmd = [
        *_resolve_pyinstaller_cmd(),
        "--noconfirm",
        "--windowed",
        "--name",
        args.name,
        "--onefile" if args.mode == "onefile" else "--onedir",
    ]
    if args.clean:
        cmd.append("--clean")
    if icon.exists():
        cmd.extend(["--icon", str(icon)])
    cmd.append(str(entry))
    _run(cmd)

    dist = root / "dist"
    release = root / ".release" / args.name
    if release.exists():
        shutil.rmtree(release)
    release.mkdir(parents=True, exist_ok=True)

    if args.mode == "onefile":
        exe = dist / f"{args.name}.exe"
        if not exe.exists():
            raise SystemExit(f"Expected exe not found: {exe}")
        shutil.copy2(exe, release / exe.name)
        exe_name = exe.name
    else:
        out_dir = dist / args.name
        if not out_dir.exists():
            raise SystemExit(f"Expected output dir not found: {out_dir}")
        shutil.copytree(out_dir, release / args.name)
        exe_name = f"{args.name}/{args.name}.exe"

    shutil.copy2(env_path, release / ".env")
    if icon.exists():
        shutil.copy2(icon, release / "app.ico")

    _write_quickstart(release / "README-TESTFLIGHT.txt", exe_name=exe_name)

    zip_base = root / ".release" / args.name
    zip_path = shutil.make_archive(str(zip_base), "zip", root_dir=release)
    print(f"Built package directory: {release}")
    print(f"Built zip: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
