"""Coding tools — Read/Edit/Glob/Grep/Bash for agent-driven development.

These tools give the agent CC-style file manipulation capabilities so it can
read and modify code, search the codebase, and run shell commands.

Security model:
- read_file / edit_file / glob / grep: always available, paths resolved relative to
  CODING_WORKDIR (falls back to cwd if unset).
- bash: opt-in only — requires CODING_BASH=true env var.  When disabled the tool
  definition is simply not advertised to the LLM.
"""

from __future__ import annotations

import asyncio
import fnmatch
import re
import subprocess
from pathlib import Path
from typing import Any

from ..config import CodingConfig


class CodingTool:
    """File-system and shell tools for coding tasks."""

    def __init__(self, config: CodingConfig) -> None:
        self._config = config

    # ── helpers ────────────────────────────────────────────────────────────

    def _resolve(self, path: str) -> Path:
        """Resolve a path relative to CODING_WORKDIR (or cwd if unset)."""
        p = Path(path)
        if p.is_absolute():
            return p
        base = Path(self._config.workdir) if self._config.workdir else Path.cwd()
        return base / p

    def _workdir(self) -> Path:
        return Path(self._config.workdir) if self._config.workdir else Path.cwd()

    # ── tool definitions ──────────────────────────────────────────────────

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        defs: list[dict[str, Any]] = [
            {
                "name": "read_file",
                "description": (
                    "Read a file and return its contents with line numbers (cat -n format). "
                    "Use offset and limit to read large files in chunks."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (absolute or relative to working directory)",
                        },
                        "offset": {
                            "type": "integer",
                            "description": "1-based line number to start reading from (default: 1)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of lines to read (default: all)",
                        },
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "edit_file",
                "description": (
                    "Edit a file by replacing old_string with new_string. "
                    "old_string must appear exactly once in the file. "
                    "ALWAYS call read_file before edit_file to confirm the exact text."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path to edit",
                        },
                        "old_string": {
                            "type": "string",
                            "description": "Exact text to find and replace (must be unique in file)",
                        },
                        "new_string": {
                            "type": "string",
                            "description": "Replacement text",
                        },
                    },
                    "required": ["path", "old_string", "new_string"],
                },
            },
            {
                "name": "glob",
                "description": (
                    "Find files matching a glob pattern (e.g. '**/*.py'). "
                    "Returns a newline-separated list of matching file paths."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern (e.g. '**/*.py', 'src/**/*.ts')",
                        },
                        "path": {
                            "type": "string",
                            "description": "Root directory to search in (default: working directory)",
                        },
                    },
                    "required": ["pattern"],
                },
            },
            {
                "name": "grep",
                "description": (
                    "Search file contents using a regular expression pattern. "
                    "Returns matching file paths (files_with_matches mode) or "
                    "matching lines with context (content mode)."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Regular expression pattern to search for",
                        },
                        "path": {
                            "type": "string",
                            "description": "File or directory to search (default: working directory)",
                        },
                        "glob": {
                            "type": "string",
                            "description": "Filter files by glob pattern (e.g. '*.py')",
                        },
                        "output_mode": {
                            "type": "string",
                            "enum": ["files_with_matches", "content"],
                            "description": (
                                "Output mode: 'files_with_matches' (default) or "
                                "'content' (show matching lines)"
                            ),
                        },
                    },
                    "required": ["pattern"],
                },
            },
        ]

        if self._config.bash_enabled:
            defs.append(
                {
                    "name": "bash",
                    "description": (
                        "Run a shell command and return its stdout+stderr. "
                        "Working directory is set to CODING_WORKDIR if configured. "
                        "Default timeout: 30 seconds."
                    ),
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Shell command to execute",
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds (default: 30)",
                            },
                        },
                        "required": ["command"],
                    },
                }
            )

        return defs

    # ── dispatcher ────────────────────────────────────────────────────────

    async def call(self, name: str, tool_input: dict[str, Any]) -> tuple[str, str | None]:
        try:
            if name == "read_file":
                return self._read_file(**tool_input), None
            if name == "edit_file":
                return self._edit_file(**tool_input), None
            if name == "glob":
                return self._glob(**tool_input), None
            if name == "grep":
                return self._grep(**tool_input), None
            if name == "bash":
                return await self._bash(**tool_input), None
            return f"Unknown coding tool: {name}", None
        except Exception as e:
            return f"Error: {e}", None

    # ── implementations ───────────────────────────────────────────────────

    def _read_file(self, path: str, offset: int = 1, limit: int = 0) -> str:
        resolved = self._resolve(path)
        try:
            text = resolved.read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            return f"File not found: {path}"
        except IsADirectoryError:
            return f"Path is a directory: {path}"

        lines = text.splitlines(keepends=True)
        total = len(lines)

        start = max(0, offset - 1)  # convert 1-based to 0-based
        end = (start + limit) if limit > 0 else total

        selected = lines[start:end]
        if not selected:
            return f"(empty or offset beyond end of file — total lines: {total})"

        buf = []
        for i, line in enumerate(selected, start=start + 1):
            buf.append(f"{i:6d}\t{line}")

        result = "".join(buf)
        if not result.endswith("\n"):
            result += "\n"

        if end < total:
            result += f"\n(showing lines {start + 1}–{end} of {total}; use offset/limit for more)"

        return result

    def _edit_file(self, path: str, old_string: str, new_string: str) -> str:
        resolved = self._resolve(path)
        try:
            original = resolved.read_text(encoding="utf-8")
        except FileNotFoundError:
            return f"File not found: {path}"

        count = original.count(old_string)
        if count == 0:
            return (
                "edit_file failed: old_string not found in file.\n"
                "Tip: call read_file first and copy the exact text."
            )
        if count > 1:
            return (
                f"edit_file failed: old_string matches {count} locations. "
                "Provide a longer, more unique string."
            )

        updated = original.replace(old_string, new_string, 1)
        resolved.write_text(updated, encoding="utf-8")
        return f"Edited {path}: replaced 1 occurrence."

    def _glob(self, pattern: str, path: str = "") -> str:
        root = Path(path) if path else self._workdir()
        try:
            matches = sorted(root.glob(pattern))
        except Exception as e:
            return f"Glob error: {e}"

        if not matches:
            return f"No files matched: {pattern}"

        lines = [str(m) for m in matches]
        return "\n".join(lines)

    def _grep(
        self,
        pattern: str,
        path: str = "",
        glob: str = "",
        output_mode: str = "files_with_matches",
    ) -> str:
        root = Path(path) if path else self._workdir()

        try:
            regex = re.compile(pattern)
        except re.error as e:
            return f"Invalid regex: {e}"

        # Collect candidate files
        if root.is_file():
            candidates = [root]
        else:
            candidates = [p for p in root.rglob("*") if p.is_file()]
            if glob:
                candidates = [p for p in candidates if fnmatch.fnmatch(p.name, glob)]

        matched_files: list[str] = []
        content_lines: list[str] = []

        for fpath in sorted(candidates):
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            if output_mode == "content":
                for lineno, line in enumerate(text.splitlines(), start=1):
                    if regex.search(line):
                        content_lines.append(f"{fpath}:{lineno}: {line}")
            else:
                if regex.search(text):
                    matched_files.append(str(fpath))

        if output_mode == "content":
            if not content_lines:
                return "No matches found."
            return "\n".join(content_lines[:500])  # cap at 500 lines

        if not matched_files:
            return "No matching files found."
        return "\n".join(matched_files)

    async def _bash(self, command: str, timeout: int = 30) -> str:
        cwd = str(self._workdir())
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
            )
            try:
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                return f"Command timed out after {timeout}s: {command}"

            output = stdout.decode("utf-8", errors="replace") if stdout else ""
            rc = proc.returncode or 0
            if rc != 0:
                return f"Exit {rc}:\n{output}"
            return output or "(no output)"
        except Exception as e:
            return f"Bash error: {e}"
