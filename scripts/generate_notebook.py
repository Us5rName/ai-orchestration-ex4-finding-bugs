"""Generate notebooks/comparison_analysis.ipynb via nbformat.

Produces an SDK-based, keyless notebook with 8 sections. Imports only
from ex04.sdk and ex04.shared. Runs deterministically on fixture data.

Usage: uv run python scripts/generate_notebook.py

Traceability: [TODO P8-R07]
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).parent.parent
NB_PATH = ROOT / "notebooks" / "comparison_analysis.ipynb"

EVIDENCE_BANNER = (
    "> **Evidence Class: FIXTURE** — All results are deterministic fixtures,\n"
    "> not live LLM telemetry. Token telemetry is blocked (no API keys)."
)


def _md(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(source)


def _code(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(source)


def build_notebook() -> nbf.NotebookNode:
    """Build the full comparison_analysis notebook."""
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3", "language": "python", "name": "python3"
    }
    nb.cells = [
        # Section 1: Header and provenance
        _md("# EX04 — Comparison Analysis\n\n" + EVIDENCE_BANNER),
        _code("""\
import json  # noqa: E401
import sys
from pathlib import Path

ROOT = Path(".").resolve()
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

prov = json.loads(  # noqa: E402
    (ROOT / "artifacts" / "pre_fix" / "provenance.json").read_text()
)
print(f"Target repo  : {prov['target_repo']}")
print(f"Target commit: {prov['target_commit'][:12]}...")
print(f"Graphify     : {prov['graphify_status']}")
print(f"Evidence class: {prov['evidence_class']}")"""),

        # Section 2: Load manifests
        _md("## Section 2 — Fixture Manifests"),
        _code("""\
naive_m = json.loads(
    (ROOT / "artifacts" / "manifests" / "fixture-naive-001_manifest.json").read_text()
)
guided_m = json.loads(
    (ROOT / "artifacts" / "manifests" / "fixture-001_manifest.json").read_text()
)
print("Naive  :", naive_m["run_id"], "| files:", naive_m["files_read"],
      "| tokens:", naive_m["input_tokens"])
print("Guided :", guided_m["run_id"], "| files:", guided_m["files_read"],
      "| tokens:", guided_m["input_tokens"])"""),

        # Section 3: Signed metrics (from fixture)
        _md("## Section 3 — Signed Delta Table\n\n"
            + "> Token delta is `None` because telemetry is blocked."),
        _code("""\
from ex04.shared.types_experiment import SignedMetrics  # noqa: F401
from ex04.shared.types_results import InvestigationResult

# Build fixture results matching the manifests
naive_r = InvestigationResult(
    files_read=naive_m["files_read"], iterations=naive_m["iterations"],
    parser_status="parsed_ok", gate_status="pass_without_gate",
    evidence_class="fixture",
)
guided_r = InvestigationResult(
    files_read=guided_m["files_read"], iterations=guided_m["iterations"],
    parser_status="parsed_ok", gate_status="pass_without_gate",
    evidence_class="fixture",
)

print(f"{'Metric':<20} {'Naive':>8} {'Graph-guided':>14} {'Delta':>8}")
print("-" * 52)
print(f"{'Files read':<20} {naive_r.files_read:>8} {guided_r.files_read:>14} "
      f"{guided_r.files_read - naive_r.files_read:>+8}")
print(f"{'Iterations':<20} {naive_r.iterations:>8} {guided_r.iterations:>14} "
      f"{guided_r.iterations - naive_r.iterations:>+8}")
print(f"{'Input tokens':<20} {'N/A (blocked)':>8} {'N/A (blocked)':>14} {'N/A':>8}")"""),

        # Section 4: Graph navigation
        _md("## Section 4 — Graph Navigation Demo\n\n"
            "> Loads real Graphify output from artifacts/pre_fix/graphify-out/graph.json."),
        _code("""\
graph_path = ROOT / "artifacts" / "pre_fix" / "graphify-out" / "graph.json"
graph = json.loads(graph_path.read_text())
nodes = graph.get("nodes", [])
edges = graph.get("edges", [])
print(f"Graph: {len(nodes)} nodes, {len(edges)} edges")
print("Top-5 nodes by label:")
for n in nodes[:5]:
    print(f"  [{n.get('community','?')}] {n['label']:<40} ({n.get('source_file','')})")"""),

        # Section 5: Vault navigation
        _md("## Section 5 — Vault Navigation Demo"),
        _code("""\
vault_dir = ROOT / "obsidian"
notes = list(vault_dir.rglob("*.md")) if vault_dir.exists() else []
print(f"Vault: {len(notes)} notes in {vault_dir}")
for note in notes[:5]:
    print(f"  {note.relative_to(vault_dir)}")"""),

        # Section 6: Correctness gate (skipped)
        _md("## Section 6 — Correctness Gate\n\n"
            "> Gate status: `skipped` — no patch provided in keyless mode."),
        _code("""\
for m in (naive_m, guided_m):
    print(f"{m['run_id']}: gate={m['correctness_gate_status']}, "
          f"patch={m['patch_status']}")"""),

        # Section 7: Charts
        _md("## Section 7 — Charts\n\n"
            "> Pre-generated fixture-labeled PNGs from `assets/charts/`."),
        _code("""\
from IPython.display import Image, display  # noqa: I001
for fname in sorted((ROOT / "assets" / "charts").glob("*.png")):
    print(fname.name)
    display(Image(str(fname), width=500))"""),

        # Section 8: Evidence classification summary
        _md("## Section 8 — Evidence Classification Summary"),
        _code("""\
rows = [
    ("Target repo", "andela/buggy-python", "Deterministic — real clone"),
    ("Graphify extraction", "snippets/ → 13 nodes", "Deterministic — real CLI run"),
    ("Bug reproduction", "ImportError exit code 1", "Deterministic — real run"),
    ("Naive investigation", "Fixture manifest", "Fixture — no live LLM"),
    ("Graph investigation", "Fixture manifest", "Fixture — no live LLM"),
    ("Token telemetry", "N/A", "Blocked — no API keys"),
    ("Cost estimates", "N/A", "Blocked — no token data"),
]
print(f"{'Evidence Item':<28} {'Value':<22} {'Classification'}")
print("-" * 75)
for r in rows:
    print(f"{r[0]:<28} {r[1]:<22} {r[2]}")"""),
    ]
    return nb


def main() -> None:
    """Write the notebook to notebooks/comparison_analysis.ipynb."""
    nb = build_notebook()
    NB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with NB_PATH.open("w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Wrote {NB_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
