"""Characterization tests for the coding tool provider."""

from __future__ import annotations

from pathlib import Path

import pytest

from familiar_agent.config import CodingConfig
from familiar_agent.tools.coding import CodingTool


def _tool(tmp_path: Path, *, bash_enabled: bool = False) -> CodingTool:
    return CodingTool(CodingConfig(workdir=str(tmp_path), bash_enabled=bash_enabled))


def test_bash_definition_is_hidden_unless_enabled(tmp_path: Path) -> None:
    disabled_names = {spec["name"] for spec in _tool(tmp_path).get_tool_definitions()}
    enabled_names = {
        spec["name"] for spec in _tool(tmp_path, bash_enabled=True).get_tool_definitions()
    }

    assert "bash" not in disabled_names
    assert "run_tests" not in disabled_names
    assert "bash" in enabled_names
    assert "run_tests" in enabled_names


@pytest.mark.asyncio
async def test_read_file_returns_cat_n_style_line_numbers(tmp_path: Path) -> None:
    (tmp_path / "sample.txt").write_text("alpha\nbeta\ngamma\n", encoding="utf-8")

    text, image = await _tool(tmp_path).call(
        "read_file",
        {"path": "sample.txt", "offset": 1, "limit": 2},
    )

    assert image is None
    assert "     1\talpha\n" in text
    assert "     2\tbeta\n" in text
    assert "gamma" not in text


@pytest.mark.asyncio
async def test_edit_file_rejects_non_unique_old_string(tmp_path: Path) -> None:
    target = tmp_path / "sample.txt"
    target.write_text("same\nsame\n", encoding="utf-8")

    text, image = await _tool(tmp_path).call(
        "edit_file",
        {"path": "sample.txt", "old_string": "same", "new_string": "changed"},
    )

    assert image is None
    assert "matches 2 locations" in text
    assert target.read_text(encoding="utf-8") == "same\nsame\n"


@pytest.mark.asyncio
async def test_write_file_creates_parent_directories(tmp_path: Path) -> None:
    text, image = await _tool(tmp_path).call(
        "write_file",
        {"path": "nested/sample.txt", "content": "hello\n"},
    )

    assert image is None
    assert "Wrote nested/sample.txt" in text
    assert (tmp_path / "nested" / "sample.txt").read_text(encoding="utf-8") == "hello\n"


@pytest.mark.asyncio
async def test_multi_edit_file_applies_replacements_atomically(tmp_path: Path) -> None:
    target = tmp_path / "sample.txt"
    target.write_text("alpha\nbeta\n", encoding="utf-8")

    text, image = await _tool(tmp_path).call(
        "multi_edit_file",
        {
            "path": "sample.txt",
            "edits": [
                {"old_string": "alpha", "new_string": "one"},
                {"old_string": "missing", "new_string": "two"},
            ],
        },
    )

    assert image is None
    assert "old_string not found" in text
    assert target.read_text(encoding="utf-8") == "alpha\nbeta\n"


@pytest.mark.asyncio
async def test_grep_content_mode_caps_results_at_500_lines(tmp_path: Path) -> None:
    target = tmp_path / "many.txt"
    target.write_text("\n".join("hit" for _ in range(501)) + "\n", encoding="utf-8")

    text, image = await _tool(tmp_path).call(
        "grep",
        {"pattern": "hit", "path": str(target), "output_mode": "content"},
    )

    lines = text.splitlines()
    assert image is None
    assert len(lines) == 500
    assert lines[0].endswith(":1: hit")
    assert lines[-1].endswith(":500: hit")


@pytest.mark.asyncio
async def test_git_status_uses_workdir(tmp_path: Path) -> None:
    await _tool(tmp_path)._run_process(["git", "init"], timeout=20)

    text, image = await _tool(tmp_path).call("git_status", {})

    assert image is None
    assert "##" in text


@pytest.mark.asyncio
async def test_run_tests_requires_bash_enabled(tmp_path: Path) -> None:
    text, image = await _tool(tmp_path).call("run_tests", {"command": "echo ok"})

    assert image is None
    assert "CODING_BASH=true" in text
