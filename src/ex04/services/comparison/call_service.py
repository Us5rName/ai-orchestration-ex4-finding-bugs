"""Atomic provider call and telemetry path for comparison experiments.

Both comparison runners must delegate all provider calls to
ComparisonCallService. This ensures budget check, gatekeeper invocation,
ledger recording, and trace recording happen in one canonical sequence —
preventing a provider call from succeeding while telemetry is forgotten.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from ex04.providers.interface import Message
from ex04.services.comparison.budget import BudgetLedger
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types_results import ProviderResponse


@dataclass(frozen=True, slots=True)
class InstrumentedCallResult:
    """Immutable result of one instrumented provider call.

    All required telemetry is co-located with the provider response so
    callers cannot forget to record tokens or trace events.

    Attributes:
        response: Raw provider response with text and token counts.
        elapsed_seconds: Wall-clock time for the provider call.
        provider: Provider name used for this call.
        model: Model identifier reported by the request.
    """

    response: ProviderResponse
    elapsed_seconds: float
    provider: str
    model: str


class ComparisonCallService:
    """Canonical provider-call path shared by both comparison runners.

    Encapsulates the invariant sequence:
    1. Pre-call budget check (models + iterations).
    2. Gatekeeper invocation (rate limiting, retry, logging).
    3. Ledger recording.
    4. Trace recording.

    Args:
        gatekeeper: The API gatekeeper implementation to use.
    """

    def __init__(self, gatekeeper: GatekeeperInterface) -> None:
        """Store the gatekeeper dependency."""
        self._gatekeeper = gatekeeper

    def execute(
        self,
        messages: list[Message],
        provider: str,
        model: str,
        ledger: BudgetLedger,
        trace: TraceRecorder,
    ) -> InstrumentedCallResult:
        """Execute one provider call with full telemetry.

        Performs the pre-call budget check, delegates to the gatekeeper,
        records the result in the ledger and trace, and returns an
        InstrumentedCallResult.

        Args:
            messages: Canonical message list from PromptBuilder.
            provider: Provider name (e.g. "openai").
            model: Model identifier for trace metadata.
            ledger: Shared budget ledger to check and update.
            trace: Trace recorder to record the provider_call event.

        Returns:
            InstrumentedCallResult with response and telemetry.

        Raises:
            BudgetExceededError: If budget would be exceeded before call.
            RuntimeError: On gatekeeper/provider failure.
        """
        ledger.check(models=1, iterations=1)
        t0 = time.perf_counter()
        response = self._gatekeeper.send(provider, messages)
        elapsed = time.perf_counter() - t0
        ledger.record(models=1, iterations=1)
        trace.record("provider_call", ledger, provider=provider, model=model)
        return InstrumentedCallResult(
            response=response,
            elapsed_seconds=elapsed,
            provider=provider,
            model=model,
        )
