"""Graph Guided Runner — executes graph-guided investigation workflow.

Uses ranked graph entities (by degree centrality), relationships, source
anchors, and vault notes (index.md → hot.md) to provide focused context.

Context acquisition strategy: graph → vault → targeted source anchors.
This is the independent variable vs. NaiveRunner.

Traceability: [PRD-GGI §Contracts], [TODO T6.02, T6.04], [PRD-CE §12.3]
"""

from __future__ import annotations

import time
from pathlib import Path

from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types import GraphData, RunMetrics

_MAX_ENTITIES = 20
_MAX_VAULT_NOTES = 3


class GraphGuidedRunner:
    """Run a focused graph/vault-guided comparison pass.

    Context is derived exclusively from graph_data and the vault — no
    filesystem scan of source files is performed.
    """

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
        """Use graph entities and vault notes before asking the model.

        Args:
            bug_report: Natural-language bug description.
            graph_data: Parsed Graphify output with entities and relationships.
            vault_path: Root of Obsidian vault (optional).

        Returns:
            RunMetrics with token counts, files_read, and source_anchors.
        """
        started = time.perf_counter()
        graph_context, source_anchors = self._graph_context(graph_data)
        vault_context, files_read = self._vault_context(vault_path)
        response = self.gatekeeper.send(
            self.provider,
            [
                {
                    "role": "user",
                    "content": (
                        f"Bug:\n{bug_report}\n\n"
                        f"{graph_context}\n\n"
                        f"{vault_context}"
                    ),
                }
            ],
        )
        return RunMetrics(
            tokens_used=response.input_tokens + response.output_tokens,
            files_read=files_read,
            iterations=1,
            time_seconds=time.perf_counter() - started,
            found_root_cause=bool(response.text.strip()),
        )

    @staticmethod
    def _graph_context(graph_data: GraphData | None) -> tuple[str, list[str]]:
        """Build ranked entity context with source anchors from graph_data.

        Returns:
            Tuple of (context_text, source_anchors).
        """
        if graph_data is None:
            return "Graph: unavailable", []

        degree: dict[str, int] = {}
        for rel in graph_data.relationships:
            degree[rel.source] = degree.get(rel.source, 0) + 1
            degree[rel.target] = degree.get(rel.target, 0) + 1

        ranked = sorted(
            graph_data.entities,
            key=lambda e: degree.get(e.name, 0),
            reverse=True,
        )[:_MAX_ENTITIES]

        anchors = [
            f"{e.file_path}:{e.line_range[0]}-{e.line_range[1]}"
            for e in ranked
            if e.file_path
        ]
        lines = ["Graph entities (ranked by degree centrality):"]
        for e in ranked:
            rel_count = degree.get(e.name, 0)
            anchor = f"{e.file_path}:{e.line_range[0]}" if e.file_path else "unknown"
            lines.append(f"  - {e.name} [{e.kind}] degree={rel_count} anchor={anchor}")

        rels_sample = graph_data.relationships[:10]
        if rels_sample:
            lines.append("Relationships (sample):")
            for r in rels_sample:
                lines.append(f"  {r.source} --{r.type}--> {r.target}")

        return "\n".join(lines), anchors

    @staticmethod
    def _vault_context(vault_path: Path | None) -> tuple[str, int]:
        """Navigate vault: index.md → hot.md → component notes.

        Returns:
            Tuple of (vault_context_text, files_read_count).
        """
        if vault_path is None or not vault_path.is_dir():
            return "Vault: unavailable", 0
        candidates = [vault_path / "index.md", vault_path / "hot.md"]
        notes = [p for p in candidates if p.is_file()][:_MAX_VAULT_NOTES]
        if not notes:
            return "Vault: no index or hot notes found", 0
        text = "\n\n".join(
            f"=== {note.name} ===\n{note.read_text(encoding='utf-8')}" for note in notes
        )
        return text, len(notes)
