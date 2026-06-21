"""Immutable JSONL trace recorder for comparison investigations."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ex04.services.comparison.budget import BudgetLedger


@dataclass
class TraceRecorder:
    """Record actual operations and persist them as JSONL."""

    run_id: str
    events: list[dict[str, Any]] = field(default_factory=list)
    path: Path | None = None
    sha256: str = ""

    def record(self, operation: str, ledger: BudgetLedger, **details: object) -> None:
        """Append one operation event using the ledger's current counters."""
        event: dict[str, Any] = {
            "sequence": len(self.events) + 1,
            "operation": operation,
            **details,
            **ledger.snapshot(),
        }
        self.events.append(event)

    def budget_stop(self, ledger: BudgetLedger, reason: str) -> None:
        """Record a terminal budget-stop event."""
        self.record("budget_stop", ledger, reason=reason)

    def persist(self, artifact_root: Path) -> tuple[Path, str]:
        """Write JSONL trace under artifacts/runs/<run-id>/traces."""
        trace_dir = artifact_root / "runs" / self.run_id / "traces"
        trace_dir.mkdir(parents=True, exist_ok=True)
        self.path = trace_dir / "investigation.jsonl"
        if self.path.exists():
            raise FileExistsError(f"Trace already exists: {self.path}")
        text = "".join(json.dumps(e, sort_keys=True, default=str) + "\n" for e in self.events)
        self.path.write_text(text, encoding="utf-8")
        self.sha256 = hashlib.sha256(text.encode()).hexdigest()
        return self.path, self.sha256
