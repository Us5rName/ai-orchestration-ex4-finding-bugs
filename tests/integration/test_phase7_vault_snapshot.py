"""Phase 7 Obsidian vault snapshot regression tests."""

import re
from pathlib import Path

VAULT_ROOT = Path("obsidian")
WIKILINK_RE = re.compile(r"\[\[(?P<target>[^]|#]+)")


def test_phase7_vault_contains_required_navigation_notes() -> None:
    """Committed vault must include index, hot area, and entity notes."""
    assert (VAULT_ROOT / "index.md").is_file()
    assert (VAULT_ROOT / "hot.md").is_file()
    assert len(list((VAULT_ROOT / "notes").glob("*.md"))) >= 2


def test_phase7_vault_wikilinks_resolve() -> None:
    """All Obsidian wikilinks in generated vault notes must resolve."""
    missing: list[str] = []
    for note in VAULT_ROOT.rglob("*.md"):
        for match in WIKILINK_RE.finditer(note.read_text(encoding="utf-8")):
            target = match.group("target")
            if not _resolve_wikilink(target).is_file():
                missing.append(f"{note}: {target}")

    assert missing == []


def _resolve_wikilink(target: str) -> Path:
    path = VAULT_ROOT / f"{target}.md"
    if path.is_file():
        return path
    return VAULT_ROOT / "notes" / f"{target}.md"
