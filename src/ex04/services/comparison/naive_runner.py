"""Naive Runner — executes naive investigation workflow."""

from __future__ import annotations

import time
from pathlib import Path

from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types import RunMetrics


class NaiveRunner:
    """Run an unfocused baseline over raw source files."""

    def __init__(self, gatekeeper: GatekeeperInterface, provider: str = "openai") -> None:
        """Initialize with Gatekeeper dependency."""
        self.gatekeeper = gatekeeper
        self.provider = provider

    def run(self, bug_report: str, source_files: list[Path]) -> RunMetrics:
        """Dump raw source context into one Gatekeeper call and measure it."""
        started = time.perf_counter()
        readable = [path for path in source_files if path.is_file()]
        context = "\n\n".join(f"--- {path} ---\n{path.read_text(encoding='utf-8')}" for path in readable)
        response = self.gatekeeper.send(
            self.provider,
            [{"role": "user", "content": f"Find and fix this bug:\n{bug_report}\n\n{context}"}],
        )
        return RunMetrics(
            tokens_used=response.input_tokens + response.output_tokens,
            files_read=len(readable),
            iterations=1,
            time_seconds=time.perf_counter() - started,
            found_root_cause=bool(response.text.strip()),
        )
