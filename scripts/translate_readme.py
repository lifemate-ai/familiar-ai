"""Translate README.md (English) → README-{lang}.md using Claude."""

import argparse
import os
import sys
from pathlib import Path

import anthropic

LANGUAGES = {
    "ja": ("Japanese", "日本語"),
    "zh": ("Simplified Chinese", "简体中文"),
    "fr": ("French", "Français"),
    "de": ("German", "Deutsch"),
}

PROMPT = """\
You are translating a README.md for an open-source project called "Familiar AI".

Target language: {language_name}

Rules:
- Translate English → {language_name}
- Keep all Markdown formatting (headings, tables, code blocks, badges, links) exactly as-is
- Do NOT translate: code, variable names, command names, URLs, badge markdown
- Do NOT translate the project name "Familiar AI" or "familiar-ai"
- Use natural {language_name} — not literal machine translation
- Keep the casual, friendly tone of the original
- Output only the translated Markdown, nothing else

README.md to translate:
{readme}
"""


def translate(client: anthropic.Anthropic, readme_en: str, lang: str) -> str:
    language_name, _ = LANGUAGES[lang]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": PROMPT.format(language_name=language_name, readme=readme_en),
            }
        ],
    )
    return response.content[0].text.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate README.md into multiple languages.")
    parser.add_argument(
        "--lang",
        choices=list(LANGUAGES.keys()),
        help="Target language code (default: all)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    readme_en = (repo_root / "README.md").read_text(encoding="utf-8")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    targets = [args.lang] if args.lang else list(LANGUAGES.keys())

    for lang in targets:
        _, native_name = LANGUAGES[lang]
        print(f"Translating → {native_name} ({lang})...", flush=True)
        translated = translate(client, readme_en, lang)
        output_path = repo_root / f"README-{lang}.md"
        output_path.write_text(translated + "\n", encoding="utf-8")
        print(f"  Written to {output_path}")


if __name__ == "__main__":
    main()
