"""Check that generated wiki pages are up-to-date.

Exits with code 1 and a diff summary if wikis are out of sync with canonical docs.
Run: uv run python scripts/check_docs_sync.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
GEN_SCRIPT = ROOT / "scripts" / "generate_doc_wikis.py"


def _generated_files(wiki_dir: Path) -> list[Path]:
    """Return generated Markdown files in a wiki directory."""
    return sorted(path for path in wiki_dir.glob("*.md") if _is_generated(path))


def _is_generated(path: Path) -> bool:
    """Return True when a wiki file carries the generated marker."""
    return path.exists() and path.read_text(encoding="utf-8").startswith("<!-- GENERATED")


def check_wiki_sync(existing_dir: Path, generated_dir: Path, label: str) -> bool:
    """Return True if all generated files match the canonical output."""
    expected = {path.name: path for path in _generated_files(generated_dir)}
    existing = {path.name: path for path in _generated_files(existing_dir)}
    ok = True
    for name, generated in expected.items():
        current = existing.get(name)
        if current is None:
            print(f"MISSING: {label}/{name}")
            ok = False
            continue
        if current.read_text(encoding="utf-8") != generated.read_text(encoding="utf-8"):
            print(f"OUT OF SYNC: {label}/{name}")
            ok = False
    stale = sorted(set(existing) - set(expected))
    for name in stale:
        print(f"STALE GENERATED FILE: {label}/{name}")
        ok = False
    if ok:
        print(f"OK: {label}")
    return ok


def _build_expected_docs(tmp_path: Path) -> Path:
    """Generate expected docs in a temporary copy."""
    import shutil

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
        raise RuntimeError(result.stderr)
    return tmp_docs


def main() -> None:
    """Check both generated wiki directories."""
    with tempfile.TemporaryDirectory() as tmp:
        try:
            tmp_docs = _build_expected_docs(Path(tmp))
        except RuntimeError as exc:
            print(f"Generator failed: {exc}")
            sys.exit(1)
        ok_plan = check_wiki_sync(ROOT / "docs" / "plan-wiki", tmp_docs / "plan-wiki", "plan-wiki")
        ok_todo = check_wiki_sync(ROOT / "docs" / "todo-wiki", tmp_docs / "todo-wiki", "todo-wiki")
    if ok_plan and ok_todo:
        print("All wikis are in sync.")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
