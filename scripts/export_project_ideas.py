#!/usr/bin/env python3
"""Export markdown-based project ideas into repo-ready folders with starter code."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
LANGUAGE_ALIASES = {
    "py": "python",
    "python3": "python",
    "js": "javascript",
    "ts": "typescript",
    "golang": "go",
}
STARTER_FILES = {
    "python": "main.py",
    "javascript": "index.js",
    "typescript": "index.ts",
    "go": "main.go",
    "rust": "main.rs",
}
MAX_UNIQUE_SUFFIX_ATTEMPTS = 1000


def parse_frontmatter(markdown: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(markdown)
    if not match:
        return {}, markdown
    body = markdown[match.end() :]
    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip().lower()] = value.strip().strip('"').strip("'")
    return metadata, body


def extract_title(content: str) -> str:
    match = TITLE_RE.search(content)
    if match:
        return match.group(1).strip()
    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return "untitled-idea"


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value or "untitled-idea"


def normalize_language(value: str) -> str:
    if not value:
        return "python"
    normalized = value.strip().lower()
    return LANGUAGE_ALIASES.get(normalized, normalized)


def starter_code(title: str, language: str, description: str) -> str:
    todo_text = f"TODO: implement {description}"
    todo_quoted = json.dumps(todo_text)
    if language == "python":
        return (
            f'"""Starter code for: {title}"""\n\n'
            "def main() -> None:\n"
            f"    print({todo_quoted})\n\n"
            'if __name__ == "__main__":\n'
            "    main()\n"
        )
    if language == "javascript":
        return f"// Starter code for: {title}\nconsole.log({todo_quoted});\n"
    if language == "typescript":
        return (
            f"// Starter code for: {title}\n"
            "function main(): void {\n"
            f"  console.log({todo_quoted});\n"
            "}\n\n"
            "main();\n"
        )
    if language == "go":
        return (
            "package main\n\n"
            'import "fmt"\n\n'
            "func main() {\n"
            f"    fmt.Println({todo_quoted})\n"
            "}\n"
        )
    if language == "rust":
        return f"fn main() {{\n    println!({todo_quoted});\n}}\n"
    return f"Starter template for {title}\nTODO: implement {description}\n"


def iter_markdown_files(source: Path) -> Iterable[Path]:
    if source.is_file() and source.suffix.lower() == ".md":
        yield source
        return
    for path in source.rglob("*.md"):
        if path.is_file():
            yield path


def unique_destination(output_root: Path, slug: str) -> Path:
    destination = output_root / slug
    if not destination.exists():
        return destination
    for suffix in range(2, 2 + MAX_UNIQUE_SUFFIX_ATTEMPTS):
        candidate = output_root / f"{slug}-{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(
        "Unable to find a unique output directory for slug "
        f"'{slug}' after checking {MAX_UNIQUE_SUFFIX_ATTEMPTS} sequential suffixes."
    )


def export_idea(md_file: Path, output_root: Path, overwrite: bool) -> Path:
    raw = md_file.read_text(encoding="utf-8")
    metadata, content = parse_frontmatter(raw)
    title = metadata.get("title") or extract_title(content)
    language = normalize_language(metadata.get("language", "python"))
    description = metadata.get("description") or title
    base_slug = slugify(title)
    destination = output_root / base_slug
    if destination.exists() and not overwrite:
        destination = unique_destination(output_root, base_slug)

    destination.mkdir(parents=True, exist_ok=True)
    starter_name = STARTER_FILES.get(language, "starter.txt")
    starter_path = destination / starter_name
    readme_path = destination / "README.md"
    idea_copy_path = destination / "idea.md"

    starter_path.write_text(starter_code(title, language, description), encoding="utf-8")
    readme_path.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                f"- Source file: `{md_file.name}`",
                f"- Language: `{language}`",
                "",
                "## Description",
                description,
                "",
                "## Next steps",
                "- Refine scope and acceptance criteria",
                "- Break down implementation milestones",
                "- Replace starter code with a working prototype",
                "",
            ]
        ),
        encoding="utf-8",
    )
    idea_copy_path.write_text(raw, encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export Obsidian/Markdown project ideas into folders with starter code."
    )
    parser.add_argument("--source", required=True, help="Markdown file or folder to import.")
    parser.add_argument(
        "--output",
        default="project_ideas",
        help="Output directory where generated project folders will be stored.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow writing into existing output folders.",
    )
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()

    if not source.exists():
        raise FileNotFoundError(f"Source path does not exist: {source}")

    output.mkdir(parents=True, exist_ok=True)
    exported = []
    for md_file in iter_markdown_files(source):
        exported.append(export_idea(md_file, output, overwrite=args.overwrite))

    if not exported:
        print(f"No markdown files found in: {source}")
        return

    print(f"Exported {len(exported)} idea(s) into {output}")
    for path in exported:
        print(f"- {path}")


if __name__ == "__main__":
    main()
