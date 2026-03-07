"""Tests for Phase 6-3 _i18n.py refactor: _T dict → locales/{lang}.json.

TDD: written before implementation.
All tests verify that the public _t() API is unchanged and JSON locale files exist.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# The locales directory should be next to _i18n.py
LOCALES_DIR = Path(__file__).parent.parent / "src" / "familiar_agent" / "locales"

# All 84 keys that must be present in every locale
from familiar_agent._i18n import _T  # noqa: E402 — import after path setup

ALL_KEYS = list(_T.keys())


# ---------------------------------------------------------------------------
# Tests: locales directory and JSON files exist
# ---------------------------------------------------------------------------


def test_locales_dir_exists():
    """locales/ directory exists next to _i18n.py."""
    assert LOCALES_DIR.is_dir(), f"Expected {LOCALES_DIR} to be a directory"


def test_en_json_exists():
    """locales/en.json is mandatory — it is the fallback locale."""
    assert (LOCALES_DIR / "en.json").exists()


def test_ja_json_exists():
    """locales/ja.json exists (primary non-English locale for this project)."""
    assert (LOCALES_DIR / "ja.json").exists()


def test_en_json_has_all_keys():
    """en.json contains all 84 translation keys."""
    data = json.loads((LOCALES_DIR / "en.json").read_text(encoding="utf-8"))
    missing = [k for k in ALL_KEYS if k not in data]
    assert not missing, f"en.json is missing keys: {missing}"


def test_ja_json_has_all_keys():
    """ja.json contains all 84 translation keys."""
    data = json.loads((LOCALES_DIR / "ja.json").read_text(encoding="utf-8"))
    missing = [k for k in ALL_KEYS if k not in data]
    assert not missing, f"ja.json is missing keys: {missing}"


def test_locale_files_are_valid_json():
    """Every .json file in locales/ is valid JSON."""
    json_files = list(LOCALES_DIR.glob("*.json"))
    assert json_files, "No JSON files found in locales/"
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            pytest.fail(f"{path.name} is not valid JSON: {exc}")


def test_locale_file_count():
    """At least 10 locale files exist (en + major world languages)."""
    count = len(list(LOCALES_DIR.glob("*.json")))
    assert count >= 10, f"Expected ≥10 locale files, found {count}"


# ---------------------------------------------------------------------------
# Tests: _t() API unchanged
# ---------------------------------------------------------------------------


def test_t_returns_nonempty_for_all_keys_in_en():
    """_t() returns a non-empty string for every key when locale=en."""
    import os
    from unittest.mock import patch

    with patch.dict(os.environ, {"LANG": "en_US.UTF-8"}):
        # Re-import to pick up the patched env
        import importlib
        import familiar_agent._i18n as i18n_mod

        importlib.reload(i18n_mod)
        _t = i18n_mod._t
        for key in ALL_KEYS:
            # Keys with format placeholders need dummy kwargs — skip them here
            lang_dict = _T[key]
            if "{" in lang_dict.get("en", ""):
                continue
            result = _t(key)
            assert result, f"_t('{key}') returned empty string"


def test_t_returns_same_english_strings_as_before():
    """_t() returns the same English text as the original _T dict."""
    import os
    from unittest.mock import patch

    with patch.dict(os.environ, {"LANG": "en_US.UTF-8"}):
        import importlib
        import familiar_agent._i18n as i18n_mod

        importlib.reload(i18n_mod)
        _t = i18n_mod._t
        for key in ALL_KEYS:
            lang_dict = _T[key]
            en_text = lang_dict.get("en", "")
            if "{" in en_text:
                continue  # skip format keys
            assert _t(key) == en_text, f"_t('{key}') mismatch"


def test_t_format_kwargs_work():
    """_t() correctly applies format kwargs for keys with placeholders."""
    import os
    from unittest.mock import patch

    with patch.dict(os.environ, {"LANG": "en_US.UTF-8"}):
        import importlib
        import familiar_agent._i18n as i18n_mod

        importlib.reload(i18n_mod)
        _t = i18n_mod._t
        # "desire_prompt_greet_companion" uses {companion} placeholder
        result = _t("desire_prompt_greet_companion", companion="Alice")
        assert "Alice" in result


def test_t_japanese_works():
    """_t() returns Japanese text when LANG=ja."""
    import os
    from unittest.mock import patch

    with patch.dict(os.environ, {"LANG": "ja_JP.UTF-8"}):
        import importlib
        import familiar_agent._i18n as i18n_mod

        importlib.reload(i18n_mod)
        _t = i18n_mod._t
        result = _t("repl_goodbye")
        # Japanese strings use multi-byte chars; just check it's different from English
        en_text = _T["repl_goodbye"]["en"]
        ja_text = _T["repl_goodbye"]["ja"]
        assert result == ja_text, f"Expected Japanese string, got: {result!r}"
        assert result != en_text


def test_t_unknown_lang_falls_back_to_en():
    """Unknown LANG falls back to English strings."""
    import os
    from unittest.mock import patch

    with patch.dict(os.environ, {"LANG": "xx_XX.UTF-8"}):
        import importlib
        import familiar_agent._i18n as i18n_mod

        importlib.reload(i18n_mod)
        _t = i18n_mod._t
        result = _t("repl_goodbye")
        assert result == _T["repl_goodbye"]["en"]
