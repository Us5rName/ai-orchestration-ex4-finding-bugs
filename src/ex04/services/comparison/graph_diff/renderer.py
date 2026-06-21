"""Persist graph-diff JSON and Markdown artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ex04.services.comparison.graph_diff.models import GraphDiffArtifacts, GraphDiffResult
from ex04.shared.artifact_store import ArtifactOverwriteError


def render_graph_diff(result: GraphDiffResult, artifact_path: Path) -> GraphDiffArtifacts:
    """Write graph_diff.json and graph_diff.md under artifact_path/reports."""
    reports_dir = artifact_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    data = result.to_dict()
    json_text = json.dumps(data, indent=2, sort_keys=True)
    markdown_text = _markdown(result)
    json_path = reports_dir / "graph_diff.json"
    markdown_path = reports_dir / "graph_diff.md"
    _write_once(json_path, json_text)
    _write_once(markdown_path, markdown_text)
    return GraphDiffArtifacts(
        json_path=json_path,
        markdown_path=markdown_path,
        graph_diff_hash=hashlib.sha256(json_text.encode("utf-8")).hexdigest(),
        markdown_hash=hashlib.sha256(markdown_text.encode("utf-8")).hexdigest(),
    )


def _write_once(path: Path, text: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise ArtifactOverwriteError(f"Artifact already exists with different bytes: {path}")
    if not path.exists():
        path.write_text(text, encoding="utf-8")


def _markdown(result: GraphDiffResult) -> str:
    lines = [
        "# Graph Diff",
        "",
        f"Status: `{result.status.value}`",
        "",
        "## Snapshots",
        "",
        f"- Pre: `{result.pre_snapshot.sha256}` "
        f"({result.pre_snapshot.entity_count} entities, "
        f"{result.pre_snapshot.relationship_count} relationships)",
        f"- Post: `{result.post_snapshot.sha256}` "
        f"({result.post_snapshot.entity_count} entities, "
        f"{result.post_snapshot.relationship_count} relationships)",
    ]
    if result.error_detail:
        lines.extend(["", f"Detail: {result.error_detail}"])
    lines.extend(_summary(result))
    lines.extend(_entity_lines(result))
    lines.extend(_relationship_lines(result))
    lines.extend(_community_lines(result))
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in result.limitations)
    return "\n".join(lines) + "\n"


def _summary(result: GraphDiffResult) -> list[str]:
    return [
        "",
        "## Summary",
        "",
        f"- Entities: {len(result.entity_changes)}",
        f"- Relationships: {len(result.relationship_changes)}",
        f"- Communities: {len(result.community_changes)}",
        "",
        "Graph Change Analysis: structural changes are evidence only and do not prove correctness.",
    ]


def _entity_lines(result: GraphDiffResult) -> list[str]:
    lines = ["", "## Entity Changes", "", "| Entity | Change | Fields |", "|---|---|---|"]
    lines.extend(
        f"| `{change.entity_id}` | {change.change.value} | "
        f"{', '.join(field.field_name for field in change.field_changes)} |"
        for change in result.entity_changes
    )
    return lines


def _relationship_lines(result: GraphDiffResult) -> list[str]:
    lines = ["", "## Relationship Changes", "", "| Source | Type | Target | Change | Fields |", "|---|---|---|---|---|"]
    lines.extend(
        f"| `{c.identity.source_id}` | {c.identity.rel_type} | `{c.identity.target_id}` | "
        f"{c.change.value} | {', '.join(f.field_name for f in c.field_changes)} |"
        for c in result.relationship_changes
    )
    return lines


def _community_lines(result: GraphDiffResult) -> list[str]:
    lines = ["", "## Community Changes", "", "| Before | After | Change | Jaccard |", "|---|---|---|---:|"]
    lines.extend(
        f"| `{c.before_community}` | `{c.after_community}` | {c.change.value} | {c.jaccard:.3f} |"
        for c in result.community_changes
    )
    return lines
