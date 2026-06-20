"""Shared cumulative budget ledger for comparison runners."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from ex04.shared.types_request import ComparisonRequest


class BudgetExceededError(RuntimeError):
    """Raised before an operation that would exceed a configured budget."""


def estimate_context_tokens(text: str) -> int:
    """Deterministic shared token estimator: one token per four UTF-8 bytes."""
    return max(1, (len(text.encode("utf-8")) + 3) // 4) if text else 0


@dataclass
class BudgetLedger:
    """Cumulative operation counters shared by both comparison modes."""

    max_files: int
    max_bytes: int
    max_context_tokens: int
    max_tool_calls: int
    max_model_calls: int
    max_iterations: int
    max_retries: int
    timeout_seconds: float
    started: float = field(default_factory=time.perf_counter)
    files_read: int = 0
    bytes_read: int = 0
    context_tokens: int = 0
    tool_calls: int = 0
    model_calls: int = 0
    iterations: int = 0
    retries: int = 0
    limitations: list[str] = field(default_factory=list)

    @classmethod
    def from_request(cls, request: ComparisonRequest) -> BudgetLedger:
        """Create a ledger from the canonical request limits."""
        return cls(
            request.max_files, request.max_bytes, request.token_budget,
            request.max_tool_calls, request.max_model_calls, request.max_iterations,
            request.max_retries, float(request.timeout_seconds),
        )

    @property
    def elapsed_seconds(self) -> float:
        """Wall-clock time since ledger creation."""
        return time.perf_counter() - self.started

    def check(self, *, files: int = 0, bytes_: int = 0, tokens: int = 0,
              tools: int = 0, models: int = 0, iterations: int = 0,
              retries: int = 0) -> None:
        """Reject an operation before it exceeds any configured limit."""
        checks = (
            ("files_read", self.files_read + files, self.max_files),
            ("bytes_read", self.bytes_read + bytes_, self.max_bytes),
            ("context_tokens", self.context_tokens + tokens, self.max_context_tokens),
            ("tool_calls", self.tool_calls + tools, self.max_tool_calls),
            ("model_calls", self.model_calls + models, self.max_model_calls),
            ("iterations", self.iterations + iterations, self.max_iterations),
            ("retries", self.retries + retries, self.max_retries),
        )
        for name, value, limit in checks:
            if value > limit:
                self.limitations.append(f"Budget exhausted: {name} {value}>{limit}")
                raise BudgetExceededError(self.limitations[-1])
        if self.elapsed_seconds > self.timeout_seconds:
            self.limitations.append("Budget exhausted: timeout")
            raise BudgetExceededError(self.limitations[-1])

    def record(self, *, files: int = 0, bytes_: int = 0, tokens: int = 0,
               tools: int = 0, models: int = 0, iterations: int = 0,
               retries: int = 0) -> None:
        """Add actual usage after a successful operation."""
        self.files_read += files
        self.bytes_read += bytes_
        self.context_tokens += tokens
        self.tool_calls += tools
        self.model_calls += models
        self.iterations += iterations
        self.retries += retries

    def snapshot(self) -> dict[str, int | float]:
        """Return current counters for result and trace population."""
        return {
            "files_read": self.files_read,
            "bytes_read": self.bytes_read,
            "context_tokens": self.context_tokens,
            "tool_calls": self.tool_calls,
            "model_calls": self.model_calls,
            "iterations": self.iterations,
            "retries": self.retries,
            "elapsed_seconds": self.elapsed_seconds,
        }
