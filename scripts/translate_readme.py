"""Translate README.md (English) → README-ja.md (Japanese) using Claude."""

import os
import sys
from pathlib import Path

import anthropic

PROMPT = """\
You are translating a README.md for an open-source project called "familiar-ai".

Rules:
- Translate English → Japanese
- Keep all Markdown formatting (headings, tables, code blocks, badges, links) exactly as-is
- Do NOT translate: code, variable names, command names, URLs, badge markdown
- Do NOT translate the project name "familiar-ai"
- Use natural Japanese — not literal machine translation
- Keep the casual, friendly tone of the original
- Output only the translated Markdown, nothing else

README.md to translate:
{readme}
"""


def main() -> None:
    repo_root = Path(__file__).parent.parent
    readme_en = (repo_root / "README.md").read_text(encoding="utf-8")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": PROMPT.format(readme=readme_en)}],
    )

    translated = response.content[0].text.strip()
    output_path = repo_root / "README-ja.md"
    output_path.write_text(translated + "\n", encoding="utf-8")
    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
