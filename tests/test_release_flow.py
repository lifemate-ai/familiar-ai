from __future__ import annotations

from pathlib import Path

import pytest

from scripts.release_flow import extract_release_notes, prepare_release, read_version


def test_prepare_release_updates_version_and_changelog(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "familiar-ai"\nversion = "0.5.0"\n',
        encoding="utf-8",
    )
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n"
        "## [Unreleased]\n\n"
        "### Added\n"
        "- New thing\n\n"
        "### Changed\n"
        "- Tweaked thing\n\n"
        "## [0.5.0] - 2026-04-01\n\n"
        "### Added\n"
        "- Old thing\n",
        encoding="utf-8",
    )

    prepared = prepare_release(
        "0.6.0",
        release_date="2026-04-05",
        pyproject_path=pyproject,
        changelog_path=changelog,
    )

    assert prepared.version == "0.6.0"
    assert read_version(pyproject) == "0.6.0"

    updated = changelog.read_text(encoding="utf-8")
    assert "## [Unreleased]\n\n### Added\n\n### Changed\n\n### Fixed\n" in updated
    assert "## [0.6.0] - 2026-04-05" in updated
    assert "- New thing" in updated
    assert "- Tweaked thing" in updated


def test_prepare_release_rejects_empty_unreleased(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "familiar-ai"\nversion = "0.5.0"\n',
        encoding="utf-8",
    )
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("# Changelog\n\n## [Unreleased]\n\n", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        prepare_release("0.6.0", pyproject_path=pyproject, changelog_path=changelog)


def test_prepare_release_rejects_placeholder_only_unreleased(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "familiar-ai"\nversion = "0.5.0"\n',
        encoding="utf-8",
    )
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n## [Unreleased]\n\n### Added\n\n### Changed\n\n### Fixed\n\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="placeholders"):
        prepare_release("0.6.0", pyproject_path=pyproject, changelog_path=changelog)


def test_extract_release_notes_returns_matching_section(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n"
        "## [Unreleased]\n\n"
        "### Added\n\n"
        "## [0.6.0] - 2026-04-05\n\n"
        "### Added\n"
        "- New thing\n\n"
        "### Fixed\n"
        "- Bug fix\n\n"
        "## [0.5.0] - 2026-04-01\n\n"
        "### Added\n"
        "- Old thing\n",
        encoding="utf-8",
    )

    notes = extract_release_notes("0.6.0", changelog_path=changelog)

    assert notes.startswith("## [0.6.0] - 2026-04-05")
    assert "- New thing" in notes
    assert "- Bug fix" in notes
