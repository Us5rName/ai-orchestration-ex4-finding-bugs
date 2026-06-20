"""Naive Runner — bounded bug-report-driven investigation workflow.

Replaces full-corpus concatenation with bounded navigation: tree listing,
keyword filtering, and selective file reading up to hard budget limits.
Budget counters are cumulative and never reset across iterations.

No graph context, graph nodes, or vault data may enter this runner.

Traceability: [PRD-CE §Naive], [TODO P6-R03]
"""

from __future__ import annotations

import re
import time
from pathlib import Path

from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types import RunMetrics

_SUCCESS_PATTERNS = re.compile(
    r"root cause|fix:|problem:|indexerror|line \d+|traceback", re.IGNORECASE
)


def _extract_keywords(bug_report: str) -> set[str]:
    """Extract relevant search terms from a bug report."""
    words = re.findall(r"\b[a-zA-Z_]\w{2,}\b", bug_report.lower())
    stop = {"the", "and", "for", "with", "that", "this", "from", "when"}
    return {w for w in words if w not in stop}


def _response_indicates_finding(text: str) -> bool:
    """Return True only when text contains structured diagnostic indicators."""
    return bool(_SUCCESS_PATTERNS.search(text))


class NaiveRunner:
    """Run a bounded, unfocused baseline over source files.

    Explores the repository using only ordinary navigation (tree listing,
    keyword-filtered file reading). Graph context is structurally excluded.
    All budget limits are enforced cumulatively within each run() call.
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

    def run(self, bug_report: str, source_files: list[Path]) -> RunMetrics:
        """Navigate source files within budget limits and query the model.

        Args:
            bug_report: Natural-language bug description.
            source_files: Candidate files for inspection.

        Returns:
            RunMetrics with cumulative usage and conservative success flag.
        """
        started = time.perf_counter()
        keywords = _extract_keywords(bug_report)
        trace: list[dict[str, object]] = []

        # Phase 1: tree inspection (1 tool call)
        all_py = [p for p in source_files if p.is_file()]
        tool_calls = 1
        trace.append({"op": "tree_list", "total_files": len(all_py)})

        # Phase 2: keyword filter — prefer files matching bug-report terms
        def _score(p: Path) -> int:
            name = p.name.lower()
            return sum(1 for kw in keywords if kw in name)

        ranked = sorted(all_py, key=_score, reverse=True)

        # Phase 3: bounded selective reading
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
                trace.append(
                    {"op": "read_file", "path": str(path), "bytes": len(chunk.encode())}
                )
            except OSError:
                continue

        context = "\n\n".join(context_parts) if context_parts else "(no files read)"
        response = self.gatekeeper.send(
            self.provider,
            [{"role": "user", "content": f"Bug:\n{bug_report}\n\n{context}"}],
        )

        return RunMetrics(
            tokens_used=response.input_tokens + response.output_tokens,
            files_read=files_read,
            iterations=1,
            time_seconds=time.perf_counter() - started,
            found_root_cause=_response_indicates_finding(response.text),
        )
