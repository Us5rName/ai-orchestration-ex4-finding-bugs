"""StructuredEvidence — one piece of structured evidence in an investigation run.

Traceability: [PRD-CE §Result Contract], [TODO P6-R02-REV]
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StructuredEvidence:
    """One piece of structured evidence collected during an investigation run.

    Represents a source anchor, graph node, vault note, or combination that
    influenced the diagnosis. Missing anchors must use empty string rather
    than being omitted.
    """

    source_file: str = ""
    line_start: int = 0
    line_end: int = 0
    symbol: str = ""
    excerpt_hash: str = ""
    graph_node: str = ""
    edge_type: str = ""
    vault_note: str = ""
    dependency_path: str = ""
    ranking_score: float = 0.0
    sent_to_model: bool = False
    in_final_diagnosis: bool = False
