"""Graph Parser — parses Grphify output into structured GraphData.

Reads Grphify's graph.json (NetworkX node-link format) and converts it
into GraphData with entities, relationships, and communities.

Grphify schema (verified against the installed package):
  - edges live under ``links`` (node_link_data default), ``edges`` fallback.
  - nodes carry ``id``, ``label``, ``file_type``, ``source_file``,
    ``source_location`` (e.g. ``"L1"``) and, after clustering, ``community``
    (id) plus ``community_name``.
  - edges carry ``source``, ``target`` and ``relation`` (not ``type``).

Implementation: Phase 4 (T4.02)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path

from ex04.shared.json_utils import load_json
from ex04.shared.types import Community, Entity, GraphData, Relationship

logger = logging.getLogger(__name__)


class GraphParser:
    """Parse Grphify graph.json into structured GraphData."""

    def parse(self, graph_path: Path) -> GraphData:
        """Parse graph.json into GraphData (entities, relationships, communities).

        Raises:
            FileNotFoundError: If the graph file does not exist.
            ValueError: If the JSON is malformed.
        """
        if not graph_path.exists():
            raise FileNotFoundError(f"Graph file not found: {graph_path}")

        raw = load_json(graph_path)

        nodes = raw.get("nodes", [])
        # node_link_data serialises edges under "links"; older graphs use "edges".
        edges = raw.get("links", raw.get("edges", []))

        entities = self._parse_nodes(nodes)
        relationships = self._parse_edges(edges)
        communities = self._parse_communities(nodes, raw.get("communities", []))

        logger.info(
            "Parsed graph: %d entities, %d relationships, %d communities",
            len(entities),
            len(relationships),
            len(communities),
        )
        return GraphData(entities=entities, relationships=relationships, communities=communities)

    @staticmethod
    def _parse_nodes(nodes: list[dict]) -> list[Entity]:
        """Map Grphify nodes to Entity objects (name = node id, so edges connect)."""
        return [
            Entity(
                name=str(node.get("id", node.get("label", ""))),
                kind=str(node.get("file_type", node.get("kind", ""))),
                file_path=str(node.get("source_file", node.get("file_path", ""))),
                line_range=_parse_line_range(node.get("source_location")),
            )
            for node in nodes
        ]

    @staticmethod
    def _parse_edges(edges: list[dict]) -> list[Relationship]:
        """Map Grphify edges to Relationship objects (type = ``relation``)."""
        return [
            Relationship(
                source=str(edge.get("source", "")),
                target=str(edge.get("target", "")),
                type=str(edge.get("relation", edge.get("type", ""))),
            )
            for edge in edges
        ]

    @staticmethod
    def _parse_communities(nodes: list[dict], legacy: list[dict]) -> list[Community]:
        """Build communities from node-level cluster metadata, legacy array fallback.

        Grphify stores communities as a node-level ``community`` id (plus
        ``community_name``) after clustering. Falls back to a legacy top-level
        ``communities`` array when node metadata is absent.
        """
        grouped: dict[str, list[str]] = defaultdict(list)
        names: dict[str, str] = {}
        for node in nodes:
            if "community" not in node:
                continue
            cid = str(node["community"])
            grouped[cid].append(str(node.get("id", node.get("label", ""))))
            names.setdefault(cid, str(node.get("community_name", f"Community {cid}")))

        if grouped:
            return [
                Community(name=names[cid], entities=members, size=len(members))
                for cid, members in grouped.items()
            ]
        return _parse_legacy_communities(legacy)


def _parse_line_range(source_location: object) -> tuple[int, int]:
    """Parse a ``source_location`` string (``"L12"`` / ``"L3-L9"``) to a line range."""
    if not isinstance(source_location, str):
        return (0, 0)
    parts = [p.strip().lstrip("Ll") for p in source_location.split("-") if p.strip()]
    try:
        nums = [int(p) for p in parts if p]
    except ValueError:
        return (0, 0)
    return (nums[0], nums[-1]) if nums else (0, 0)


def _parse_legacy_communities(communities: list[dict]) -> list[Community]:
    """Convert a legacy top-level community array to Community objects."""
    result: list[Community] = []
    for comm in communities:
        members = comm.get("members", comm.get("entities", []))
        result.append(
            Community(
                name=str(comm.get("name", "")),
                entities=[str(m) for m in members],
                size=len(members),
            )
        )
    return result
