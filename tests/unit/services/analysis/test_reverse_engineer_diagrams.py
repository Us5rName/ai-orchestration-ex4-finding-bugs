"""Diagram tests for ReverseEngineer (T4.16).

Tests extract_block_schema() and extract_oop_schema() methods.
"""

from __future__ import annotations

from ex04.services.analysis.reverse_engineer import ReverseEngineer
from ex04.shared.types import Entity, GraphData, Relationship


class TestReverseEngineerExtractBlockSchema:
    """Tests for ReverseEngineer.extract_block_schema() method."""

    def test_extract_block_schema_returns_mermaid(self) -> None:
        """Test that extract_block_schema() returns Mermaid diagram."""
        entities = [
            Entity(name="AuthService", kind="class", file_path="auth.py"),
            Entity(name="Database", kind="class", file_path="db.py"),
        ]
        relationships = [
            Relationship(source="AuthService", target="Database", type="uses"),
        ]
        graph_data = GraphData(entities=entities, relationships=relationships)
        engine = ReverseEngineer()
        result = engine.extract_block_schema(graph_data)

        assert "```mermaid" in result
        assert "block" in result.lower()

    def test_extract_block_schema_groups_by_file(self) -> None:
        """Test that extract_block_schema() groups entities by file."""
        entities = [
            Entity(name="Auth", kind="class", file_path="auth.py"),
            Entity(name="User", kind="function", file_path="auth.py"),
            Entity(name="DB", kind="class", file_path="db.py"),
        ]
        graph_data = GraphData(entities=entities)
        engine = ReverseEngineer()
        result = engine.extract_block_schema(graph_data)

        assert "auth.py" in result or "auth" in result.lower()


class TestReverseEngineerExtractOopSchema:
    """Tests for ReverseEngineer.extract_oop_schema() method."""

    def test_extract_oop_schema_returns_class_diagram(self) -> None:
        """Test that extract_oop_schema() returns a class diagram."""
        entities = [
            Entity(name="BaseModel", kind="class", file_path="models.py"),
            Entity(name="User", kind="class", file_path="models.py"),
        ]
        relationships = [
            Relationship(source="User", target="BaseModel", type="inherits"),
        ]
        graph_data = GraphData(entities=entities, relationships=relationships)
        engine = ReverseEngineer()
        result = engine.extract_oop_schema(graph_data)

        assert "classDiagram" in result
        assert "User" in result
        assert "BaseModel" in result

    def test_extract_oop_schema_shows_inheritance(self) -> None:
        """Test that extract_oop_schema() shows inheritance relationships."""
        relationships = [
            Relationship(source="Child", target="Parent", type="inherits"),
        ]
        graph_data = GraphData(relationships=relationships)
        engine = ReverseEngineer()
        result = engine.extract_oop_schema(graph_data)

        assert "Child" in result
        assert "Parent" in result
