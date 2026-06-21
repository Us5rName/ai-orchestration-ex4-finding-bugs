"""Graph snapshot provenance helpers."""

from __future__ import annotations

from pathlib import Path

from ex04.services.comparison.graph_diff.canonicalize import canonical_graph_hash
from ex04.services.comparison.graph_diff.models import GraphSnapshotRef
from ex04.services.graph.interface import GraphReaderInterface
from ex04.shared.types_graph_enums import EdgeDirection


def snapshot_ref(reader: GraphReaderInterface, path: Path | None = None) -> GraphSnapshotRef:
    """Build typed snapshot provenance."""
    communities = reader.communities()
    return GraphSnapshotRef(
        portable_path=str(path) if path else "",
        sha256=canonical_graph_hash(reader),
        entity_count=len(reader.all_nodes()),
        relationship_count=sum(
            len(reader.edges_of(node.entity_id, direction=EdgeDirection.OUTGOING))
            for node in reader.all_nodes()
        ),
        community_count=len([key for key in communities if key is not None]),
    )
