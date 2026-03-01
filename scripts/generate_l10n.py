#!/usr/bin/env python3
"""Generate i18n translations (36 keys) and localized READMEs for 74 languages (ElevenLabs v3).

Usage:
    uv run scripts/generate_l10n.py                        # all 44 new languages
    uv run scripts/generate_l10n.py --lang es ko hi        # specific languages
    uv run scripts/generate_l10n.py --only-readme          # only README files
    uv run scripts/generate_l10n.py --only-i18n            # only _i18n.py keys
    uv run scripts/generate_l10n.py --api openai           # use OpenAI (default: anthropic)
    uv run scripts/generate_l10n.py --api gemini           # use Google Gemini

Output:
    - readme-l10n/README-{lang}.md  for each language
    - src/familiar_agent/_i18n.py   updated with new language entries
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
I18N_FILE = REPO_ROOT / "src" / "familiar_agent" / "_i18n.py"
README_EN = REPO_ROOT / "README.md"
README_L10N = REPO_ROOT / "readme-l10n"

# 68 new languages (beyond existing en, ja, zh, zh-TW, fr, de) — ElevenLabs v3 full coverage
NEW_LANGS: list[tuple[str, str]] = [
    ("es", "Spanish"),
    ("pt", "Portuguese (Brazilian)"),
    ("ru", "Russian"),
    ("ko", "Korean"),
    ("hi", "Hindi"),
    ("uk", "Ukrainian"),
    ("it", "Italian"),
    ("nl", "Dutch"),
    ("pl", "Polish"),
    ("tr", "Turkish"),
    ("vi", "Vietnamese"),
    ("th", "Thai"),
    ("id", "Indonesian"),
    ("ms", "Malay"),
    ("ar", "Arabic"),
    ("fa", "Persian"),
    ("he", "Hebrew"),
    ("bn", "Bengali"),
    ("ta", "Tamil"),
    ("te", "Telugu"),
    ("kn", "Kannada"),
    ("ml", "Malayalam"),
    ("pa", "Punjabi"),
    ("ur", "Urdu"),
    ("sw", "Swahili"),
    ("af", "Afrikaans"),
    ("sv", "Swedish"),
    ("no", "Norwegian"),
    ("da", "Danish"),
    ("fi", "Finnish"),
    ("cs", "Czech"),
    ("sk", "Slovak"),
    ("hu", "Hungarian"),
    ("ro", "Romanian"),
    ("el", "Greek"),
    ("bg", "Bulgarian"),
    ("hr", "Croatian"),
    ("sr", "Serbian"),
    ("ca", "Catalan"),
    ("fil", "Filipino"),
    ("lt", "Lithuanian"),
    ("lv", "Latvian"),
    ("et", "Estonian"),
    ("sl", "Slovenian"),
    # ElevenLabs v3 additional languages (74 total)
    ("hy", "Armenian"),
    ("as", "Assamese"),
    ("az", "Azerbaijani"),
    ("be", "Belarusian"),
    ("bs", "Bosnian"),
    ("ceb", "Cebuano"),
    ("ny", "Chichewa"),
    ("gl", "Galician"),
    ("ka", "Georgian"),
    ("gu", "Gujarati"),
    ("ha", "Hausa"),
    ("is", "Icelandic"),
    ("ga", "Irish"),
    ("jv", "Javanese"),
    ("kk", "Kazakh"),
    ("ky", "Kirghiz"),
    ("ln", "Lingala"),
    ("lb", "Luxembourgish"),
    ("mk", "Macedonian"),
    ("mr", "Marathi"),
    ("ne", "Nepali"),
    ("ps", "Pashto"),
    ("sd", "Sindhi"),
    ("so", "Somali"),
    ("cy", "Welsh"),
]

_I18N_PROMPT = """\
Translate these UI strings from English to {language_name} (language code: {code}).

Rules:
- Return ONLY a valid JSON object with the same keys
- Values must be translated into natural {language_name}
- Preserve {{placeholder}} variables EXACTLY as-is (e.g. {{log_path}}, {{direction}}, {{duration}})
- Preserve emoji characters exactly
- Use casual, friendly tone
- For "summary_lang": return the native name of {language_name} in {language_name}
- For "default_companion_name": return a common first name in {language_name} culture

English strings to translate:
{json_keys}
"""

_ADD_KEY_PROMPT = """\
Translate this single UI string from English to {language_name} (language code: {code}).

Rules:
- Return ONLY the translated string — no JSON wrapper, no quotes, no explanation
- Preserve emoji characters exactly
- Use casual, friendly tone (present progressive if it's a status label)

English string: {english_value}
"""

_README_PROMPT = """\
Translate this README.md from English to {language_name}.

Rules:
- Keep ALL Markdown formatting (headings, tables, code blocks, badges, links) exactly as-is
- Do NOT translate: code, variable names, flag names (PLATFORM, API_KEY etc), URLs, badge markdown
- Do NOT translate the project name "Familiar AI" or "familiar-ai"
- Do NOT translate command-line examples
- Keep the casual, friendly tone
- Replace the language switcher section at the top with just: "[→ English README](../README.md)"
- Output only the translated Markdown, nothing else

README.md:
{readme}
"""


def _extract_english_values() -> dict[str, str]:
    """Read _i18n.py and extract English values for all 36 keys."""
    # Import the module to get the dict safely
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from familiar_agent._i18n import _T  # noqa: PLC0415

    return {key: translations["en"] for key, translations in _T.items()}


def _read_current_translations() -> dict[str, dict[str, str]]:
    """Read current _T dict from _i18n.py."""
    sys.path.insert(0, str(REPO_ROOT / "src"))
    # Force fresh import
    if "familiar_agent._i18n" in sys.modules:
        del sys.modules["familiar_agent._i18n"]
    if "familiar_agent" in sys.modules:
        del sys.modules["familiar_agent"]
    from familiar_agent._i18n import _T  # noqa: PLC0415

    return dict(_T)


def _write_i18n_file(translations: dict[str, dict[str, str]]) -> None:
    """Write the updated _T dict back to _i18n.py."""
    original = I18N_FILE.read_text(encoding="utf-8")

    # Find the _T dict block: from "_T: dict[str, dict[str, str]] = {" to closing "}"
    # We'll replace only the _T dict content
    start_marker = "_T: dict[str, dict[str, str]] = {"
    start = original.index(start_marker)

    # Find the matching closing brace
    depth = 0
    end = start + len(start_marker) - 1
    for i, ch in enumerate(
        original[start + len(start_marker) - 1 :], start=start + len(start_marker) - 1
    ):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    # Build sorted language list: existing order + new langs alphabetically
    all_langs = sorted(
        {lang for entry in translations.values() for lang in entry.keys()},
        key=lambda x: (x not in ("en", "ja", "zh", "zh-tw", "fr", "de"), x),
    )

    # Reconstruct the _T dict as Python source
    # Use repr() for values to preserve emoji and Unicode correctly
    def _pyrepr(s: str) -> str:
        """Return a Python double-quoted string literal preserving Unicode/emoji."""
        # Use repr() then normalise to double quotes to match existing style
        r = repr(s)
        if r.startswith("'"):
            r = '"' + r[1:-1].replace('"', '\\"').replace("\\'", "'") + '"'
        return r

    lines = [f"{start_marker}"]
    for key, lang_map in translations.items():
        lines.append(f"    {_pyrepr(key)}: {{")
        for lang in all_langs:
            if lang in lang_map:
                val = lang_map[lang]
                lines.append(f"        {_pyrepr(lang)}: {_pyrepr(val)},")
        lines.append("    },")

    lines.append("}")
    new_t_block = "\n".join(lines)

    updated = original[:start] + new_t_block + original[end:]
    I18N_FILE.write_text(updated, encoding="utf-8")


async def _complete(client: object, api: str, prompt: str, max_tokens: int) -> str:
    """Unified completion call across OpenAI / Anthropic / Gemini."""
    if api == "openai":
        from openai import AsyncOpenAI  # noqa: PLC0415

        assert isinstance(client, AsyncOpenAI)
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""
    elif api == "anthropic":
        import anthropic as _ant  # noqa: PLC0415

        assert isinstance(client, _ant.AsyncAnthropic)
        resp = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text
    else:  # gemini via openai-compat
        from openai import AsyncOpenAI  # noqa: PLC0415

        assert isinstance(client, AsyncOpenAI)
        resp = await client.chat.completions.create(
            model="gemini-1.5-flash",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""


async def _translate_i18n(
    client: object,
    api: str,
    code: str,
    language_name: str,
    english_values: dict[str, str],
) -> dict[str, str] | None:
    """Ask LLM to translate all 36 i18n keys. Returns dict of translations."""
    json_keys = json.dumps(english_values, ensure_ascii=False, indent=2)
    prompt = _I18N_PROMPT.format(language_name=language_name, code=code, json_keys=json_keys)
    try:
        raw = await _complete(client, api, prompt, 2048)
        raw = raw.strip()
        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except Exception as e:
        print(f"  [i18n ERROR {code}] {e}", file=sys.stderr)
        return None


async def _translate_readme(
    client: object,
    api: str,
    code: str,
    language_name: str,
    readme_en: str,
) -> str | None:
    """Translate README.md to target language."""
    prompt = _README_PROMPT.format(language_name=language_name, readme=readme_en)
    try:
        raw = await _complete(client, api, prompt, 8192)
        return raw.strip()
    except Exception as e:
        print(f"  [README ERROR {code}] {e}", file=sys.stderr)
        return None


async def _process_lang(
    sem: asyncio.Semaphore,
    client: object,
    api: str,
    code: str,
    language_name: str,
    english_values: dict[str, str],
    readme_en: str,
    only_readme: bool,
    only_i18n: bool,
) -> tuple[str, dict[str, str] | None, str | None]:
    """Process one language: i18n + README translation under semaphore."""
    async with sem:
        print(f"  → {language_name} ({code})", flush=True)
        i18n_result = None
        readme_result = None

        if not only_readme:
            i18n_result = await _translate_i18n(client, api, code, language_name, english_values)

        if not only_i18n:
            readme_result = await _translate_readme(client, api, code, language_name, readme_en)

        return code, i18n_result, readme_result


async def _translate_single_key(
    client: object,
    api: str,
    key: str,
    english_value: str,
    code: str,
    language_name: str,
) -> tuple[str, str] | None:
    """Translate a single i18n key for one language. Returns (code, translated_value)."""
    prompt = _ADD_KEY_PROMPT.format(
        language_name=language_name, code=code, english_value=english_value
    )
    try:
        raw = await _complete(client, api, prompt, 128)
        return code, raw.strip().strip('"').strip("'")
    except Exception as e:
        print(f"  [ADD_KEY ERROR {code}] {e}", file=sys.stderr)
        return None


async def main_async_add_key(
    key: str,
    english_value: str,
    api: str,
) -> None:
    """Add a single new key to _i18n.py across all 74 languages."""
    # All languages: existing 6 + 68 new (en is the source, skip it)
    existing_non_en = [
        ("ja", "Japanese"),
        ("zh", "Chinese (Simplified)"),
        ("zh-tw", "Chinese (Traditional)"),
        ("fr", "French"),
        ("de", "German"),
    ]
    all_langs = existing_non_en + NEW_LANGS

    if api == "openai":
        from openai import AsyncOpenAI  # noqa: PLC0415

        client: object = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    elif api == "gemini":
        from openai import AsyncOpenAI  # noqa: PLC0415

        client = AsyncOpenAI(
            api_key=os.environ["GEMINI_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
    else:
        import anthropic as _ant  # noqa: PLC0415

        client = _ant.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    sem = asyncio.Semaphore(5)
    print(f"Translating key '{key}' = '{english_value}' into {len(all_langs)} languages...")

    async def _bounded(code: str, lang_name: str) -> tuple[str, str] | None:
        async with sem:
            return await _translate_single_key(client, api, key, english_value, code, lang_name)

    results = await asyncio.gather(*[_bounded(c, ln) for c, ln in all_langs])

    current = _read_current_translations()
    translations: dict[str, str] = {"en": english_value}
    for r in results:
        if r:
            translations[r[0]] = r[1]

    current[key] = translations
    _write_i18n_file(current)
    print(f"  ✓ Added '{key}' with {len(translations)} language entries to _i18n.py")

    if hasattr(client, "close"):
        await client.close()


async def main_async(
    target_langs: list[tuple[str, str]],
    only_readme: bool,
    only_i18n: bool,
    api: str,
) -> None:
    README_L10N.mkdir(exist_ok=True)

    if api == "openai":
        from openai import AsyncOpenAI  # noqa: PLC0415

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY not set", file=sys.stderr)
            sys.exit(1)
        client: object = AsyncOpenAI(api_key=api_key)
    elif api == "gemini":
        from openai import AsyncOpenAI  # noqa: PLC0415

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not set", file=sys.stderr)
            sys.exit(1)
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
    else:  # anthropic
        import anthropic as _ant  # noqa: PLC0415

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
            sys.exit(1)
        client = _ant.AsyncAnthropic(api_key=api_key)

    english_values = _extract_english_values()
    readme_en = README_EN.read_text(encoding="utf-8")

    # Load current translations to merge into
    current = _read_current_translations()

    # Semaphore: max 5 concurrent API calls to avoid rate limits
    sem = asyncio.Semaphore(5)

    print(f"Processing {len(target_langs)} languages using {api} API...")
    tasks = [
        _process_lang(
            sem, client, api, code, lang, english_values, readme_en, only_readme, only_i18n
        )
        for code, lang in target_langs
    ]
    results = await asyncio.gather(*tasks)

    # Merge i18n results into current translations
    i18n_updates: dict[str, tuple[str, dict[str, str]]] = {}
    for code, i18n_result, readme_result in results:
        if i18n_result:
            i18n_updates[code] = i18n_result
        if readme_result:
            out_path = README_L10N / f"README-{code}.md"
            out_path.write_text(readme_result + "\n", encoding="utf-8")
            print(f"  ✓ readme-l10n/README-{code}.md")

    if i18n_updates and not only_readme:
        # Merge into current translations dict
        for key in current:
            for code, translations in i18n_updates.items():
                if key in translations:
                    current[key][code] = translations[key]

        _write_i18n_file(current)
        print(f"  ✓ _i18n.py updated with {len(i18n_updates)} new languages")
        # Validate: re-import and check
        for code in i18n_updates:
            if code not in current.get("banner_subtitle", {}):
                print(f"  ⚠ WARNING: {code} missing from banner_subtitle", file=sys.stderr)

    if hasattr(client, "close"):
        await client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate i18n + README localizations.")
    parser.add_argument(
        "--lang",
        nargs="+",
        help="Language codes to process (default: all 68 new languages)",
    )
    parser.add_argument(
        "--only-readme",
        action="store_true",
        help="Only generate README files, skip i18n key translation",
    )
    parser.add_argument(
        "--only-i18n",
        action="store_true",
        help="Only update _i18n.py, skip README generation",
    )
    parser.add_argument(
        "--add-key",
        metavar="KEY=english_value",
        help="Add a single new i18n key across all 74 languages (e.g. --add-key action_recall='💭 recalling...')",
    )
    parser.add_argument(
        "--api",
        choices=["anthropic", "openai", "gemini"],
        default="anthropic",
        help="LLM backend to use for translation (default: anthropic)",
    )
    args = parser.parse_args()

    if args.add_key:
        if "=" not in args.add_key:
            print("Error: --add-key requires KEY=value format", file=sys.stderr)
            sys.exit(1)
        key, english_value = args.add_key.split("=", 1)
        asyncio.run(main_async_add_key(key.strip(), english_value.strip(), args.api))
        print("Done!")
        return

    lang_map = dict(NEW_LANGS)
    if args.lang:
        target_langs = []
        for code in args.lang:
            if code not in lang_map:
                print(f"Error: unknown language code '{code}'", file=sys.stderr)
                print(f"Available: {', '.join(lang_map)}", file=sys.stderr)
                sys.exit(1)
            target_langs.append((code, lang_map[code]))
    else:
        target_langs = NEW_LANGS

    asyncio.run(main_async(target_langs, args.only_readme, args.only_i18n, args.api))
    print("Done!")


if __name__ == "__main__":
    main()
