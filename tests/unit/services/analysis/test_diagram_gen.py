"""Tests for DiagramGenerator — validates mermaid saving and syntax checks."""

from pathlib import Path

from ex04.services.analysis.diagram_gen import DiagramGenerator


class TestDiagramGeneratorSaveDiagram:
    """Tests for DiagramGenerator.save_diagram method."""

    def test_save_diagram_creates_file(self, tmp_path: Path) -> None:
        """Test that save_diagram creates the output file."""
        gen = DiagramGenerator()
        content = "```mermaid\ngraph TD\n    A --> B\n```"
        result_path = gen.save_diagram(content, "test_diagram", tmp_path)

        assert result_path.exists()
        assert result_path.name == "test_diagram.md"

    def test_save_diagram_writes_content(self, tmp_path: Path) -> None:
        """Test that save_diagram writes the correct content."""
        gen = DiagramGenerator()
        content = "```mermaid\ngraph TD\n    A --> B\n```"
        result_path = gen.save_diagram(content, "test_diagram", tmp_path)

        assert result_path.read_text(encoding="utf-8") == content

    def test_save_diagram_returns_path(self, tmp_path: Path) -> None:
        """Test that save_diagram returns a Path object."""
        gen = DiagramGenerator()
        content = "```mermaid\ngraph TD\n    A --> B\n```"
        result = gen.save_diagram(content, "test_diagram", tmp_path)

        assert isinstance(result, Path)

    def test_save_diagram_creates_subdirectory(self, tmp_path: Path) -> None:
        """Test that save_diagram creates parent directories if needed."""
        gen = DiagramGenerator()
        content = "```mermaid\ngraph TD\n    A --> B\n```"
        output_dir = tmp_path / "output" / "diagrams"
        result_path = gen.save_diagram(content, "test_diagram", output_dir)

        assert result_path.exists()
        assert "output" in result_path.parts
        assert "diagrams" in result_path.parts


class TestDiagramGeneratorValidateMermaid:
    """Tests for DiagramGenerator.validate_mermaid method."""

    def test_validate_valid_block_diagram(self) -> None:
        """Test validation of a valid mermaid block diagram."""
        content = "```mermaid\nblock\n    A --> B\n```"
        assert DiagramGenerator.validate_mermaid(content) is True

    def test_validate_valid_class_diagram(self) -> None:
        """Test validation of a valid mermaid class diagram."""
        content = "```mermaid\nclassDiagram\n    class A\n```"
        assert DiagramGenerator.validate_mermaid(content) is True

    def test_validate_valid_graph_diagram(self) -> None:
        """Test validation of a valid mermaid graph diagram."""
        content = "```mermaid\ngraph TD\n    A --> B\n```"
        assert DiagramGenerator.validate_mermaid(content) is True

    def test_validate_missing_fenced_code(self) -> None:
        """Test validation fails when mermaid keyword is not in fenced code block."""
        content = "mermaid\ngraph TD\n    A --> B"
        assert DiagramGenerator.validate_mermaid(content) is False

    def test_validate_unbalanced_fences(self) -> None:
        """Test validation fails with unbalanced code fences."""
        content = "```mermaid\ngraph TD\n    A --> B\n"
        assert DiagramGenerator.validate_mermaid(content) is False

    def test_validate_empty_content(self) -> None:
        """Test validation fails on empty content."""
        assert DiagramGenerator.validate_mermaid("") is False

    def test_validate_none_content(self) -> None:
        """Test validation fails on None content."""
        assert DiagramGenerator.validate_mermaid(None) is False
