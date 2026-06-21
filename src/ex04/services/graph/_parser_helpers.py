"""Internal parsing utilities for GraphParser.

GraphParserError is defined here and re-exported by parser.py.
Edge parsing (with validation) lives here to keep parser.py ≤ 150 lines.
Traceability: [TODO T4.19a], [PLAN ADR-007].
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter

from ex04.shared.types import Community, Relationship

_VALID_CONFIDENCE = {"extracted", "inferred", "unknown"}


class GraphParserError(ValueError):
    """Raised when a graph artifact fails structural validation."""


def parse_optional_float(
    edge: dict[str, object], field_name: str, idx: int
) -> float | None:
    """Parse an optional numeric field from an edge dict."""
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


def _content_key(src: str, tgt: str, rel_type: str) -> str:
    """Return a deterministic content-derived base key for a relationship."""
    canonical = json.dumps([src, rel_type, tgt], sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _validate_finite_float(value: float | None, field: str, idx: int) -> None:
    """Raise GraphParserError if value is present but not finite."""
    if value is not None and not math.isfinite(value):
        raise GraphParserError(
            f"Edge[{idx}] field '{field}' must be finite; got {value!r}."
        )


def parse_edges(edges: list[object], entity_ids: set[str]) -> list[Relationship]:
    """Parse Grphify edges with full validation and content-derived keys.

    Rejects None/missing endpoints, endpoints not in entity_ids,
    invalid confidence strings, non-finite numerics, and duplicate explicit keys.
    Generated keys are content-derived (not index-based).
    """
    result: list[Relationship] = []
    explicit_keys: set[str] = set()
    base_key_counts: Counter[str] = Counter()
    for i, edge in enumerate(edges):
        if not isinstance(edge, dict):
            raise GraphParserError(f"Edge[{i}] must be a JSON object.")
        raw_src, raw_tgt = edge.get("source"), edge.get("target")
        if raw_src is None:
            raise GraphParserError(f"Edge[{i}] 'source' is None — explicit None endpoint is invalid.")
        if raw_tgt is None:
            raise GraphParserError(f"Edge[{i}] 'target' is None — explicit None endpoint is invalid.")
        src, tgt = str(raw_src), str(raw_tgt)
        if not src:
            raise GraphParserError(f"Edge[{i}] 'source' is empty.")
        if not tgt:
            raise GraphParserError(f"Edge[{i}] 'target' is empty.")
        if src not in entity_ids:
            raise GraphParserError(f"Edge[{i}] source {src!r} does not refer to a parsed entity.")
        if tgt not in entity_ids:
            raise GraphParserError(f"Edge[{i}] target {tgt!r} does not refer to a parsed entity.")
        rel_type = str(edge.get("relation", edge.get("type", "")))
        explicit_key = edge.get("key")
        if explicit_key is not None:
            ekey = str(explicit_key)
            if ekey in explicit_keys:
                raise GraphParserError(f"Edge[{i}] duplicate explicit key: {ekey!r}.")
            explicit_keys.add(ekey)
            key = ekey
        else:
            base = _content_key(src, tgt, rel_type)
            occurrence = base_key_counts[base]
            base_key_counts[base] += 1
            key = base if occurrence == 0 else f"{base}#{occurrence}"
        confidence_raw = edge.get("confidence")
        confidence: str | None = None
        if confidence_raw is not None:
            conf_str = str(confidence_raw).lower()
            if conf_str not in _VALID_CONFIDENCE:
                raise GraphParserError(
                    f"Edge[{i}] invalid confidence value: {confidence_raw!r}. "
                    f"Expected one of {sorted(_VALID_CONFIDENCE)}."
                )
            confidence = conf_str
        cs = parse_optional_float(edge, "confidence_score", i)
        wt = parse_optional_float(edge, "weight", i)
        _validate_finite_float(cs, "confidence_score", i)
        _validate_finite_float(wt, "weight", i)
        skip = {"source", "target", "relation", "type", "key", "confidence",
                "confidence_score", "weight", "source_anchor"}
        result.append(Relationship(
            source=src, target=tgt, type=rel_type, key=key,
            confidence=confidence, confidence_score=cs, weight=wt,
            source_anchor=edge.get("source_anchor"),
            metadata={k: v for k, v in edge.items() if k not in skip},
        ))
    return result
