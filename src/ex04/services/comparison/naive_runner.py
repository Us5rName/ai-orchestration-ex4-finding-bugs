"""Naive Runner — bounded bug-report-driven investigation workflow.

Bounded navigation: tree listing, keyword filtering, selective file reading
up to hard budget limits. Budget counters cumulative, never reset.
Success requires structured JSON output + confirmed source anchor.
Phrase/keyword matching is NOT used to determine success.
No graph context, graph nodes, or vault data may enter this runner.

Traceability: [PRD-CE §Naive], [TODO P6-R03-REV], [Correction #3]
"""

from __future__ import annotations

import re
import time
from pathlib import Path

from ex04.services.comparison._output_parser import JSON_SCHEMA, parse_json_response
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types_results import InvestigationResult

# Public alias so tests can import without reaching into private module
_parse_json_response = parse_json_response


def _extract_keywords(bug_report: str) -> set[str]:
    """Extract relevant search terms from a bug report."""
    words = re.findall(r"\b[a-zA-Z_]\w{2,}\b", bug_report.lower())
    stop = {"the", "and", "for", "with", "that", "this", "from", "when"}
    return {w for w in words if w not in stop}


class NaiveRunner:
    """Run a bounded, unfocused baseline over source files.

    Explores the repository using only ordinary navigation (tree listing,
    keyword-filtered file reading). Graph context is structurally excluded.
    All budget limits are enforced cumulatively. Success is determined by
    structured JSON output validation, not keyword or phrase matching.
    """

    def __init__(
        self,
        gatekeeper: GatekeeperInterface,
        provider: str = "openai",
        max_files: int = 20,
        max_bytes: int = 524288,
        timeout_seconds: float = 120.0,
    ) -> None:
        """Initialize with Gatekeeper and budget parameters."""
        self.gatekeeper = gatekeeper
        self.provider = provider
        self.max_files = max_files
        self.max_bytes = max_bytes
        self.timeout_seconds = timeout_seconds

    def run(self, bug_report: str, source_files: list[Path]) -> InvestigationResult:
        """Navigate source files within budget limits and query the model.

        Args:
            bug_report: Natural-language bug description.
            source_files: Candidate files for inspection.

        Returns:
            InvestigationResult with structured output and budget telemetry.
        """
        started = time.perf_counter()
        keywords = _extract_keywords(bug_report)
        all_py = [p for p in source_files if p.is_file()]
        tool_calls = 1  # counts tree_list

        def _score(p: Path) -> int:
            nm = p.name.lower()
            return sum(1 for kw in keywords if kw in nm)

        ranked = sorted(all_py, key=_score, reverse=True)
        context_parts: list[str] = []
        files_read = 0
        bytes_read = 0

        for path in ranked:
            if files_read >= self.max_files or bytes_read >= self.max_bytes:
                break
            if time.perf_counter() - started >= self.timeout_seconds:
                break
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
                chunk = text[: self.max_bytes - bytes_read]
                context_parts.append(f"--- {path.name} ---\n{chunk}")
                files_read += 1
                bytes_read += len(chunk.encode())
                tool_calls += 1
            except OSError:
                continue

        context = "\n\n".join(context_parts) if context_parts else "(no files read)"
        response = self.gatekeeper.send(
            self.provider,
            [{"role": "user", "content": f"Bug:\n{bug_report}\n\n{context}\n\n{JSON_SCHEMA}"}],
        )

        parser_status, parsed = parse_json_response(response.text)
        known = {p.name for p in source_files} | {str(p) for p in source_files}
        valid_anchors: list[str] = []
        limitations: list[str] = []
        if parsed and isinstance(parsed.get("suspected_files"), list):
            for sf in parsed["suspected_files"]:
                if sf in known or any(sf in str(p) for p in source_files):
                    valid_anchors.append(str(sf))
                else:
                    limitations.append(f"Suspected file '{sf}' not in source corpus.")

        return InvestigationResult(
            root_cause=str(parsed.get("root_cause", "")) if parsed else "",
            proposed_fix=str(parsed.get("patch", "")) if parsed else "",
            original_problem=bug_report,
            files_read=files_read,
            bytes_read=bytes_read,
            tool_calls=tool_calls,
            model_calls=1,
            iterations=1,
            duration_seconds=time.perf_counter() - started,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            parser_status=parser_status,
            gate_status="pass_without_gate",
            limitations=limitations,
            evidence_class="fixture",
            telemetry_available=False,
        )
