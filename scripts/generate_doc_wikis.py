"""Generate wiki pages from canonical documentation.

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

HEADER = "<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->\n\n"


def _extract_h2_sections(text: str) -> list[tuple[str, str]]:
    """Return list of (heading, body) for each H2 section."""
    pattern = re.compile(r"^## (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    sections: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        heading = m.group(1).strip()
        if heading == "Table of Contents":
            continue
        body = text[m.end() : end].strip()
        sections.append((heading, body))
    return sections


def _slug(heading: str) -> str:
    """Convert heading to filename slug."""
    plain = re.sub(r"^\d+\.\s+", "", heading)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", plain).strip("-")
    aliases = {
        "Architectural-Decision-Records-ADRs": "ADRs",
        "UML-Activity-Diagram-Main-Investigation-Flow": "UML-Activity-Diagram",
        "Project-Structure-Final": "Project-Structure",
        "Phase-6-Comparison-Service": "Phase-6-Comparison",
        "Phase-7-End-to-End-Execution": "Phase-7-End-to-End",
        "Task-Dependency-Summary": "Dependency-Summary",
    }
    return aliases.get(slug, slug)


def _write_wiki(source: Path, out_dir: Path, label: str) -> None:
    """Regenerate Home.md and one page per H2 section."""
    text = source.read_text(encoding="utf-8")
    sections = _extract_h2_sections(text)
    home_lines = [HEADER, f"# {label.upper()} Wiki - Home\n\n"]
    home_lines.append(f"Navigation index generated from `{source.relative_to(ROOT)}`.\n\n")
    home_lines.append("| # | Section |\n|---|---|\n")
    for idx, (heading, _body) in enumerate(sections, 1):
        slug = _slug(heading)
        page = f"{idx:02d}-{slug}.md"
        home_lines.append(f"| {idx} | [{heading}](./{page}) |\n")
        body = _section_page(label, heading, _body)
        (out_dir / page).write_text(body, encoding="utf-8")
    (out_dir / "Home.md").write_text("".join(home_lines), encoding="utf-8")
    print(f"{label}-wiki updated ({len(sections)} sections)")


def _section_page(label: str, heading: str, body: str) -> str:
    """Return a generated section page."""
    return f"{HEADER}# {heading}\n\n[Back to Home](./Home.md)\n\n{body}\n"


def generate_plan_wiki() -> None:
    """Regenerate plan-wiki from PLAN.md."""
    _write_wiki(PLAN_SRC, PLAN_WIKI, "plan")


def generate_todo_wiki() -> None:
    """Regenerate todo-wiki from TODO.md."""
    _write_wiki(TODO_SRC, TODO_WIKI, "todo")


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
