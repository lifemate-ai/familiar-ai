# Repository Guidelines

## Project Structure & Module Organization
- `src/familiar_agent/`: main application code. Key modules include `main.py` (entry point), `agent.py` (core loop), `tools/` (tool integrations), and `gui.py` / `tui.py` (interfaces).
- `tests/`: pytest-based test suite. Follow existing `test_*.py` organization.
- `benchmarks/`: benchmark scenarios and prompt sets.
- `scripts/`: maintenance and automation scripts.
- `persona-template/` and `readme-l10n/`: persona starter files and localized READMEs.
- `dev/`: local helper commands for development workflows.

## Build, Test, and Development Commands
- `uv sync`: install project and dev dependencies from `pyproject.toml` / `uv.lock`.
- `./run.sh` (Linux/macOS/WSL2) or `run.bat` (Windows): start the app.
- `./run.sh --no-tui` or `run.bat --no-tui`: run in plain REPL mode.
- `uv run ruff check .`: lint Python code.
- `uv run ruff format .`: apply formatting.
- `uv run --group dev mypy src/familiar_agent`: static type checks.
- `uv run pytest -v`: run unit tests.
- `uvx pre-commit install`: install local hooks (Ruff + Ruff format + mypy).

## Coding Style & Naming Conventions
- Target Python 3.10+.
- Formatting/linting standard: Ruff, line length `100`.
- Naming rules: modules/functions/variables in `snake_case`, classes in `PascalCase`, constants in `UPPER_SNAKE_CASE`.
- Keep changes consistent with the existing async-first architecture (`asyncio` flows in agent/tool code).
- Add type hints for new or modified public-facing functions.

## Testing Guidelines
- Frameworks: `pytest` and `pytest-asyncio`.
- Test files: `tests/test_<feature>.py`; test names: `test_<behavior>`.
- Add tests with each behavior change, especially around tool integrations, MCP client behavior, and UI callbacks.
- There is no enforced coverage threshold in CI; maintain practical coverage for changed paths.

## Commit & Pull Request Guidelines
- Follow Conventional Commits, as used in history (for example: `feat(gui): ...`, `fix(windows): ...`).
- Keep PRs focused and single-purpose.
- Before opening a PR, run: Ruff check, Ruff format, mypy, and pytest.
- Update `CHANGELOG.md` under `[Unreleased]` when behavior changes.
- PR descriptions should include scope, testing performed, and linked issue context. Include screenshots/GIFs for GUI/TUI visual changes.
