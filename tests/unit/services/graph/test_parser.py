"""Tests for GraphParser implementation (T4.02).

Validates GraphParser.parse() against a REAL Grphify artifact
(``tests/fixtures/graph/sample_graph.json``, produced by ``graphify
update`` + ``cluster-only``) plus edge cases. The real-fixture contract
test is what proves the parser understands Grphify's actual node-link
schema (``links``, ``relation``, node-level ``community``), not a
hand-authored stand-in.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from ex04.services.graph.parser import GraphParser
from ex04.shared.types import GraphData

FIXTURE = Path(__file__).parents[3] / "fixtures" / "graph" / "sample_graph.json"


def _write_tmp(payload: dict | str) -> Path:
    """Write a JSON payload (or raw string) to a temp file and return its path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        if isinstance(payload, str):
            tmp.write(payload)
        else:
            json.dump(payload, tmp)
        return Path(tmp.name)


class TestGraphParserRealArtifact:
    """Contract tests against a genuine Grphify graph.json fixture."""

    def test_fixture_exists(self) -> None:
        """The committed real Grphify fixture must be present."""
        assert FIXTURE.exists(), f"Missing Grphify fixture: {FIXTURE}"

    def test_parses_real_artifact_non_empty(self) -> None:
        """parse() yields populated, typed data from a real Grphify artifact."""
        result = GraphParser().parse(FIXTURE)
        assert isinstance(result, GraphData)
        assert result.entities and result.relationships and result.communities

    def test_entities_use_real_node_fields(self) -> None:
        """Entities map Grphify node fields (id, file_type, source_file)."""
        result = GraphParser().parse(FIXTURE)
        sample = result.entities[0]
        assert sample.name  # node id, not empty
        assert sample.kind  # file_type, not empty
        assert sample.file_path  # source_file, not empty

    def test_relationships_use_relation_field(self) -> None:
        """Relationships read the ``relation`` field, not ``type``."""
        result = GraphParser().parse(FIXTURE)
        assert all(r.source and r.target for r in result.relationships)
        assert any(r.type for r in result.relationships)

    def test_communities_from_node_metadata(self) -> None:
        """Communities are derived from node-level ``community`` ids."""
        result = GraphParser().parse(FIXTURE)
        assert len(result.communities) >= 1
        assert all(c.size == len(c.entities) for c in result.communities)

    def test_relationship_endpoints_match_entity_names(self) -> None:
        """Edge endpoints reference node ids, so they connect to entity names."""
        result = GraphParser().parse(FIXTURE)
        names = {e.name for e in result.entities}
        connected = [r for r in result.relationships if r.source in names]
        assert connected  # at least some edges resolve to known entities


class TestGraphParserEdgeCases:
    """Edge-case and error-handling tests."""

    def test_parse_returns_graph_data_on_empty(self) -> None:
        """parse() returns GraphData for an empty node-link graph."""
        path = _write_tmp({"nodes": [], "links": []})
        try:
            result = GraphParser().parse(path)
            assert isinstance(result, GraphData)
            assert not result.entities and not result.relationships
        finally:
            path.unlink()

    def test_parse_supports_legacy_edges_key(self) -> None:
        """parse() still accepts the legacy top-level ``edges`` key."""
        path = _write_tmp(
            {"nodes": [], "edges": [{"source": "a", "target": "b", "relation": "calls"}]}
        )
        try:
            result = GraphParser().parse(path)
            assert result.relationships[0].type == "calls"
        finally:
            path.unlink()

    def test_parse_supports_legacy_communities_array(self) -> None:
        """parse() falls back to a legacy top-level communities array."""
        path = _write_tmp(
            {"nodes": [], "links": [], "communities": [{"name": "c1", "members": ["a", "b"]}]}
        )
        try:
            result = GraphParser().parse(path)
            assert result.communities[0].name == "c1"
            assert result.communities[0].size == 2
        finally:
            path.unlink()

    def test_parse_malformed_json(self) -> None:
        """parse() raises ValueError on malformed JSON."""
        path = _write_tmp("{invalid json}")
        try:
            with pytest.raises(ValueError):
                GraphParser().parse(path)
        finally:
            path.unlink()

    def test_parse_missing_file(self) -> None:
        """parse() raises FileNotFoundError on a missing file."""
        with pytest.raises(FileNotFoundError):
            GraphParser().parse(Path("/nonexistent/graph.json"))
