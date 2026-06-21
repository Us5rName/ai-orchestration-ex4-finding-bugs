"""Shared percentage-savings helper for comparison metrics.

Unifies the identical formula used by MetricsCalculator and
SignedMetricsCalculator, differing only in what to return when the
naive baseline is zero or negative.
"""

from __future__ import annotations

from typing import overload


@overload
def pct_savings(naive: float, guided: float) -> float: ...
@overload
def pct_savings(naive: float, guided: float, zero_result: None) -> float | None: ...


def pct_savings(
    naive: float, guided: float, zero_result: float | None = 0.0
) -> float | None:
    """Return percentage saved (negative = regression).

    Args:
        naive: Baseline metric value.
        guided: Graph-guided metric value.
        zero_result: Value returned when naive is zero or negative.
            Pass ``None`` to get ``None`` instead of a float sentinel.

    Returns:
        ``((naive - guided) / naive) * 100``, or ``zero_result`` when
        ``naive <= 0``.
    """
    if naive <= 0:
        return zero_result
    return ((naive - guided) / naive) * 100
