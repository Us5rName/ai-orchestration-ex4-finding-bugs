"""Unit tests for src/ex04/sdk/_comparison_inputs.py.

Verifies deterministic source-file discovery, exclusion rules,
limit enforcement, and error handling.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04.sdk._comparison_inputs import discover_source_files


@pytest.fixture
def codebase(tmp_path: Path) -> Path:
    """Create a representative Python codebase tree."""
    # Eligible files
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "utils.py").write_text("# util", encoding="utf-8")
    (sub / "core.py").write_text("# core", encoding="utf-8")

    # Excluded directories
    for excluded in (".venv", "__pycache__", "build", ".git"):
        excl_dir = tmp_path / excluded
        excl_dir.mkdir()
        (excl_dir / "hidden.py").write_text("# hidden", encoding="utf-8")

    return tmp_path


class TestDiscoverSourceFiles:
    """Tests for discover_source_files helper."""

    def test_finds_eligible_files(self, codebase: Path) -> None:
        result = discover_source_files(codebase)
        names = [f.name for f in result]
        assert "main.py" in names
        assert "utils.py" in names
        assert "core.py" in names

    def test_excludes_venv_files(self, codebase: Path) -> None:
        result = discover_source_files(codebase)
        for f in result:
            assert ".venv" not in f.parts

    def test_excludes_pycache_files(self, codebase: Path) -> None:
        result = discover_source_files(codebase)
        for f in result:
            assert "__pycache__" not in f.parts

    def test_excludes_build_files(self, codebase: Path) -> None:
        result = discover_source_files(codebase)
        for f in result:
            assert "build" not in f.parts

    def test_deterministic_order(self, codebase: Path) -> None:
        first = discover_source_files(codebase)
        second = discover_source_files(codebase)
        assert first == second

    def test_nested_files_found(self, codebase: Path) -> None:
        result = discover_source_files(codebase)
        paths = [str(f) for f in result]
        assert any("pkg" in p for p in paths)

    def test_nonexistent_target_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            discover_source_files(tmp_path / "does_not_exist")

    def test_file_target_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "single.py"
        f.write_text("x = 1", encoding="utf-8")
        with pytest.raises(NotADirectoryError):
            discover_source_files(f)

    def test_no_python_files_raises(self, tmp_path: Path) -> None:
        (tmp_path / "readme.txt").write_text("nothing", encoding="utf-8")
        with pytest.raises(FileNotFoundError, match="No eligible Python"):
            discover_source_files(tmp_path)

    def test_limit_applied(self, codebase: Path) -> None:
        result = discover_source_files(codebase, config={"comparison": {"naive_file_limit": 1}})
        assert len(result) == 1

    def test_limit_none_returns_all(self, codebase: Path) -> None:
        all_files = discover_source_files(codebase)
        limited = discover_source_files(codebase, config={"comparison": {}})
        assert all_files == limited

    def test_invalid_limit_zero_raises(self, codebase: Path) -> None:
        with pytest.raises(ValueError):
            discover_source_files(codebase, config={"comparison": {"naive_file_limit": 0}})

    def test_invalid_limit_negative_raises(self, codebase: Path) -> None:
        with pytest.raises(ValueError):
            discover_source_files(codebase, config={"comparison": {"naive_file_limit": -5}})

    def test_invalid_limit_string_raises(self, codebase: Path) -> None:
        with pytest.raises(ValueError):
            discover_source_files(codebase, config={"comparison": {"naive_file_limit": "bad"}})

    def test_returns_path_objects(self, codebase: Path) -> None:
        result = discover_source_files(codebase)
        assert all(isinstance(f, Path) for f in result)
