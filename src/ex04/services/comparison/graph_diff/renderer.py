"""Persist graph-diff JSON and Markdown artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ex04.services.comparison.graph_diff.models import GraphDiffArtifacts, GraphDiffResult


def render_graph_diff(result: GraphDiffResult, artifact_path: Path) -> GraphDiffArtifacts:
    """Write graph_diff.json and graph_diff.md under artifact_path/reports."""
    reports_dir = artifact_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    data = result.to_dict()
    json_text = json.dumps(data, indent=2, sort_keys=True, default=str)
    markdown_text = _markdown(result)
    json_path = reports_dir / "graph_diff.json"
    markdown_path = reports_dir / "graph_diff.md"
    json_path.write_text(json_text, encoding="utf-8")
    markdown_path.write_text(markdown_text, encoding="utf-8")
    return GraphDiffArtifacts(
        json_path=json_path,
        markdown_path=markdown_path,
        graph_diff_hash=hashlib.sha256(json_text.encode()).hexdigest(),
        markdown_hash=hashlib.sha256(markdown_text.encode()).hexdigest(),
    )


def _markdown(result: GraphDiffResult) -> str:
    lines = [
        "# Graph Diff",
        "",
        f"Status: `{result.status.value}`",
    ]
    if result.error_detail:
        lines.extend(["", f"Detail: {result.error_detail}"])
    lines.extend([
        "",
        "## Summary",
        "",
        f"- Entities: {len(result.entity_changes)}",
        f"- Relationships: {len(result.relationship_changes)}",
        f"- Communities: {len(result.community_changes)}",
        "",
        "## Entity Changes",
        "",
        "| Entity | Change |",
        "|---|---|",
    ])
    lines.extend(f"| `{change.entity_id}` | {change.change.value} |" for change in result.entity_changes)
    lines.extend([
        "",
        "## Relationship Changes",
        "",
        "| Source | Type | Target | Change |",
        "|---|---|---|---|",
    ])
    lines.extend(
        f"| `{change.identity.source_id}` | {change.identity.rel_type} | "
        f"`{change.identity.target_id}` | {change.change.value} |"
        for change in result.relationship_changes
    )
    lines.extend([
        "",
        "## Community Changes",
        "",
        "| Before | After | Change | Jaccard |",
        "|---|---|---|---:|",
    ])
    lines.extend(
        f"| `{change.before_community}` | `{change.after_community}` | "
        f"{change.change.value} | {change.jaccard:.3f} |"
        for change in result.community_changes
    )
    return "\n".join(lines) + "\n"
