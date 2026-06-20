"""Runtime fairness enforcement for controlled comparison experiments."""

from __future__ import annotations

from dataclasses import asdict

from ex04.shared.types_request import CONTROLLED, ComparisonRequest, classified_field_names


class FairnessViolationError(RuntimeError):
    """Raised when controlled fields differ between naive and guided configs."""


class FairnessEnforcer:
    """Enforce experiment fairness before any provider call.

    Compares all fields classified as controlled. If any differs, raises
    FairnessViolationError with the field name and both values.
    Must be called before gatekeeper.send() — no exceptions.
    """

    def check(
        self, naive_req: ComparisonRequest, guided_req: ComparisonRequest
    ) -> None:
        """Assert that all controlled fields are identical.

        Args:
            naive_req: ComparisonRequest for the naive run.
            guided_req: ComparisonRequest for the graph-guided run.

        Raises:
            FairnessViolationError: If any controlled field differs.
        """
        naive_dict, guided_dict = asdict(naive_req), asdict(guided_req)
        for field in classified_field_names(CONTROLLED):
            naive_val, guided_val = naive_dict[field], guided_dict[field]
            if naive_val != guided_val:
                raise FairnessViolationError(
                    f"Fairness violation: field '{field}' differs between "
                    f"naive ({naive_val!r}) and guided ({guided_val!r})."
                )

    @staticmethod
    def config_hash(req: ComparisonRequest) -> str:
        """Return the full stable SHA-256 digest of the controlled fields."""
        return req.controlled_config_hash()
