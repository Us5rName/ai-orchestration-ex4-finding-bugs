"""Tests for deferred ComparisonService facade."""

import pytest

from ex04.services.comparison.service import ComparisonService


def test_comparison_service_is_deferred_until_phase_6() -> None:
    service = ComparisonService()
    with pytest.raises(NotImplementedError, match="Phase 6"):
        service.run_comparison("bug", [])
