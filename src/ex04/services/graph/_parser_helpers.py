"""Internal parsing utilities for GraphParser.

GraphParserError is defined here and re-exported by parser.py.
Traceability: [TODO T4.19a], [PLAN ADR-007].
"""

from __future__ import annotations

from ex04.shared.types import Community


class GraphParserError(ValueError):
    """Raised when a graph artifact fails structural validation."""


def parse_optional_float(
    edge: dict[str, object], field_name: str, idx: int
) -> float | None:
    """Parse an optional numeric field from an edge dict.

    Raises:
        GraphParserError: If the field is present but not numeric.
    """
    raw = edge.get(field_name)
    if raw is None:
        return None
    try:
        return float(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise GraphParserError(
            f"Edge[{idx}] invalid {field_name} value: {raw!r}. Expected a number."
        ) from exc


def parse_line_range(source_location: object) -> tuple[int, int]:
    """Parse a ``source_location`` string (``"L12"`` / ``"L3-L9"``)."""
    if not isinstance(source_location, str):
        return (0, 0)
    parts = [p.strip().lstrip("Ll") for p in source_location.split("-") if p.strip()]
    try:
        nums = [int(p) for p in parts if p]
    except ValueError:
        return (0, 0)
    return (nums[0], nums[-1]) if nums else (0, 0)


def parse_legacy_communities(communities: list[object]) -> list[Community]:
    """Convert a legacy top-level community array to Community objects."""
    result: list[Community] = []
    for comm in communities:
        if not isinstance(comm, dict):
            continue
        members = comm.get("members", comm.get("entities", []))
        result.append(Community(
            name=str(comm.get("name", "")),
            entities=[str(m) for m in members],  # type: ignore[union-attr]
            size=len(members),  # type: ignore[arg-type]
        ))
    return result
