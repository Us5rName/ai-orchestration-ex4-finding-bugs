"""Tests for GraphParser implementation (T4.02).

Tests GraphParser.parse() against GraphServiceInterface contract:
- Reads graph.json and returns GraphData
- Extracts entities, relationships, communities from Grphify output
- Handles missing fields, malformed JSON, empty graph
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from ex04.services.graph.parser import GraphParser
from ex04.shared.types import GraphData


class TestGraphParserParse:
    """Tests for GraphParser.parse() method."""

    def test_parse_returns_graph_data(self) -> None:
        """Test that parse() returns a GraphData object."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump({"nodes": [], "edges": []}, tmp)
            tmp_path = tmp.name

        try:
            parser = GraphParser()
            result = parser.parse(Path(tmp_path))
            assert isinstance(result, GraphData)
        finally:
            Path(tmp_path).unlink()

    def test_parse_entities_from_nodes(self) -> None:
        """Test that parse() extracts entities from nodes."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(
                {
                    "nodes": [
                        {
                            "name": "foo",
                            "kind": "function",
                            "file_path": "a.py",
                            "line_start": 1,
                            "line_end": 10,
                        }
                    ],
                    "edges": [],
                },
                tmp,
            )
            tmp_path = tmp.name

        try:
            parser = GraphParser()
            result = parser.parse(Path(tmp_path))
            assert len(result.entities) == 1
            assert result.entities[0].name == "foo"
            assert result.entities[0].kind == "function"
        finally:
            Path(tmp_path).unlink()

    def test_parse_relationships_from_edges(self) -> None:
        """Test that parse() extracts relationships from edges."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(
                {
                    "nodes": [],
                    "edges": [{"source": "foo", "target": "bar", "type": "calls"}],
                },
                tmp,
            )
            tmp_path = tmp.name

        try:
            parser = GraphParser()
            result = parser.parse(Path(tmp_path))
            assert len(result.relationships) == 1
            assert result.relationships[0].source == "foo"
            assert result.relationships[0].target == "bar"
            assert result.relationships[0].type == "calls"
        finally:
            Path(tmp_path).unlink()

    def test_parse_communities(self) -> None:
        """Test that parse() extracts communities."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(
                {
                    "nodes": [],
                    "edges": [],
                    "communities": [{"name": "community1", "members": ["foo", "bar"]}],
                },
                tmp,
            )
            tmp_path = tmp.name

        try:
            parser = GraphParser()
            result = parser.parse(Path(tmp_path))
            assert len(result.communities) == 1
            assert result.communities[0].name == "community1"
        finally:
            Path(tmp_path).unlink()

    def test_parse_empty_graph(self) -> None:
        """Test that parse() handles empty graph data."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump({"nodes": [], "edges": []}, tmp)
            tmp_path = tmp.name

        try:
            parser = GraphParser()
            result = parser.parse(Path(tmp_path))
            assert len(result.entities) == 0
            assert len(result.relationships) == 0
            assert len(result.communities) == 0
        finally:
            Path(tmp_path).unlink()

    def test_parse_malformed_json(self) -> None:
        """Test that parse() raises on malformed JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write("{invalid json}")
            tmp_path = tmp.name

        try:
            parser = GraphParser()
            with pytest.raises(ValueError):
                parser.parse(Path(tmp_path))
        finally:
            Path(tmp_path).unlink()

    def test_parse_missing_file(self) -> None:
        """Test that parse() raises on missing file."""
        parser = GraphParser()
        with pytest.raises(FileNotFoundError):
            parser.parse(Path("/nonexistent/graph.json"))
