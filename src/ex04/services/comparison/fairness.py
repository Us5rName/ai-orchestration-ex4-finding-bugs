"""Runtime fairness enforcement for controlled comparison experiments.

Verifies that naive and graph-guided ExperimentConfig instances are
identical on all controlled fields before any provider call is made.
Also provides a deterministic configuration hash for manifest linkage.

Traceability: [PRD-CE §Fairness], [TODO P6-R05]
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from ex04.shared.types_experiment import ExperimentConfig

_CONTROLLED_FIELDS = (
    "provider",
    "model",
    "system_prompt",
    "max_model_calls",
    "max_tool_calls",
    "max_iterations",
    "token_budget",
    "prompt_version",
)


class FairnessViolationError(RuntimeError):
    """Raised when controlled fields differ between naive and guided configs."""


class FairnessEnforcer:
    """Enforce experiment fairness before any provider call.

    Compares all controlled fields between the naive and graph-guided
    ExperimentConfig instances. If any field differs, raises
    FairnessViolationError with the name of the offending field.
    """

    def check(
        self, naive_cfg: ExperimentConfig, guided_cfg: ExperimentConfig
    ) -> None:
        """Assert that all controlled fields are identical.

        Args:
            naive_cfg: Configuration for the naive run.
            guided_cfg: Configuration for the graph-guided run.

        Raises:
            FairnessViolationError: If any controlled field differs.
        """
        naive_dict = asdict(naive_cfg)
        guided_dict = asdict(guided_cfg)
        for field in _CONTROLLED_FIELDS:
            if naive_dict[field] != guided_dict[field]:
                raise FairnessViolationError(
                    f"Fairness violation: field '{field}' differs between "
                    f"naive ({naive_dict[field]!r}) and guided "
                    f"({guided_dict[field]!r})."
                )

    @staticmethod
    def config_hash(config: ExperimentConfig) -> str:
        """Return a stable 16-character SHA-256 prefix of the config.

        Only controlled fields are hashed to produce a stable key that
        is identical for any two fair configs.
        """
        controlled = {f: getattr(config, f) for f in _CONTROLLED_FIELDS}
        serialised = json.dumps(controlled, sort_keys=True)
        return hashlib.sha256(serialised.encode()).hexdigest()[:16]
