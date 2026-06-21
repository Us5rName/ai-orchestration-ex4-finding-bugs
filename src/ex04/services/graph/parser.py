"""Graph Parser — parses Grphify output into structured GraphData.

Grphify schema: edges under ``links``/``edges``, nodes carry ``id``,
``label``, ``file_type``, ``source_file``, ``source_location``,
``community``. T4.19a enrichment: populates all enriched fields.
One-parser-path rule: GraphReader must not re-parse raw JSON.

Implementation: Phase 4 (T4.02); enriched T4.19a.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path

from ex04.services.graph._parser_helpers import (
    GraphParserError,
    parse_legacy_communities,
    parse_line_range,
    parse_optional_float,
)
from ex04.shared.json_utils import load_json
from ex04.shared.types import Community, Entity, GraphData, Relationship

__all__ = ["GraphParser", "GraphParserError"]

logger = logging.getLogger(__name__)

_VALID_CONFIDENCE = {"extracted", "inferred", "unknown"}


class GraphParser:
    """Parse Grphify graph.json into structured GraphData."""

    def parse(self, graph_path: Path) -> GraphData:
        """Parse graph.json into GraphData (entities, relationships, communities).

        Raises:
            FileNotFoundError: If the graph file does not exist.
            GraphParserError: If structure, endpoints, or field types are invalid.
            ValueError: If the JSON is malformed (from load_json).
        """
        if not graph_path.exists():
            raise FileNotFoundError(f"Graph file not found: {graph_path}")
        raw = load_json(graph_path)
        if not isinstance(raw, dict):
            raise GraphParserError("Graph artifact must be a JSON object.")
        nodes = raw.get("nodes", [])
        if not isinstance(nodes, list):
            raise GraphParserError("'nodes' must be a list.")
        edges = raw.get("links", raw.get("edges", []))
        if not isinstance(edges, list):
            raise GraphParserError("'links'/'edges' must be a list.")
        entities = self._parse_nodes(nodes)
        relationships = self._parse_edges(edges)
        communities = self._parse_communities(nodes, raw.get("communities", []))
        logger.info(
            "Parsed graph: %d entities, %d relationships, %d communities",
            len(entities), len(relationships), len(communities),
        )
        return GraphData(entities=entities, relationships=relationships, communities=communities)

    @staticmethod
    def _parse_nodes(nodes: list[object]) -> list[Entity]:
        """Map Grphify nodes to enriched Entity objects."""
        result: list[Entity] = []
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                raise GraphParserError(f"Node[{i}] must be a JSON object.")
            node_id = str(node.get("id", node.get("label", "")))
            if not node_id:
                raise GraphParserError(f"Node[{i}] missing 'id' or 'label'.")
            label = str(node.get("label", node_id))
            community_raw = node.get("community")
            community: int | None = None
            if community_raw is not None:
                try:
                    community = int(community_raw)
                except (TypeError, ValueError):
                    logger.warning("Node[%d] invalid community: %r", i, community_raw)
            skip = {"id", "label", "file_type", "source_file", "source_location",
                    "community", "community_name", "kind"}
            metadata = {k: v for k, v in node.items() if k not in skip}
            result.append(Entity(
                name=node_id, kind=str(node.get("file_type", node.get("kind", ""))),
                file_path=str(node.get("source_file", node.get("file_path", ""))),
                line_range=parse_line_range(node.get("source_location")),
                label=label, community=community, metadata=metadata,
            ))
        return result

    @staticmethod
    def _parse_edges(edges: list[object]) -> list[Relationship]:
        """Map Grphify edges to enriched Relationship objects."""
        result: list[Relationship] = []
        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                raise GraphParserError(f"Edge[{i}] must be a JSON object.")
            src = str(edge.get("source", ""))
            tgt = str(edge.get("target", ""))
            if not src or not tgt:
                raise GraphParserError(f"Edge[{i}] missing 'source' or 'target'.")
            rel_type = str(edge.get("relation", edge.get("type", "")))
            key = edge.get("key") or f"{src}:{rel_type}:{tgt}:{i}"
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
            skip = {"source", "target", "relation", "type", "key", "confidence",
                    "confidence_score", "weight", "source_anchor"}
            result.append(Relationship(
                source=src, target=tgt, type=rel_type, key=str(key),
                confidence=confidence,
                confidence_score=parse_optional_float(edge, "confidence_score", i),
                weight=parse_optional_float(edge, "weight", i),
                source_anchor=edge.get("source_anchor"),
                metadata={k: v for k, v in edge.items() if k not in skip},
            ))
        return result

    @staticmethod
    def _parse_communities(
        nodes: list[object], legacy: list[object]
    ) -> list[Community]:
        """Build communities from node-level cluster metadata, legacy fallback."""
        grouped: dict[str, list[str]] = defaultdict(list)
        names: dict[str, str] = {}
        for node in nodes:
            if not isinstance(node, dict) or "community" not in node:
                continue
            cid = str(node["community"])
            grouped[cid].append(str(node.get("id", node.get("label", ""))))
            names.setdefault(cid, str(node.get("community_name", f"Community {cid}")))
        if grouped:
            return [
                Community(name=names[cid], entities=members, size=len(members))
                for cid, members in grouped.items()
            ]
        return parse_legacy_communities(legacy)
