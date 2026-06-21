"""Phase 7 post-investigation vault updates."""

from __future__ import annotations

import json
from pathlib import Path

SECTION_MARKER = "<!-- phase7-investigation-summary -->"


def update_phase7_vault(vault_path: Path, investigation_result_path: Path) -> dict[str, Path]:
    """Write post-investigation notes and update `hot.md` with fix context."""
    vault_path.mkdir(parents=True, exist_ok=True)
    result = json.loads(investigation_result_path.read_text(encoding="utf-8"))
    paths = {
        "investigation": vault_path / "phase7-investigation.md",
        "before_after": vault_path / "phase7-before-after.md",
        "hot": vault_path / "hot.md",
    }
    paths["investigation"].write_text(_investigation_note(result), encoding="utf-8")
    paths["before_after"].write_text(_before_after_note(result), encoding="utf-8")
    _upsert_hot_summary(paths["hot"])
    return paths


def _investigation_note(result: dict[str, object]) -> str:
    return "\n".join([
        "# Phase 7 Investigation",
        "",
        "## Root Cause",
        "",
        str(result.get("root_cause", "")),
        "",
        "## Linked Evidence",
        "",
        "- [[phase7-before-after|Before/after vault note]]",
        "- [[notes/snippets_foobar_foo|foo() graph node]]",
        "- [[hot|Hot area]]",
        "",
    ])


def _before_after_note(result: dict[str, object]) -> str:
    return "\n".join([
        "# Phase 7 Before/After",
        "",
        "## Before",
        "",
        "`foo(bar=[])` reused the same list across calls.",
        "",
        "## After",
        "",
        "`foo(bar=None)` allocates a fresh list when the caller does not pass one.",
        "",
        "## Verification",
        "",
        f"- Passed: `{result.get('test_results', {}).get('passed')}`",
        "- Report: `reports/bug_analysis.md`",
        "",
    ])


def _upsert_hot_summary(hot_path: Path) -> None:
    existing = hot_path.read_text(encoding="utf-8") if hot_path.exists() else "# Hot Area\n"
    base = existing.split(SECTION_MARKER)[0].rstrip()
    summary = f"""

{SECTION_MARKER}
## Phase 7 Fix Summary

- Root cause note: [[phase7-investigation]]
- Before/after note: [[phase7-before-after]]
- Primary fixed symbol: [[notes/snippets_foobar_foo|foo()]]
"""
    hot_path.write_text(f"{base}{summary}", encoding="utf-8")
