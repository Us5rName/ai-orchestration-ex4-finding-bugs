"""Check that plan-wiki/Home.md and todo-wiki/Home.md are up-to-date.

Exits with code 1 and a diff summary if wikis are out of sync with canonical docs.
Run: uv run python scripts/check_docs_sync.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
PLAN_HOME = ROOT / "docs" / "plan-wiki" / "Home.md"
TODO_HOME = ROOT / "docs" / "todo-wiki" / "Home.md"
GEN_SCRIPT = ROOT / "scripts" / "generate_doc_wikis.py"


def check_file_sync(existing: Path, label: str) -> bool:
    """Return True if the file matches what generate_doc_wikis.py would produce."""
    if not existing.exists():
        print(f"MISSING: {label} ({existing})")
        return False

    with tempfile.TemporaryDirectory() as tmp:
        import shutil

        tmp_path = Path(tmp)
        # Copy docs dir into temp, run generator, compare Home.md
        tmp_docs = tmp_path / "docs"
        shutil.copytree(ROOT / "docs", tmp_docs)
        tmp_scripts = tmp_path / "scripts"
        tmp_scripts.mkdir()
        shutil.copy(GEN_SCRIPT, tmp_scripts / "generate_doc_wikis.py")

        result = subprocess.run(
            [sys.executable, str(tmp_scripts / "generate_doc_wikis.py")],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Generator failed: {result.stderr}")
            return False

        if label.startswith("plan"):
            generated = tmp_docs / "plan-wiki" / "Home.md"
        else:
            generated = tmp_docs / "todo-wiki" / "Home.md"

        existing_text = existing.read_text(encoding="utf-8")
        generated_text = generated.read_text(encoding="utf-8") if generated.exists() else ""

        if existing_text == generated_text:
            print(f"OK: {label}")
            return True
        else:
            print(f"OUT OF SYNC: {label}")
            print("  Run: uv run python scripts/generate_doc_wikis.py")
            return False


def main() -> None:
    """Check both wiki Home files."""
    ok_plan = check_file_sync(PLAN_HOME, "plan-wiki/Home.md")
    ok_todo = check_file_sync(TODO_HOME, "todo-wiki/Home.md")
    if ok_plan and ok_todo:
        print("All wikis are in sync.")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
