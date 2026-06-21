"""Bug-report-sensitive entity ranking for graph-guided investigation.

Ranks graph entities using four weighted signals:
  - Bug-report term match (0.40) — strongest signal
  - File/path keyword match (0.20)
  - Node type relevance (0.10): function > class > file > module > other
  - Degree centrality (0.30) — graph connectivity

Limitations: ranking is heuristic; entity kind labels depend on Graphify
conventions; term extraction uses simple word splitting (no NLP).

Traceability: [PRD-GGI §Ranking], [TODO P6-R04]
"""

from __future__ import annotations

import re

from ex04.shared.graph_ops import degree_map
from ex04.shared.types import Entity, Relationship

_KIND_SCORES: dict[str, float] = {
    "function": 1.0,
    "method": 0.9,
    "class": 0.7,
    "file": 0.4,
    "module": 0.3,
}

_STOP_WORDS = frozenset(
    {"the", "and", "for", "with", "that", "this", "from", "when", "not", "are"}
)


def extract_terms(bug_report: str) -> set[str]:
    """Extract meaningful search terms from a bug report string."""
    words = re.findall(r"\b[a-zA-Z_]\w{2,}\b", bug_report.lower())
    return {w for w in words if w not in _STOP_WORDS}


def score_entity(
    entity: Entity,
    bug_report_terms: set[str],
    degree_map: dict[str, int],
    max_degree: int,
) -> float:
    """Compute a weighted relevance score for one graph entity.

    Args:
        entity: Graph entity to score.
        bug_report_terms: Pre-extracted terms from the bug report.
        degree_map: Map of entity name to its degree (relationship count).
        max_degree: Maximum degree in the graph (for normalisation).

    Returns:
        Score in [0.0, 1.0] (higher = more relevant).
    """
    name_lower = entity.name.lower()
    path_lower = (entity.file_path or "").lower()

    # Signal A: term match in entity name (weight 0.40)
    term_hit = any(t in name_lower for t in bug_report_terms)
    sig_term = 0.40 if term_hit else 0.0

    # Signal B: term match in file path (weight 0.20)
    path_hit = any(t in path_lower for t in bug_report_terms)
    sig_path = 0.20 if path_hit else 0.0

    # Signal C: node type relevance (weight 0.10)
    sig_kind = 0.10 * _KIND_SCORES.get(entity.kind.lower(), 0.1)

    # Signal D: normalised degree centrality (weight 0.30)
    deg = degree_map.get(entity.name, 0)
    sig_deg = 0.30 * (deg / max_degree if max_degree > 0 else 0.0)

    return sig_term + sig_path + sig_kind + sig_deg


def rank_entities(
    entities: list[Entity],
    relationships: list[Relationship],
    bug_report: str,
    max_count: int = 20,
) -> list[tuple[Entity, float]]:
    """Return top-N entities sorted by multi-signal relevance score.

    Args:
        entities: All graph entities.
        relationships: All relationships (used for degree calculation).
        bug_report: Natural-language bug description.
        max_count: Maximum number of entities to return.

    Returns:
        List of (entity, score) pairs, highest score first.
    """
    terms = extract_terms(bug_report)
    degrees = degree_map(relationships)

    max_degree = max(degrees.values(), default=1)
    scored = [
        (e, score_entity(e, terms, degrees, max_degree)) for e in entities
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:max_count]
