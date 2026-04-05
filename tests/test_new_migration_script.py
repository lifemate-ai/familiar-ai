from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def _bash_executable() -> str:
    if os.name != "nt":
        return "bash"

    git_exe = shutil.which("git.exe") or shutil.which("git")
    if git_exe:
        git_bash = Path(git_exe).with_name("bash.exe")
        if git_bash.exists():
            return str(git_bash)

    candidates = [
        Path(os.environ.get("ProgramW6432", r"C:\Program Files")) / "Git" / "bin" / "bash.exe",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "bin" / "bash.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
        / "Git"
        / "bin"
        / "bash.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return "bash"


def _run_script(tmp_path: Path, *args: str) -> Path:
    script = Path.cwd() / "scripts" / "new_migration.sh"
    result = subprocess.run(
        [_bash_executable(), str(script), *args, "--dir", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip())


def test_new_migration_script_creates_file_with_slug_and_template(tmp_path) -> None:
    created = _run_script(tmp_path, "Add memory jobs table", "--date", "2026-03-03")
    assert created.name == "2026-03-03-001_add_memory_jobs_table.py"
    content = created.read_text(encoding="utf-8")
    assert "def upgrade(conn: sqlite3.Connection) -> None:" in content
    assert '"""TODO: describe migration."""' in content


def test_new_migration_script_increments_sequence(tmp_path) -> None:
    first = _run_script(tmp_path, "first", "--date", "2026-03-03")
    second = _run_script(tmp_path, "second", "--date", "2026-03-03")
    assert first.name.startswith("2026-03-03-001_")
    assert second.name.startswith("2026-03-03-002_")


def test_new_migration_script_accepts_windows_style_dir_with_cygpath(tmp_path) -> None:
    script = Path.cwd() / "scripts" / "new_migration.sh"
    fake_cygdrive = tmp_path / "cygdrive" / "c"
    fake_cygdrive.mkdir(parents=True)
    fake_root_name = f"fake-root-{tmp_path.name}"
    fake_root = fake_cygdrive / fake_root_name
    fake_root.mkdir()
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fake_cygpath = fake_bin / "cygpath"
    fake_cygpath.write_text(
        r"""#!/usr/bin/env bash
set -euo pipefail

mode="$1"
path="$2"
fake_cygdrive="${FAKE_CYGDRIVE:?}"
path="${path//\\//}"

case "$mode" in
  -u)
    case "$path" in
      C:/*)
        root_name="${path#C:/}"
        root_name="${root_name%%/*}"
        suffix="${path#C:/$root_name/}"
        printf '%s/%s/%s\n' "$fake_cygdrive" "$root_name" "$suffix"
        ;;
      *)
        printf '%s\n' "$path"
        ;;
    esac
    ;;
  *)
    echo "unsupported cygpath mode: $mode" >&2
    exit 1
    ;;
esac
""",
        encoding="utf-8",
    )
    fake_cygpath.chmod(0o755)

    env = os.environ.copy()
    env["FAKE_CYGDRIVE"] = str(fake_cygdrive)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    windows_dir = rf"C:\{fake_root_name}\migrations"

    result = subprocess.run(
        [
            _bash_executable(),
            str(script),
            "Add memory jobs table",
            "--date",
            "2026-03-03",
            "--dir",
            windows_dir,
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.stdout.strip() == (
        f"C:/{fake_root_name}/migrations/2026-03-03-001_add_memory_jobs_table.py"
    )
    actual = fake_root / "migrations" / "2026-03-03-001_add_memory_jobs_table.py"
    assert actual.exists()
