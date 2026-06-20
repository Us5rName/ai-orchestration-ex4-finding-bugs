"""Bug Reporter — generates structured bug analysis reports.

Produces a Markdown report from an InvestigationResult containing
root cause, suspects, fix, test results, and token usage.

## Contract (AnalysisServiceInterface)

| Method | Input | Output | Phase |
|---|---|---|---|
| `generate(investigation)` | InvestigationResult | str | P4 |

Implementation: **Phase 4** (T4.18)
"""

from __future__ import annotations

import logging
from datetime import datetime

from ex04.shared.types_results import InvestigationResult

logger = logging.getLogger(__name__)


class BugReporter:
    """Generates structured bug analysis reports from investigations.

    Converts an InvestigationResult into a Markdown report with
    sections for problem summary, root cause, investigation steps,
    proposed fix, and metadata (test results, token usage).

    Attributes:
        None — stateless utility class.
    """

    @staticmethod
    def generate(investigation: InvestigationResult) -> str:
        """Generate a structured Markdown bug report.

        Produces a report with the following sections:
        - Title with date
        - Problem Summary (root cause)
        - Investigation Steps (suspects)
        - Proposed Fix
        - Fix Status
        - Test Results
        - Token Usage

        Args:
            investigation: Investigation result to report on.

        Returns:
            Formatted Markdown bug report string.
        """
        lines: list[str] = []

        # Title
        lines.append("# Bug Analysis Report")
        lines.append("")
        lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Problem Summary
        lines.append("## Problem Summary")
        lines.append("")
        root_cause = investigation.root_cause or "Not yet determined"
        lines.append(f"**Root Cause**: {root_cause}")
        lines.append("")

        # Investigation Steps — suspects
        lines.append("## Investigation Steps")
        lines.append("")
        if investigation.suspects:
            lines.append("Suspect locations identified:")
            lines.append("")
            for i, suspect in enumerate(investigation.suspects, 1):
                lines.append(
                    f"{i}. **{suspect.file_path}** (lines {suspect.line_start}"
                    f"-{suspect.line_end}) — Score: {suspect.score:.2f}"
                )
                if suspect.reason:
                    lines.append(f"   — {suspect.reason}")
        else:
            lines.append("No suspects identified.")
        lines.append("")

        # Proposed Fix
        lines.append("## Proposed Fix")
        lines.append("")
        proposed_fix = investigation.proposed_fix or "None"
        lines.append(proposed_fix)
        lines.append("")

        # Fix Status
        lines.append("## Fix Status")
        lines.append("")
        if investigation.fix_applied:
            lines.append("✅ Fix has been applied.")
        else:
            lines.append("⚠️ Fix has not been applied yet.")
        lines.append("")

        # Test Results
        lines.append("## Test Results")
        lines.append("")
        if investigation.test_results:
            for key, value in investigation.test_results.items():
                lines.append(f"- **{key}**: {value}")
        else:
            lines.append("- No test results recorded.")
        lines.append("")

        # Token Usage
        lines.append("## Token Usage")
        lines.append("")
        metrics = investigation.token_usage
        lines.append(f"- Input tokens: {metrics.input_tokens}")
        lines.append(f"- Output tokens: {metrics.output_tokens}")
        lines.append(f"- Total tokens: {metrics.total_tokens}")
        lines.append("")

        logger.info("Generated bug report for investigation")
        return "\n".join(lines)
