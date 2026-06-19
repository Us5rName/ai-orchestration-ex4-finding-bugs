"""Result types — provider responses, suspects, investigations, pipelines.

Defines the output structures returned by services and the SDK.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ex04.shared.types_metrics import ComparisonReport, TokenMetrics


@dataclass
class ProviderResponse:
    """Response from an LLM provider call.

    Attributes:
        content: Generated text content.
        input_tokens: Tokens consumed in the request.
        output_tokens: Tokens consumed in the response.
        model: Model that generated the response.
        raw: Raw API response dict (for debugging).
    """

    content: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Suspect:
    """A suspect code location ranked by likelihood of containing a bug.

    Attributes:
        file_path: Source file path.
        line_start: Starting line number.
        line_end: Ending line number.
        score: Ranking score (higher = more likely).
        reason: Explanation for the ranking.
    """

    file_path: str
    line_start: int
    line_end: int
    score: float = 0.0
    reason: str = ""


@dataclass
class InvestigationResult:
    """Result of a full bug investigation by the agent.

    Attributes:
        root_cause: Identified root cause description.
        suspects: Ranked list of suspect locations.
        proposed_fix: Suggested code fix.
        fix_applied: Whether the fix was successfully applied.
        test_results: Test execution results dict.
        token_usage: Token metrics for the investigation.
    """

    root_cause: str = ""
    suspects: list[Suspect] = field(default_factory=list)
    proposed_fix: str = ""
    fix_applied: bool = False
    test_results: dict[str, Any] = field(default_factory=dict)
    token_usage: TokenMetrics = field(default_factory=TokenMetrics)


@dataclass
class PipelineResult:
    """Result of the full end-to-end pipeline execution.

    Attributes:
        graph_result: Path to generated graph data.
        vault_result: Path to generated vault.
        investigation: Bug investigation findings.
        comparison: Token comparison report.
        engineering: Reverse engineering results.
    """

    graph_result: str = ""
    vault_result: str = ""
    investigation: InvestigationResult = field(default_factory=InvestigationResult)
    comparison: ComparisonReport = field(default_factory=ComparisonReport)
    engineering: str = ""
