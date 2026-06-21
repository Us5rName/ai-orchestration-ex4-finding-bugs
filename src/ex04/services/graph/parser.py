"""Graph Parser — parses Grphify output into structured GraphData.

Grphify schema: edges under ``links``/``edges``, nodes carry ``id``,
``label``, ``file_type``, ``source_file``, ``source_location``,
``community``. Edge validation/key generation delegated to _parser_helpers.
One-parser-path rule: GraphReader must not re-parse raw JSON.

Implementation: Phase 4 (T4.02); enriched T4.19a; hardened T4.19a-H2.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path

from ex04.services.graph._parser_helpers import (
    GraphParserError,
    parse_edges,
    parse_legacy_communities,
    parse_line_range,
)
from ex04.shared.json_utils import load_json
from ex04.shared.types import Community, Entity, GraphData

__all__ = ["GraphParser", "GraphParserError"]

logger = logging.getLogger(__name__)


class GraphParser:
    """Parse Grphify graph.json into structured GraphData.

    Node ID validation (non-None, non-empty, no duplicates) is here.
    Edge validation and key generation are in _parser_helpers.parse_edges.
    """

    def parse(self, graph_path: Path) -> GraphData:
        """Parse graph.json into GraphData.

        Raises:
            FileNotFoundError: If the graph file does not exist.
            GraphParserError: If structure or field types are invalid.
            ValueError: If the JSON is malformed.
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
        entity_ids = {e.name for e in entities}
        relationships = parse_edges(edges, entity_ids)
        communities = self._parse_communities(nodes, raw.get("communities", []))
        logger.info(
            "Parsed graph: %d entities, %d relationships, %d communities",
            len(entities), len(relationships), len(communities),
        )
        return GraphData(entities=entities, relationships=relationships, communities=communities)

    @staticmethod
    def _parse_nodes(nodes: list[object]) -> list[Entity]:
        """Map Grphify nodes to enriched Entity objects; validate IDs."""
        result: list[Entity] = []
        seen_ids: set[str] = set()
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                raise GraphParserError(f"Node[{i}] must be a JSON object.")
            raw_id, raw_label = node.get("id"), node.get("label")
            if raw_id is None and raw_label is None:
                raise GraphParserError(
                    f"Node[{i}] missing 'id' (got None) — explicit None is not valid."
                )
            resolved_id = raw_id if raw_id is not None else raw_label
            if resolved_id is None or str(resolved_id).strip() == "":
                raise GraphParserError(
                    f"Node[{i}] has empty or None 'id': {resolved_id!r}."
                )
            node_id = str(resolved_id)
            if node_id in seen_ids:
                raise GraphParserError(f"Node[{i}] duplicate entity ID: {node_id!r}.")
            seen_ids.add(node_id)
            label = str(raw_label) if raw_label is not None else node_id
            community_raw = node.get("community")
            community: int | None = None
            if community_raw is not None:
                try:
                    community = int(community_raw)
                except (TypeError, ValueError):
                    logger.warning("Node[%d] invalid community: %r", i, community_raw)
            skip = {"id", "label", "file_type", "source_file", "source_location",
                    "community", "community_name", "kind"}
            result.append(Entity(
                name=node_id,
                kind=str(node.get("file_type", node.get("kind", ""))),
                file_path=str(node.get("source_file", node.get("file_path", ""))),
                line_range=parse_line_range(node.get("source_location")),
                label=label, community=community,
                metadata={k: v for k, v in node.items() if k not in skip},
            ))
        return result

    @staticmethod
    def _parse_communities(nodes: list[object], legacy: list[object]) -> list[Community]:
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
            return [Community(name=names[c], entities=m, size=len(m)) for c, m in grouped.items()]
        return parse_legacy_communities(legacy)
