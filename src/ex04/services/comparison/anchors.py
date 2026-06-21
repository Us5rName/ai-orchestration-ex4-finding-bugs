"""Source-anchor validation for structured investigation evidence."""

from __future__ import annotations

from pathlib import Path

from ex04.shared.types_evidence import StructuredEvidence


def validate_evidence_anchors(
    parsed: dict[str, object],
    snapshot_root: Path,
) -> tuple[list[StructuredEvidence], list[str]]:
    """Validate parsed evidence anchors against a pinned snapshot root."""
    raw = parsed.get("evidence", [])
    valid: list[StructuredEvidence] = []
    limitations: list[str] = []
    if not isinstance(raw, list):
        return valid, ["Evidence field is not a list."]
    root = snapshot_root.resolve()
    for item in raw:
        if not isinstance(item, dict):
            limitations.append("Invalid evidence entry ignored.")
            continue
        evidence = _validate_one(item, root)
        if isinstance(evidence, StructuredEvidence):
            valid.append(evidence)
        else:
            limitations.append(evidence)
    return valid, limitations


def _validate_one(item: dict[object, object], root: Path) -> StructuredEvidence | str:
    rel = str(item.get("file", ""))
    if not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        return f"Invalid evidence path ignored: {rel!r}"
    path = (root / rel).resolve()
    if not path.is_relative_to(root) or not path.exists():
        return f"Evidence file not found: {rel}"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start_raw, end_raw = item.get("line_start"), item.get("line_end")
    if not isinstance(start_raw, int) or not isinstance(end_raw, int):
        return f"Invalid evidence range: {rel}"
    start, end = start_raw, end_raw
    if end > len(lines):
        return f"Evidence range outside file: {rel}:{start}-{end}"
    return StructuredEvidence(
        source_file=rel,
        line_start=start,
        line_end=end,
        symbol=str(item.get("symbol", "")),
        sent_to_model=False,
        in_final_diagnosis=True,
    )
