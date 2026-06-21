"""Generate docs/plan-wiki/ and docs/todo-wiki/ from canonical documents.

GENERATED CONTENT IS PLACED IN wiki subdirectories.
The canonical sources are docs/PLAN.md and docs/TODO.md.
Run: uv run python scripts/generate_doc_wikis.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PLAN_SRC = ROOT / "docs" / "PLAN.md"
TODO_SRC = ROOT / "docs" / "TODO.md"
PLAN_WIKI = ROOT / "docs" / "plan-wiki"
TODO_WIKI = ROOT / "docs" / "todo-wiki"

HEADER = "<!-- GENERATED FROM CANONICAL DOCUMENTATION — DO NOT EDIT DIRECTLY -->\n\n"


def _extract_h2_sections(text: str) -> list[tuple[str, str]]:
    """Return list of (heading, body) for each H2 section."""
    pattern = re.compile(r"^## (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    sections: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        heading = m.group(1).strip()
        body = text[m.end() : end].strip()
        sections.append((heading, body))
    return sections


def _slug(heading: str) -> str:
    """Convert heading to filename slug."""
    return re.sub(r"[^a-zA-Z0-9]+", "-", heading).strip("-")


def generate_plan_wiki() -> None:
    """Regenerate plan-wiki Home.md from PLAN.md section headings."""
    text = PLAN_SRC.read_text(encoding="utf-8")
    sections = _extract_h2_sections(text)
    home_lines = [HEADER, "# PLAN Wiki — Home\n\n"]
    home_lines.append("Navigation index generated from `docs/PLAN.md`.\n\n")
    home_lines.append("| # | Section |\n|---|---|\n")
    for idx, (heading, _body) in enumerate(sections, 1):
        slug = _slug(heading)
        home_lines.append(f"| {idx} | [{heading}](./plan-{idx:02d}-{slug}.md) |\n")
    (PLAN_WIKI / "Home.md").write_text("".join(home_lines), encoding="utf-8")
    print(f"plan-wiki/Home.md updated ({len(sections)} sections)")


def generate_todo_wiki() -> None:
    """Regenerate todo-wiki Home.md from TODO.md section headings."""
    text = TODO_SRC.read_text(encoding="utf-8")
    sections = _extract_h2_sections(text)
    home_lines = [HEADER, "# TODO Wiki — Home\n\n"]
    home_lines.append("Navigation index generated from `docs/TODO.md`.\n\n")
    home_lines.append("| # | Section |\n|---|---|\n")
    for idx, (heading, _body) in enumerate(sections, 1):
        slug = _slug(heading)
        home_lines.append(f"| {idx} | [{heading}](./todo-{idx:02d}-{slug}.md) |\n")
    (TODO_WIKI / "Home.md").write_text("".join(home_lines), encoding="utf-8")
    print(f"todo-wiki/Home.md updated ({len(sections)} sections)")


def main() -> None:
    """Entry point."""
    if not PLAN_SRC.exists():
        print(f"ERROR: {PLAN_SRC} not found", file=sys.stderr)
        sys.exit(1)
    if not TODO_SRC.exists():
        print(f"ERROR: {TODO_SRC} not found", file=sys.stderr)
        sys.exit(1)
    generate_plan_wiki()
    generate_todo_wiki()
    print("Wiki generation complete.")


if __name__ == "__main__":
    main()
