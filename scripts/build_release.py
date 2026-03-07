#!/usr/bin/env python3
"""Build a distributable familiar-ai Windows installer.

Steps:
  1. Run PyInstaller to create dist/familiar-ai/ (onedir)
  2. Copy app.ico into dist/familiar-ai/ so the exe shows the icon at runtime
  3. Run Inno Setup (ISCC.exe) to create dist/familiar-ai-setup.exe

Usage (from repo root):
    build.bat --installer
    uv run python scripts/build_release.py
    uv run python scripts/build_release.py --name familiar-ai --version 0.3.0

Inno Setup must be installed:
    winget install JRSoftware.InnoSetup
    # or: choco install innosetup
"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def _read_version() -> str:
    """Read version from pyproject.toml."""
    toml_path = ROOT / "pyproject.toml"
    for line in toml_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("version") and "=" in line:
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return "0.0.0"


def _resolve_pyinstaller() -> list[str]:
    cli = shutil.which("pyinstaller")
    if cli:
        return [cli]
    if importlib.util.find_spec("PyInstaller") is not None:
        return [sys.executable, "-m", "PyInstaller"]
    raise SystemExit(
        "pyinstaller not found.\n"
        "Run: uv run --with pyinstaller python scripts/build_release.py\n"
        "Or:  pip install pyinstaller"
    )


def _resolve_iscc() -> str:
    """Find Inno Setup compiler (ISCC.exe)."""
    # Common install locations
    candidates = [
        shutil.which("ISCC"),
        shutil.which("iscc"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    ]
    for path in candidates:
        if path and Path(path).exists():
            return str(path)
    raise SystemExit(
        "Inno Setup (ISCC.exe) not found.\n"
        "Install via:  winget install JRSoftware.InnoSetup\n"
        "          or: choco install innosetup\n"
        "Then restart your terminal."
    )


# ---------------------------------------------------------------------------
# Build steps
# ---------------------------------------------------------------------------


def step_pyinstaller(name: str, icon: Path, entry: Path, clean: bool) -> Path:
    cmd = [
        *_resolve_pyinstaller(),
        "--noconfirm",
        "--windowed",
        "--onedir",
        "--name",
        name,
        "--hidden-import",
        "onvif",
        "--collect-data",
        "onvif",
    ]
    if clean:
        cmd.append("--clean")
    if icon.exists():
        cmd += ["--icon", str(icon)]
    cmd.append(str(entry))
    _run(cmd)

    out = ROOT / "dist" / name
    if not out.exists():
        raise SystemExit(f"PyInstaller output not found: {out}")
    print(f"PyInstaller: {out}")
    return out


def step_copy_icon(app_dir: Path, icon: Path) -> None:
    """Copy app.ico into the packaged app directory for runtime icon loading."""
    if icon.exists():
        dest = app_dir / "app.ico"
        shutil.copy2(icon, dest)
        print(f"Icon copied: {dest}")


def step_inno_setup(version: str, iss: Path, iscc: str) -> Path:
    _run([iscc, f"/DMyAppVersion={version}", str(iss)])
    out = ROOT / "dist" / "familiar-ai-setup.exe"
    if not out.exists():
        raise SystemExit(f"Installer not found after Inno Setup: {out}")
    print(f"\nInstaller: {out}")
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description="Build familiar-ai Windows installer")
    ap.add_argument("--name", default="familiar-ai", help="Exe/dir name (default: familiar-ai)")
    ap.add_argument("--version", default="", help="Override version (default: from pyproject.toml)")
    ap.add_argument("--icon", default="assets/app.ico", help="Path to .ico icon")
    ap.add_argument("--entry", default="scripts/familiar_entry.py", help="PyInstaller entry point")
    ap.add_argument("--iss", default="familiar-ai.iss", help="Inno Setup script path")
    ap.add_argument("--clean", action="store_true", help="Pass --clean to PyInstaller")
    ap.add_argument("--pyinstaller-only", action="store_true", help="Skip Inno Setup step")
    args = ap.parse_args()

    version = args.version or _read_version()
    icon = (ROOT / args.icon).resolve()
    entry = (ROOT / args.entry).resolve()
    iss = (ROOT / args.iss).resolve()

    if not entry.exists():
        raise SystemExit(f"Entry point not found: {entry}")
    if not iss.exists() and not args.pyinstaller_only:
        raise SystemExit(f"Inno Setup script not found: {iss}")

    print(f"=== familiar-ai release build v{version} ===\n")

    app_dir = step_pyinstaller(args.name, icon, entry, args.clean)
    step_copy_icon(app_dir, icon)

    if args.pyinstaller_only:
        print("\nPyInstaller done (--pyinstaller-only, skipping Inno Setup).")
        return 0

    iscc = _resolve_iscc()
    installer = step_inno_setup(version, iss, iscc)

    size_mb = installer.stat().st_size / 1024 / 1024
    print(f"\nDone! Installer: {installer} ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
