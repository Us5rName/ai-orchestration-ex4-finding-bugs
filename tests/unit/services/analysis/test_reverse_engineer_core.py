"""Core tests for ReverseEngineer (T4.16).

Tests the main reverse_engineer() method and empty graph handling.
"""

from __future__ import annotations

from ex04.services.analysis.reverse_engineer import ReverseEngineer
from ex04.shared.types import Community, Entity, GraphData, Relationship


class TestReverseEngineer:
    """Tests for ReverseEngineer.reverse_engineer() method."""

    def test_reverse_engineer_returns_string(self) -> None:
        """Test that reverse_engineer() returns a string."""
        graph_data = GraphData()
        engine = ReverseEngineer()
        result = engine.reverse_engineer(graph_data)

        assert isinstance(result, str)

    def test_reverse_engineer_includes_block_diagram(self) -> None:
        """Test that reverse_engineer() includes a Mermaid block diagram."""
        entities = [
            Entity(name="AuthService", kind="class", file_path="auth.py"),
            Entity(name="UserManager", kind="class", file_path="users.py"),
            Entity(name="Database", kind="class", file_path="db.py"),
        ]
        relationships = [
            Relationship(source="AuthService", target="Database", type="uses"),
            Relationship(source="UserManager", target="Database", type="uses"),
        ]
        graph_data = GraphData(entities=entities, relationships=relationships)
        engine = ReverseEngineer()
        result = engine.reverse_engineer(graph_data)

        assert "```mermaid" in result
        assert "block" in result.lower()

    def test_reverse_engineer_includes_oop_diagram(self) -> None:
        """Test that reverse_engineer() includes a Mermaid class diagram."""
        entities = [
            Entity(name="BaseModel", kind="class", file_path="models.py"),
            Entity(name="User", kind="class", file_path="models.py"),
        ]
        relationships = [
            Relationship(source="User", target="BaseModel", type="inherits"),
        ]
        graph_data = GraphData(entities=entities, relationships=relationships)
        engine = ReverseEngineer()
        result = engine.reverse_engineer(graph_data)

        assert "```mermaid" in result
        assert "classDiagram" in result

    def test_reverse_engineer_handles_empty_graph(self) -> None:
        """Test that reverse_engineer() handles empty graph gracefully."""
        graph_data = GraphData(entities=[], relationships=[], communities=[])
        engine = ReverseEngineer()
        result = engine.reverse_engineer(graph_data)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_reverse_engineer_includes_entity_summary(self) -> None:
        """Test that reverse_engineer() includes entity summary section."""
        entities = [
            Entity(name="Auth", kind="class", file_path="auth.py"),
            Entity(name="User", kind="function", file_path="auth.py"),
        ]
        graph_data = GraphData(entities=entities)
        engine = ReverseEngineer()
        result = engine.reverse_engineer(graph_data)

        assert "Entity Summary" in result or "Entities" in result
        assert "Auth" in result

    def test_reverse_engineer_includes_relationships(self) -> None:
        """Test that reverse_engineer() includes relationships section."""
        relationships = [
            Relationship(source="A", target="B", type="calls"),
            Relationship(source="B", target="C", type="calls"),
        ]
        graph_data = GraphData(relationships=relationships)
        engine = ReverseEngineer()
        result = engine.reverse_engineer(graph_data)

        assert "Relationships" in result or "Relations" in result
        assert "A" in result
        assert "B" in result

    def test_reverse_engineer_includes_communities(self) -> None:
        """Test that reverse_engineer() includes community analysis."""
        communities = [
            Community(name="Auth Module", entities=["Auth", "User"], size=2),
            Community(name="Data Module", entities=["DB", "Cache"], size=2),
        ]
        graph_data = GraphData(communities=communities)
        engine = ReverseEngineer()
        result = engine.reverse_engineer(graph_data)

        assert "Auth Module" in result
        assert "Data Module" in result

    def test_reverse_engineer_identifies_patterns(self) -> None:
        """Test that reverse_engineer() identifies common patterns."""
        entities = [
            Entity(name="Repository", kind="class", file_path="repo.py"),
            Entity(name="BaseRepository", kind="class", file_path="repo.py"),
            Entity(name="UserRepo", kind="class", file_path="repo.py"),
        ]
        relationships = [
            Relationship(source="UserRepo", target="BaseRepository", type="inherits"),
        ]
        graph_data = GraphData(entities=entities, relationships=relationships)
        engine = ReverseEngineer()
        result = engine.reverse_engineer(graph_data)

        assert "Pattern" in result or "pattern" in result
