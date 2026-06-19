"""Graph Parser — parses Grphify output (graph.json, GRAPH_REPORT.md).

Reads Grphify's graph.json output and converts it into structured
GraphData objects with entities, relationships, and communities.

Implementation: Phase 4 (T4.02)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ex04.shared.types import Community, Entity, GraphData, Relationship

logger = logging.getLogger(__name__)


class GraphParser:
    """Parse Grphify output into structured GraphData.

    Reads graph.json files produced by Grphify and extracts entities,
    relationships, and community clusters into typed data structures.
    """

    def parse(self, graph_path: Path) -> GraphData:
        """Parse graph.json into structured GraphData.

        Args:
            graph_path: Path to the graph.json file.

        Returns:
            Structured GraphData with entities, relationships, communities.

        Raises:
            FileNotFoundError: If the graph file does not exist.
            ValueError: If the JSON is malformed.
        """
        if not graph_path.exists():
            raise FileNotFoundError(f"Graph file not found: {graph_path}")

        try:
            raw = json.loads(graph_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON in {graph_path}: {exc}") from exc

        entities = self._parse_nodes(raw.get("nodes", []))
        relationships = self._parse_edges(raw.get("edges", []))
        communities = self._parse_communities(raw.get("communities", []))

        logger.info(
            "Parsed graph: %d entities, %d relationships, %d communities",
            len(entities),
            len(relationships),
            len(communities),
        )
        return GraphData(entities=entities, relationships=relationships, communities=communities)

    @staticmethod
    def _parse_nodes(nodes: list[dict]) -> list[Entity]:
        """Convert raw node dicts to Entity objects.

        Args:
            nodes: List of node dicts with name, kind, file_path, line info.

        Returns:
            List of Entity objects.
        """
        entities: list[Entity] = []
        for node in nodes:
            line_start = node.get("line_start", 0)
            line_end = node.get("line_end", 0)
            entities.append(
                Entity(
                    name=str(node.get("name", "")),
                    kind=str(node.get("kind", "")),
                    file_path=str(node.get("file_path", "")),
                    line_range=(line_start, line_end),
                )
            )
        return entities

    @staticmethod
    def _parse_edges(edges: list[dict]) -> list[Relationship]:
        """Convert raw edge dicts to Relationship objects.

        Args:
            edges: List of edge dicts with source, target, type.

        Returns:
            List of Relationship objects.
        """
        relationships: list[Relationship] = []
        for edge in edges:
            relationships.append(
                Relationship(
                    source=str(edge.get("source", "")),
                    target=str(edge.get("target", "")),
                    type=str(edge.get("type", "")),
                )
            )
        return relationships

    @staticmethod
    def _parse_communities(communities: list[dict]) -> list[Community]:
        """Convert raw community dicts to Community objects.

        Args:
            communities: List of community dicts with name and members.

        Returns:
            List of Community objects.
        """
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
