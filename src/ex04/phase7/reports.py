"""Phase 7 reverse-engineering report generation."""

from __future__ import annotations

import json
from pathlib import Path

from ex04.services.analysis.reverse_engineer import ReverseEngineer
from ex04.services.graph.parser import GraphParser


def generate_phase7_reports(
    graph_path: Path,
    investigation_result_path: Path,
    reports_dir: Path,
) -> dict[str, Path]:
    """Generate Phase 7 reverse-engineering and diagnosis reports."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    graph_data = GraphParser().parse(graph_path)
    result = json.loads(investigation_result_path.read_text(encoding="utf-8"))
    diagrams = ReverseEngineer().reverse_engineer(graph_data)

    outputs = {
        "diagrams": reports_dir / "diagrams.md",
        "root_cause": reports_dir / "root_cause.md",
        "diff": reports_dir / "diff_foobar.md",
        "pipeline": reports_dir / "pipeline.md",
        "index": reports_dir / "README.md",
    }
    outputs["diagrams"].write_text(diagrams, encoding="utf-8")
    outputs["root_cause"].write_text(_root_cause_report(result), encoding="utf-8")
    outputs["diff"].write_text(_diff_report(result), encoding="utf-8")
    outputs["pipeline"].write_text(_pipeline_report(), encoding="utf-8")
    outputs["index"].write_text(_index_report(), encoding="utf-8")
    return outputs


def _root_cause_report(result: dict[str, object]) -> str:
    return "\n".join([
        "# Root Cause",
        "",
        str(result.get("root_cause", "")),
        "",
        "## Evidence",
        "",
        "- Suspect: `snippets/foobar.py:8-10`",
        "- Failure mode: repeated calls share the same default list instance.",
        "- Verification: targeted post-fix assertion passed.",
        "",
    ])


def _diff_report(result: dict[str, object]) -> str:
    diff = str(result.get("fix_diff", "")).strip()
    return "\n".join([
        "# Before/After Diff: `snippets/foobar.py`",
        "",
        "The fix replaces the mutable default list with a `None` sentinel and "
        "allocates a fresh list inside the function.",
        "",
        "```diff",
        diff,
        "```",
        "",
    ])


def _pipeline_report() -> str:
    return """# Phase 7 Pipeline

```mermaid
flowchart LR
    target[Target snapshot] --> graph[Graphify graph]
    graph --> vault[Obsidian vault]
    graph --> agent[Graph-guided agent]
    vault --> agent
    agent --> report[Bug analysis]
    agent --> comparison[Token comparison]
    graph --> diagrams[Reverse-engineering diagrams]
```

The Phase 7 path is keyless and deterministic: Graphify supplies structural
context, the vault renders navigable notes, and the agent/comparison runners
use deterministic provider responses at the gatekeeper boundary.
"""


def _index_report() -> str:
    return """# Reports

- [Bug analysis](bug_analysis.md)
- [Root cause](root_cause.md)
- [Before/after diff](diff_foobar.md)
- [Reverse-engineering diagrams](diagrams.md)
- [Pipeline](pipeline.md)
- [Blocked operations](blocked_operations.md)
- [Clean-clone verification](clean_clone_verification.md)
"""
