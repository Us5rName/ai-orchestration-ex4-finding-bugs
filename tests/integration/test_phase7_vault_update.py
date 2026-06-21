"""Phase 7 post-investigation vault update tests."""

import shutil
from pathlib import Path

from ex04.phase7 import update_phase7_vault

RESULT = Path("artifacts/runs/phase7-investigation/result.json")


def test_phase7_vault_update_is_idempotent(tmp_path: Path) -> None:
    """Vault update should create notes and avoid duplicate hot summaries."""
    vault = tmp_path / "obsidian"
    shutil.copytree("obsidian", vault)

    update_phase7_vault(vault, RESULT)
    update_phase7_vault(vault, RESULT)

    hot = (vault / "hot.md").read_text(encoding="utf-8")
    assert hot.count("<!-- phase7-investigation-summary -->") == 1
    assert (vault / "phase7-investigation.md").is_file()
    assert (vault / "phase7-before-after.md").is_file()


def test_phase7_committed_vault_update_is_present() -> None:
    """Committed vault must include post-investigation findings."""
    investigation = Path("obsidian/phase7-investigation.md").read_text(encoding="utf-8")
    before_after = Path("obsidian/phase7-before-after.md").read_text(encoding="utf-8")
    hot = Path("obsidian/hot.md").read_text(encoding="utf-8")

    assert "mutable default argument" in investigation
    assert "foo(bar=None)" in before_after
    assert "[[phase7-investigation]]" in hot
