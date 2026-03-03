"""Simple timestamped SQLite migration runner."""

from __future__ import annotations

import importlib.util
import logging
import os
import re
import sqlite3
from pathlib import Path
from types import ModuleType
from typing import Callable

logger = logging.getLogger(__name__)

_MIGRATIONS_TABLE = "schema_migrations"


def default_migration_dir() -> Path:
    """Return the first existing `migration/` directory found upwards."""
    env = os.getenv("FAMILIAR_AI_MIGRATION_DIR")
    if env:
        return Path(env).expanduser()

    cwd_dir = Path.cwd() / "migration"
    if cwd_dir.exists():
        return cwd_dir
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "migration"
        if candidate.exists():
            return candidate
    return Path("migration")


def _ensure_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {_MIGRATIONS_TABLE} (
            id TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )


def _applied_ids(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(f"SELECT id FROM {_MIGRATIONS_TABLE}").fetchall()
    return {str(r[0]) for r in rows}


def _load_migration_module(path: Path) -> ModuleType:
    module_name = "migration_" + re.sub(r"[^a-zA-Z0-9_]", "_", path.stem)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load migration: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _get_upgrade_fn(module: ModuleType, path: Path) -> Callable[[sqlite3.Connection], None]:
    upgrade = getattr(module, "upgrade", None)
    if not callable(upgrade):
        raise RuntimeError(f"Migration missing upgrade(conn): {path}")
    return upgrade


def apply_migrations(conn: sqlite3.Connection, migration_dir: Path | None = None) -> int:
    """Apply pending migration scripts from `migration/*.py` in lexical order."""
    mig_dir = migration_dir or default_migration_dir()
    _ensure_migrations_table(conn)

    if not mig_dir.exists():
        logger.warning("Migration directory not found: %s", mig_dir)
        return 0

    files = sorted(p for p in mig_dir.glob("*.py") if p.is_file() and not p.name.startswith("_"))
    if not files:
        logger.warning("No migration scripts found in: %s", mig_dir)
        return 0

    applied = _applied_ids(conn)
    applied_count = 0

    for path in files:
        migration_id = path.stem
        if migration_id in applied:
            continue

        module = _load_migration_module(path)
        upgrade = _get_upgrade_fn(module, path)
        try:
            conn.execute("BEGIN")
            upgrade(conn)
            conn.execute(
                f"INSERT INTO {_MIGRATIONS_TABLE} (id, applied_at) VALUES (?, datetime('now'))",
                (migration_id,),
            )
            conn.commit()
            applied.add(migration_id)
            applied_count += 1
            logger.info("Applied migration: %s", migration_id)
        except Exception:
            conn.rollback()
            logger.exception("Failed migration: %s", migration_id)
            raise

    return applied_count
