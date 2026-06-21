"""Shared fixtures for agent node tests."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from ex04.services.agent.nodes.inspect import CodeInspectionNode
from ex04.shared.types_results import Suspect


@pytest.fixture
def temp_target(tmp_path: Path) -> Path:
    """Create a reusable temporary target codebase."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text(
        "def main():\n    print('Hello')\n    result = compute(1, 2)\n    print(result)\n",
        encoding="utf-8",
    )
    (src / "calc.py").write_text(
        "def add(a, b):\n    return a + b\n\ndef compute(x, y):\n    return add(x, y) * 2\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def node(temp_target: Path) -> CodeInspectionNode:
    """CodeInspectionNode with no gatekeeper."""
    return CodeInspectionNode(target_path=temp_target)


@pytest.fixture
def suspect() -> Callable[..., Suspect]:
    """Build a suspect with concise defaults."""

    def _suspect(
        file_path: str = "src/main.py",
        start: int = 1,
        end: int = 2,
        score: float = 0.9,
        reason: str = "",
    ) -> Suspect:
        return Suspect(
            file_path=file_path,
            line_start=start,
            line_end=end,
            score=score,
            reason=reason,
        )

    return _suspect


@pytest.fixture
def inspect_state() -> Callable[..., dict[str, Any]]:
    """Build a CodeInspectionNode state with concise defaults."""

    def _state(suspects: list[Suspect], **extra: Any) -> dict[str, Any]:
        return {"suspects": suspects, "inspected_code": "", **extra}

    return _state
