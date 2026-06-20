"""Graph Guided Runner — executes graph-guided investigation workflow."""

from __future__ import annotations

import time
from pathlib import Path

from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types import GraphData, RunMetrics


class GraphGuidedRunner:
    """Run a focused graph/vault-guided comparison pass."""

    def __init__(self, gatekeeper: GatekeeperInterface, provider: str = "openai") -> None:
        """Initialize with Gatekeeper dependency."""
        self.gatekeeper = gatekeeper
        self.provider = provider

    def run(
        self,
        bug_report: str,
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> RunMetrics:
        """Use graph entities and vault notes before asking the model."""
        started = time.perf_counter()
        graph_context = self._graph_context(graph_data)
        vault_context, files_read = self._vault_context(vault_path)
        response = self.gatekeeper.send(
            self.provider,
            [{"role": "user", "content": f"Bug:\n{bug_report}\n\n{graph_context}\n\n{vault_context}"}],
        )
        return RunMetrics(
            tokens_used=response.input_tokens + response.output_tokens,
            files_read=files_read,
            iterations=1,
            time_seconds=time.perf_counter() - started,
            found_root_cause=bool(response.text.strip()),
        )

    @staticmethod
    def _graph_context(graph_data: GraphData | None) -> str:
        """Build compact graph context from entity names."""
        if graph_data is None:
            return "Graph: unavailable"
        entities = ", ".join(entity.name for entity in graph_data.entities[:20])
        return f"Graph entities: {entities}"

    @staticmethod
    def _vault_context(vault_path: Path | None) -> tuple[str, int]:
        """Read focused index/hot vault notes when available."""
        if vault_path is None or not vault_path.is_dir():
            return "Vault: unavailable", 0
        notes = [path for path in [vault_path / "index.md", vault_path / "hot.md"] if path.is_file()]
        text = "\n\n".join(note.read_text(encoding="utf-8") for note in notes)
        return text, len(notes)
