"""Atomic provider call and telemetry path for comparison experiments.

Both runners delegate all provider calls here. InstrumentedCallResult carries
token_record, trace_event, and request_fingerprint (H5 hardening).
Missing telemetry is explicit — not represented as zero.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from ex04.providers.interface import Message
from ex04.services.comparison.budget import BudgetLedger
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types_metrics import TokenMetrics
from ex04.shared.types_results import ProviderResponse


@dataclass(frozen=True, slots=True)
class ProviderTraceEvent:
    """Immutable snapshot of one provider_call trace event.

    telemetry_available is False when the provider returned zero tokens
    for both input and output — this is distinct from a genuine zero count.
    """

    operation: str
    provider: str
    model: str
    elapsed_seconds: float
    telemetry_available: bool


@dataclass(frozen=True, slots=True)
class InstrumentedCallResult:
    """Immutable result of one instrumented provider call.

    Carries response, typed token record, trace event, and config fingerprint.
    telemetry_available=False means tokens were not measured — distinct from
    a genuine zero count.
    """

    response: ProviderResponse
    elapsed_seconds: float
    provider: str
    model: str
    token_record: TokenMetrics = field(default_factory=TokenMetrics)
    trace_event: ProviderTraceEvent = field(
        default_factory=lambda: ProviderTraceEvent(
            operation="provider_call",
            provider="",
            model="",
            elapsed_seconds=0.0,
            telemetry_available=False,
        )
    )
    request_fingerprint: str = ""


class ComparisonCallService:
    """Canonical provider-call path shared by both comparison runners."""

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
        *,
        request_fingerprint: str = "",
    ) -> InstrumentedCallResult:
        """Execute one provider call: budget → gatekeeper → ledger → trace → result."""
        ledger.check(models=1, iterations=1)
        t0 = time.perf_counter()
        response = self._gatekeeper.send(provider, messages)
        elapsed = time.perf_counter() - t0
        ledger.record(models=1, iterations=1)
        trace.record("provider_call", ledger, provider=provider, model=model)
        telemetry_available = response.input_tokens > 0 or response.output_tokens > 0
        token_record = TokenMetrics(
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            total_tokens=response.input_tokens + response.output_tokens,
            provider=provider,
            model=model,
        )
        trace_event = ProviderTraceEvent(
            operation="provider_call",
            provider=provider,
            model=model,
            elapsed_seconds=elapsed,
            telemetry_available=telemetry_available,
        )
        return InstrumentedCallResult(
            response=response,
            elapsed_seconds=elapsed,
            provider=provider,
            model=model,
            token_record=token_record,
            trace_event=trace_event,
            request_fingerprint=request_fingerprint,
        )
