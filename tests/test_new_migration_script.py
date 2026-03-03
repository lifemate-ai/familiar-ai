from __future__ import annotations

import subprocess
from pathlib import Path


def _run_script(tmp_path: Path, *args: str) -> Path:
    script = Path.cwd() / "scripts" / "new_migration.sh"
    result = subprocess.run(
        ["bash", str(script), *args, "--dir", str(tmp_path)],
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
