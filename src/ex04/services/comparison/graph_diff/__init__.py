"""Typed graph-diff reporting for comparison runs."""

from ex04.services.comparison.graph_diff.differ import GraphDiffer, diff_graphs
from ex04.services.comparison.graph_diff.models import (
    CommunityChange,
    CommunityChangeType,
    EntityChange,
    EntityChangeType,
    GraphDiffArtifacts,
    GraphDiffResult,
    PostGraphStatus,
    RelationshipChange,
    RelationshipChangeType,
    RelationshipIdentity,
)
from ex04.services.comparison.graph_diff.renderer import render_graph_diff

__all__ = [
    "CommunityChange",
    "CommunityChangeType",
    "EntityChange",
    "EntityChangeType",
    "GraphDiffer",
    "GraphDiffArtifacts",
    "GraphDiffResult",
    "PostGraphStatus",
    "RelationshipChange",
    "RelationshipChangeType",
    "RelationshipIdentity",
    "diff_graphs",
    "render_graph_diff",
]
