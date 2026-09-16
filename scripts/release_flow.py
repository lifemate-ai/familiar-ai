#!/usr/bin/env python3
"""Helpers for the develop -> main release flow.

Commands:
  version                  Print the current project version from pyproject.toml.
  prepare VERSION          Update pyproject.toml and roll CHANGELOG.md Unreleased into VERSION.
  notes VERSION            Print the CHANGELOG section for VERSION.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
CHANGELOG = ROOT / "CHANGELOG.md"
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
VERSION_LINE_RE = re.compile(r'^(version\s*=\s*")([^"]+)(")$', re.MULTILINE)
UNRELEASED_RE = re.compile(r"(?ms)^## \[Unreleased\]\n(?P<body>.*?)(?=^## \[|\Z)")
RELEASE_SECTION_RE = re.compile(
    r"(?ms)^## \[(?P<version>[^\]]+)\] - (?P<date>\d{4}-\d{2}-\d{2})\n(?P<body>.*?)(?=^## \[|\Z)"
)

EMPTY_UNRELEASED_TEMPLATE = "### Added\n\n### Changed\n\n### Fixed\n"


@dataclass(frozen=True)
class PreparedRelease:
    version: str
    release_date: str


def read_version(pyproject_path: Path = PYPROJECT) -> str:
    content = pyproject_path.read_text(encoding="utf-8")
    match = VERSION_LINE_RE.search(content)
    if not match:
        raise ValueError(f"Could not find version in {pyproject_path}")
    return match.group(2)


def write_version(version: str, pyproject_path: Path = PYPROJECT) -> None:
    content = pyproject_path.read_text(encoding="utf-8")
    updated, count = VERSION_LINE_RE.subn(rf"\g<1>{version}\g<3>", content, count=1)
    if count != 1:
        raise ValueError(f"Could not update version in {pyproject_path}")
    pyproject_path.write_text(updated, encoding="utf-8")


def _normalize_body(body: str) -> str:
    trimmed = body.strip()
    return (trimmed + "\n") if trimmed else ""


def _validate_version(version: str) -> None:
    if not SEMVER_RE.fullmatch(version):
        raise ValueError(f"Version must match X.Y.Z: {version}")


def _is_placeholder_only_unreleased(body: str) -> bool:
    normalize = lambda s: re.sub(r"\s+", "", s)  # noqa: E731
    return normalize(body) == normalize(EMPTY_UNRELEASED_TEMPLATE)


def prepare_release(
    version: str,
    *,
    release_date: str | None = None,
    pyproject_path: Path = PYPROJECT,
    changelog_path: Path = CHANGELOG,
) -> PreparedRelease:
    _validate_version(version)
    current_version = read_version(pyproject_path)
    if version == current_version:
        raise ValueError(f"Version {version} already matches pyproject.toml")

    changelog = changelog_path.read_text(encoding="utf-8")
    unreleased_match = UNRELEASED_RE.search(changelog)
    if not unreleased_match:
        raise ValueError("Could not find [Unreleased] section in CHANGELOG.md")
    if re.search(rf"(?m)^## \[{re.escape(version)}\] - ", changelog):
        raise ValueError(f"CHANGELOG.md already contains a section for {version}")

    chosen_date = release_date or date.today().isoformat()
    unreleased_body = _normalize_body(unreleased_match.group("body"))
    if not unreleased_body:
        raise ValueError("CHANGELOG.md [Unreleased] section is empty")
    if _is_placeholder_only_unreleased(unreleased_body):
        raise ValueError("CHANGELOG.md [Unreleased] section only contains empty placeholders")

    new_unreleased = f"## [Unreleased]\n\n{EMPTY_UNRELEASED_TEMPLATE}\n"
    new_release = f"## [{version}] - {chosen_date}\n\n{unreleased_body}"
    updated_changelog = (
        changelog[: unreleased_match.start()]
        + new_unreleased
        + new_release
        + changelog[unreleased_match.end() :]
    )
    # Normalize any triple-newline seams created by replacement.
    updated_changelog = re.sub(r"\n{4,}", "\n\n\n", updated_changelog)

    write_version(version, pyproject_path)
    changelog_path.write_text(updated_changelog, encoding="utf-8")
    return PreparedRelease(version=version, release_date=chosen_date)


def extract_release_notes(version: str, changelog_path: Path = CHANGELOG) -> str:
    changelog = changelog_path.read_text(encoding="utf-8")
    for match in RELEASE_SECTION_RE.finditer(changelog):
        if match.group("version") == version:
            body = _normalize_body(match.group("body"))
            if not body:
                raise ValueError(f"Release {version} has no notes in CHANGELOG.md")
            return f"## [{version}] - {match.group('date')}\n\n{body}"
    raise ValueError(f"Could not find CHANGELOG section for {version}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Release helpers for familiar-ai")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("version", help="Print the current project version")

    prepare_cmd = sub.add_parser(
        "prepare", help="Prepare a release by updating version + changelog"
    )
    prepare_cmd.add_argument("version", help="Release version (X.Y.Z)")
    prepare_cmd.add_argument(
        "--date",
        dest="release_date",
        default="",
        help="Release date in YYYY-MM-DD format (default: today)",
    )

    notes_cmd = sub.add_parser("notes", help="Print release notes for a version")
    notes_cmd.add_argument("version", help="Release version (X.Y.Z)")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "version":
        print(read_version())
        return 0

    if args.command == "prepare":
        prepared = prepare_release(args.version, release_date=args.release_date or None)
        print(f"Prepared release {prepared.version} ({prepared.release_date})")
        return 0

    if args.command == "notes":
        print(extract_release_notes(args.version), end="")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
