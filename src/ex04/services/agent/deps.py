"""Shared dependencies for agent workflow nodes."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ex04.shared.gatekeeper import GatekeeperInterface


@dataclass(frozen=True)
class NodeDeps:
    """Dependency bundle passed to agent workflow nodes."""

    gatekeeper: GatekeeperInterface | None = None
    provider: str = "openai"
    target_path: Path = Path(".")
    context_limit: int = 8000
    max_suspects: int = 5
    test_command: list[str] = field(default_factory=lambda: ["uv", "run", "pytest", "-q"])
