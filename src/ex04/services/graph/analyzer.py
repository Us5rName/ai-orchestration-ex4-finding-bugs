"""Graph Analyzer — lightweight structural heuristics over a parsed graph.

Provides cheap, dependency-free graph signals computed directly from
GraphData:
  - god nodes / centrality ranking via **degree** (not betweenness/PageRank)
  - communities via **connected components** (not Leiden/Louvain)

These are deliberately simple heuristics for fast, offline triage. For
richer analysis (Leiden communities, BFS/affected traversal), use Grphify's
own ``graphify query`` / ``graphify affected`` against the built graph.json
and the node-level ``community`` metadata the parser already surfaces.

Implementation: Phase 4 (T4.03)
"""

from __future__ import annotations

import logging
from collections import defaultdict

from ex04.shared.types import Community, GraphData

logger = logging.getLogger(__name__)


class GraphAnalyzer:
    """Analyze a graph with degree-based and connected-component heuristics.

    Computes node **degree** centrality, ranks nodes relative to a reference
    node, and detects clusters via **connected components**. These are
    lightweight approximations — see the module docstring for when to prefer
    Grphify's native algorithms.
    """

    def find_god_nodes(self, graph: GraphData, min_degree: int = 2) -> list[str]:
        """Identify high-degree nodes (God Nodes) in the graph.

        God Nodes are entities with many connections — they likely
        orchestrate or depend on many other parts of the codebase.

        Args:
            graph: Parsed graph data to analyze.
            min_degree: Minimum degree to qualify as a God Node.

        Returns:
            List of entity names with degree >= min_degree, sorted descending.
        """
        degree = self._compute_degree(graph)
        god_nodes = [name for name, deg in degree.items() if deg >= min_degree]
        god_nodes.sort(key=lambda n: degree[n], reverse=True)
        logger.info("Found %d God Nodes (min_degree=%d)", len(god_nodes), min_degree)
        return god_nodes

    def rank_by_centrality(self, graph: GraphData, ref_node: str) -> list[tuple[str, float]]:
        """Rank nodes by centrality relative to a reference node.

        Uses degree centrality normalized by total node count. The
        reference node itself gets a score of 1.0.

        Args:
            graph: Parsed graph data to analyze.
            ref_node: Reference node name for ranking.

        Returns:
            List of (node_name, centrality_score) tuples sorted descending.
        """
        degree = self._compute_degree(graph)
        total = max(len(degree), 1)

        ranking: list[tuple[str, float]] = []
        for name, deg in degree.items():
            score = 1.0 if name == ref_node else deg / total
            ranking.append((name, score))

        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking

    def detect_communities(self, graph: GraphData) -> list[Community]:
        """Detect community clusters in the graph.

        Uses a simple connected-components approach to find clusters
        of tightly connected entities.

        Args:
            graph: Parsed graph data to analyze.

        Returns:
            List of Community objects representing detected clusters.
        """
        if not graph.entities and not graph.relationships:
            return []

        # Build adjacency list
        adjacency: dict[str, set[str]] = defaultdict(set)
        all_nodes: set[str] = {e.name for e in graph.entities}

        for rel in graph.relationships:
            adjacency[rel.source].add(rel.target)
            adjacency[rel.target].add(rel.source)
            all_nodes.add(rel.source)
            all_nodes.add(rel.target)

        # BFS connected components
        visited: set[str] = set()
        communities: list[Community] = []
        cluster_id = 0

        for node in sorted(all_nodes):
            if node in visited:
                continue
            cluster_id += 1
            members: list[str] = []
            queue: list[str] = [node]
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                members.append(current)
                for neighbor in sorted(adjacency.get(current, set())):
                    if neighbor not in visited:
                        queue.append(neighbor)
            communities.append(
                Community(name=f"cluster_{cluster_id}", entities=members, size=len(members))
            )

        logger.info("Detected %d communities", len(communities))
        return communities

    @staticmethod
    def _compute_degree(graph: GraphData) -> dict[str, int]:
        """Compute node degrees from relationships.

        Args:
            graph: Parsed graph data.

        Returns:
            Dict mapping node names to their degree (connection count).
        """
        degree: dict[str, int] = defaultdict(int)
        for rel in graph.relationships:
            degree[rel.source] += 1
            degree[rel.target] += 1
        return dict(degree)
