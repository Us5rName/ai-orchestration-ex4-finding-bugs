"""Graph Guided Runner — executes graph-guided investigation workflow.

Uses bug-report-sensitive ranked graph entities, relationships, source
anchors, and vault notes to provide focused context. Ranking uses four
weighted signals: bug-report term match, file/path match, node type
relevance, and degree centrality.

Context acquisition strategy: graph → vault → targeted source anchors.
This is the independent variable vs. NaiveRunner.

Traceability: [PRD-GGI §Contracts], [TODO P6-R04], [PRD-CE §12.3]
"""

from __future__ import annotations

import time
from pathlib import Path

from ex04.services.comparison.ranking import rank_entities
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types import GraphData, RunMetrics

_MAX_ENTITIES = 20
_MAX_VAULT_NOTES = 3


class GraphGuidedRunner:
    """Run a focused graph/vault-guided comparison pass.

    Context is derived exclusively from graph_data and the vault — no
    filesystem scan of source files is performed. Entities are ranked
    using multiple signals from the bug report, not just graph degree.
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
        graph_context, source_anchors, limitations = self._graph_context(
            graph_data, bug_report
        )
        vault_context, files_read = self._vault_context(vault_path)

        content = f"Bug:\n{bug_report}\n\n{graph_context}\n\n{vault_context}"
        if limitations:
            content += f"\n\nLimitations: {'; '.join(limitations)}"

        response = self.gatekeeper.send(
            self.provider,
            [{"role": "user", "content": content}],
        )
        return RunMetrics(
            tokens_used=response.input_tokens + response.output_tokens,
            files_read=files_read,
            iterations=1,
            time_seconds=time.perf_counter() - started,
            found_root_cause=bool(response.text.strip()),
        )

    @staticmethod
    def _graph_context(
        graph_data: GraphData | None, bug_report: str
    ) -> tuple[str, list[str], list[str]]:
        """Build multi-signal ranked entity context with source anchors.

        Returns:
            Tuple of (context_text, source_anchors, limitations).
        """
        if graph_data is None:
            return "Graph: unavailable", [], ["Graph data not provided."]

        ranked = rank_entities(
            graph_data.entities,
            graph_data.relationships,
            bug_report,
            _MAX_ENTITIES,
        )

        anchors: list[str] = []
        lines = ["Graph entities (multi-signal ranked):"]
        missing_anchor_count = 0

        for entity, score in ranked:
            if entity.file_path:
                anchor = f"{entity.file_path}:{entity.line_range[0]}"
                anchors.append(f"{entity.file_path}:{entity.line_range[0]}-{entity.line_range[1]}")
            else:
                anchor = "unknown"
                missing_anchor_count += 1
            lines.append(
                f"  - {entity.name} [{entity.kind}] score={score:.2f} anchor={anchor}"
            )

        rels_relevant = graph_data.relationships[:15]
        if rels_relevant:
            lines.append("Relationships:")
            for r in rels_relevant:
                lines.append(f"  {r.source} --{r.type}--> {r.target}")

        limitations: list[str] = []
        if missing_anchor_count:
            limitations.append(
                f"{missing_anchor_count} entities lack a valid source anchor."
            )

        return "\n".join(lines), anchors, limitations

    @staticmethod
    def _vault_context(vault_path: Path | None) -> tuple[str, int]:
        """Navigate vault: index.md → hot.md → component notes."""
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
