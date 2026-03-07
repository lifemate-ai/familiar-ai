#!/usr/bin/env python3
"""One-command testflight release helper for Windows packaging.

Runs:
1) prepare_testflight_env.py
2) build_testflight_windows.py
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare env and build Windows testflight package")
    ap.add_argument("--name", default="familiar-testflight", help="Executable name")
    ap.add_argument(
        "--mode",
        choices=["onefile", "onedir"],
        default="onefile",
        help="Packaging mode (default: onefile)",
    )
    ap.add_argument("--icon", default="assets/app.ico", help="Path to .ico icon")
    ap.add_argument(
        "--entry", default="scripts/familiar_testflight_entry.py", help="Entrypoint script"
    )

    ap.add_argument(
        "--source-env", default=".env", help="Source env file for API key/platform/model"
    )
    ap.add_argument(
        "--output-env", default=".testflight/.env", help="Generated distributable env path"
    )
    ap.add_argument("--platform", default="", help="Override PLATFORM")
    ap.add_argument("--model", default="", help="Override MODEL")

    ap.add_argument("--clean", action="store_true", help="Pass --clean to pyinstaller")
    args = ap.parse_args()

    root = Path.cwd()
    prepare_script = root / "scripts" / "prepare_testflight_env.py"
    build_script = root / "scripts" / "build_testflight_windows.py"

    prep_cmd = [
        sys.executable,
        str(prepare_script),
        "--source-env",
        args.source_env,
        "--output",
        args.output_env,
    ]
    if args.platform:
        prep_cmd.extend(["--platform", args.platform])
    if args.model:
        prep_cmd.extend(["--model", args.model])
    _run(prep_cmd)

    build_cmd = [
        sys.executable,
        str(build_script),
        "--name",
        args.name,
        "--mode",
        args.mode,
        "--icon",
        args.icon,
        "--env",
        args.output_env,
        "--entry",
        args.entry,
    ]
    if args.clean:
        build_cmd.append("--clean")
    _run(build_cmd)

    print("Done. Share the zip in .release/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
