"""Runtime fairness enforcement for controlled comparison experiments.

Verifies that naive and graph-guided ComparisonRequest instances are identical
on every field classified as controlled before any provider call.

Delegates to the canonical parity mechanism in parity.py — there is exactly
one production fingerprint implementation.
"""

from __future__ import annotations

from dataclasses import asdict

from ex04.services.comparison.parity import ParityError, assert_request_parity
from ex04.shared.types_request import CONTROLLED, ComparisonRequest, classified_field_names


class FairnessViolationError(RuntimeError):
    """Raised when controlled fields differ between naive and guided configs."""


class FairnessEnforcer:
    """Enforce experiment fairness before any provider call.

    Delegates fingerprint comparison to the canonical assert_request_parity()
    in parity.py. On mismatch, re-raises as FairnessViolationError with
    field-level diagnostic detail for actionable error messages.
    """

    def check(
        self,
        naive_req: ComparisonRequest,
        guided_req: ComparisonRequest,
    ) -> None:
        """Assert all controlled fields are identical via canonical parity check."""
        try:
            assert_request_parity(naive_req, guided_req)
        except ParityError:
            naive_dict, guided_dict = asdict(naive_req), asdict(guided_req)
            for fname in classified_field_names(CONTROLLED):
                naive_val, guided_val = naive_dict[fname], guided_dict[fname]
                if naive_val != guided_val:
                    raise FairnessViolationError(
                        f"Fairness violation: field '{fname}' differs between "
                        f"naive ({naive_val!r}) and guided ({guided_val!r})."
                    ) from None

    @staticmethod
    def config_hash(req: ComparisonRequest) -> str:
        """Return the full stable SHA-256 digest of the controlled fields."""
        return req.controlled_config_hash()
