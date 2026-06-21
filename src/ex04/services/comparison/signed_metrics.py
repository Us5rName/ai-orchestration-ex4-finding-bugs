"""Signed metrics computation for comparison experiments.

Computes deltas between naive and graph-guided runs without clamping
negative values — a regression is valid evidence and must remain visible.

Traceability: [PRD-CE §Metrics], [TODO T6.07]
"""

from __future__ import annotations

from ex04.services.comparison.metrics_utils import pct_savings
from ex04.shared.types import RunMetrics
from ex04.shared.types_experiment import SignedMetrics


class SignedMetricsCalculator:
    """Compute signed deltas between naive and graph-guided runs.

    Negative deltas (regressions) are preserved and never clamped to zero.
    Division-by-zero cases return None rather than raising.
    """

    def compute(self, naive: RunMetrics, guided: RunMetrics) -> SignedMetrics:
        """Return SignedMetrics with absolute values and signed deltas.

        Args:
            naive: Metrics from the naive investigation run.
            guided: Metrics from the graph-guided investigation run.

        Returns:
            SignedMetrics with deltas and percentage savings (may be negative).
        """
        naive_tok = naive.tokens_used if naive.tokens_used > 0 else None
        guided_tok = guided.tokens_used if guided.tokens_used > 0 else None
        tok_delta = (guided_tok - naive_tok) if (naive_tok and guided_tok) else None
        tok_pct = pct_savings(naive.tokens_used, guided.tokens_used, None)

        return SignedMetrics(
            naive_tokens=naive_tok,
            guided_tokens=guided_tok,
            token_delta=tok_delta,
            token_savings_pct=tok_pct,
            naive_files=naive.files_read,
            guided_files=guided.files_read,
            file_delta=guided.files_read - naive.files_read,
            file_savings_pct=pct_savings(naive.files_read, guided.files_read, None),
            naive_iterations=naive.iterations,
            guided_iterations=guided.iterations,
            iteration_delta=guided.iterations - naive.iterations,
            naive_duration=naive.time_seconds,
            guided_duration=guided.time_seconds,
            duration_delta=guided.time_seconds - naive.time_seconds,
            naive_correct=naive.found_root_cause,
            guided_correct=guided.found_root_cause,
            limitations=self._limitations(naive_tok, guided_tok),
        )

    @staticmethod
    def _limitations(naive_tok: int | None, guided_tok: int | None) -> list[str]:
        """List known limitations of this metrics record."""
        lims: list[str] = []
        if naive_tok is None or guided_tok is None:
            lims.append("Token telemetry unavailable — cost comparison skipped.")
        return lims
