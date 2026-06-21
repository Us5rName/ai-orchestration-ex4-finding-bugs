"""Validate notebook cell imports and classification labels.

Parses notebooks/comparison_analysis.ipynb without executing it and
asserts structural/import correctness.

Traceability: [TODO P8-R07]
"""

from __future__ import annotations

import re
from pathlib import Path

import nbformat

ROOT = Path(__file__).parent.parent.parent.parent
NB_PATH = ROOT / "notebooks" / "comparison_analysis.ipynb"

_FORBIDDEN = re.compile(
    r"from ex04\.services\.|from ex04\.providers\.|import ex04\.services\."
)
_SDK_IMPORT = re.compile(r"from ex04\.(sdk|shared)")
_EVIDENCE_CLASS = re.compile(r"Evidence Class", re.IGNORECASE)


def _load_notebook() -> nbformat.NotebookNode:
    with NB_PATH.open(encoding="utf-8") as f:
        return nbformat.read(f, as_version=4)


def _code_cells(nb: nbformat.NotebookNode) -> list[str]:
    return [c["source"] for c in nb.cells if c["cell_type"] == "code"]


def _all_source(nb: nbformat.NotebookNode) -> str:
    return "\n".join(c["source"] for c in nb.cells)


def test_notebook_file_exists() -> None:
    """notebooks/comparison_analysis.ipynb must exist."""
    assert NB_PATH.exists(), f"Notebook not found: {NB_PATH}"


def test_no_service_imports_in_notebook() -> None:
    """Notebook cells must not import internal service modules directly."""
    nb = _load_notebook()
    violations = [
        f"Cell: {src[:60]!r}"
        for src in _code_cells(nb)
        if _FORBIDDEN.search(src)
    ]
    assert not violations, "Forbidden service imports found:\n" + "\n".join(violations)


def test_sdk_import_present() -> None:
    """At least one code cell must import from ex04.sdk or ex04.shared."""
    nb = _load_notebook()
    has_sdk = any(_SDK_IMPORT.search(src) for src in _code_cells(nb))
    assert has_sdk, "No SDK/shared imports found — notebook must use SDK layer only"


def test_evidence_classification_label_present() -> None:
    """Notebook must include an 'Evidence Class' label (fixture disclaimer)."""
    nb = _load_notebook()
    assert _EVIDENCE_CLASS.search(_all_source(nb)), (
        "No 'Evidence Class' label found — notebook must display classification banner"
    )
