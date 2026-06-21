"""Comparison request helpers."""

from __future__ import annotations

from dataclasses import replace

from ex04.shared.types_request import ComparisonRequest


def strategy_request(
    request: ComparisonRequest,
    mode: str,
    *,
    run_id: str | None = None,
) -> ComparisonRequest:
    """Return a request specialized for one comparison strategy."""
    return replace(
        request,
        run_id=run_id or request.run_id,
        mode=mode,
        strategy_artifact_dir=mode,
    )
