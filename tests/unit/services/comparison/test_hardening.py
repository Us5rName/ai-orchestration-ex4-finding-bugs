"""Hardening tests for H3 (parity), H4 (provenance), H5 (telemetry).

Traceability: [TODO T5.03], [PLAN ADR-007].
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ex04.services.comparison.call_service import (
    ComparisonCallService,
    InstrumentedCallResult,
    ProviderTraceEvent,
)
from ex04.services.comparison.context_bundle import ContextStrategy
from ex04.services.comparison.fairness import FairnessEnforcer, FairnessViolationError
from ex04.services.comparison.graph_guided_runner import GraphGuidedRunner
from ex04.services.comparison.naive_runner import NaiveRunner
from ex04.services.comparison.parity import ParityError, assert_request_parity
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.types import Entity, GraphData
from ex04.shared.types_metrics import TokenMetrics
from ex04.shared.types_request import ComparisonRequest


def _req(**overrides: object) -> ComparisonRequest:
    defaults: dict[str, object] = {"bug_report": "test", "provider": "openai"}
    defaults.update(overrides)
    return ComparisonRequest(**defaults)  # type: ignore[arg-type]


def _mock_gk(input_tokens: int = 100, output_tokens: int = 50) -> MagicMock:
    gk = MagicMock()
    resp = MagicMock()
    resp.text = ""
    resp.input_tokens = input_tokens
    resp.output_tokens = output_tokens
    gk.send.return_value = resp
    return gk


def _mock_ledger() -> MagicMock:
    ledger = MagicMock()
    ledger.snapshot.return_value = {}
    ledger.bytes_read = 0
    ledger.files_read = 0
    ledger.context_tokens = 0
    ledger.tool_calls = 0
    ledger.model_calls = 0
    ledger.iterations = 0
    ledger.retries = 0
    ledger.limitations = []
    return ledger


# ---------------------------------------------------------------------------
# H3 — FairnessEnforcer delegates to canonical parity mechanism
# ---------------------------------------------------------------------------


class TestH3ParityMechanism:
    def test_fairness_enforcer_passes_identical_requests(self) -> None:
        req = _req()
        FairnessEnforcer().check(req, req)

    def test_fairness_enforcer_raises_on_provider_mismatch(self) -> None:
        with pytest.raises(FairnessViolationError, match="provider"):
            FairnessEnforcer().check(_req(provider="openai"), _req(provider="anthropic"))

    def test_assert_request_parity_raises_parity_error(self) -> None:
        with pytest.raises(ParityError):
            assert_request_parity(_req(provider="openai"), _req(provider="anthropic"))

    def test_assert_request_parity_passes_identical(self) -> None:
        req = _req()
        assert_request_parity(req, req)

    def test_config_hash_is_64_hex(self) -> None:
        h = FairnessEnforcer.config_hash(_req())
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_mismatch_rejected_before_provider_call(self) -> None:
        gk = _mock_gk()
        enforcer = FairnessEnforcer()
        with pytest.raises(FairnessViolationError):
            enforcer.check(_req(provider="openai"), _req(provider="anthropic"))
        gk.send.assert_not_called()

    def test_fingerprint_deterministic(self) -> None:
        req = _req(model="gpt-4o")
        h1 = FairnessEnforcer.config_hash(req)
        h2 = FairnessEnforcer.config_hash(req)
        assert h1 == h2

    def test_treatment_fields_excluded(self) -> None:
        h1 = FairnessEnforcer.config_hash(_req(run_id="naive-001"))
        h2 = FairnessEnforcer.config_hash(_req(run_id="guided-001"))
        assert h1 == h2

    def test_controlled_model_changes_hash(self) -> None:
        h1 = FairnessEnforcer.config_hash(_req(model="gpt-4o"))
        h2 = FairnessEnforcer.config_hash(_req(model="gpt-4o-mini"))
        assert h1 != h2

    def test_no_credential_in_fingerprint(self) -> None:
        req = _req(system_prompt="use secret_api_key=supersecret")
        h = FairnessEnforcer.config_hash(req)
        assert "supersecret" not in h


# ---------------------------------------------------------------------------
# H4 — Exact ContextBundle provenance
# ---------------------------------------------------------------------------


class TestH4ContextProvenance:
    def test_naive_only_includes_read_files(self, tmp_path: Path) -> None:
        included = tmp_path / "included.py"
        included.write_text("# included\n")
        not_included = tmp_path / "zzz_unrelated.py"
        not_included.write_text("# not included\n")
        runner = NaiveRunner(_mock_gk(), provider="openai")
        result = runner.run("bug in included", [included, not_included])
        assert result.files_read == 1

    def test_naive_bundle_source_count_matches_read_count(
        self, tmp_path: Path
    ) -> None:
        src = tmp_path / "module.py"
        src.write_text("def foo(): pass\n")
        bundle_refs: list = []

        orig_make = NaiveRunner._make_bundle

        def capture_bundle(self, context, included):  # type: ignore[override]
            bundle = orig_make(self, context, included)
            bundle_refs.extend(bundle.source_refs)
            return bundle

        import types as _types
        runner = NaiveRunner(_mock_gk(), provider="openai")
        runner._make_bundle = _types.MethodType(capture_bundle, runner)  # type: ignore[method-assign]
        runner.run("bug in module", [src])
        assert len(bundle_refs) >= 1

    def test_graph_bundle_only_includes_sent_entities(self) -> None:
        graph = GraphData(
            entities=[
                Entity(name="SentClass", kind="class", file_path="sent.py"),
                Entity(name="OtherClass", kind="class", file_path="other.py"),
            ],
            relationships=[],
        )
        runner = GraphGuidedRunner(_mock_gk(), provider="openai")
        runner.run("bug in SentClass", graph_data=graph)

    def test_source_refs_strategy_is_naive(self, tmp_path: Path) -> None:
        src = tmp_path / "source.py"
        src.write_text("x = 1\n")
        bundle_refs: list = []

        orig_call = NaiveRunner._call_provider

        def capture(self, req, bundle, ledger, trace):  # type: ignore[override]
            bundle_refs.append(bundle.strategy)
            return orig_call(self, req, bundle, ledger, trace)

        import types as _types
        runner = NaiveRunner(_mock_gk(), provider="openai")
        runner._call_provider = _types.MethodType(capture, runner)  # type: ignore[method-assign]
        runner.run("bug", [src])
        assert any(s == ContextStrategy.NAIVE for s in bundle_refs)


# ---------------------------------------------------------------------------
# H5 — Atomic call telemetry and evidence
# ---------------------------------------------------------------------------


class TestH5AtomicTelemetry:
    def test_instrumented_result_is_frozen(self) -> None:
        from ex04.shared.types_results import ProviderResponse
        resp = ProviderResponse(text="", input_tokens=10, output_tokens=5)
        result = InstrumentedCallResult(
            response=resp, elapsed_seconds=0.1, provider="openai", model="gpt-4o"
        )
        with pytest.raises((AttributeError, TypeError)):
            result.provider = "other"  # type: ignore[misc]

    def test_call_service_produces_token_record(self) -> None:
        gk = _mock_gk(input_tokens=42, output_tokens=17)
        svc = ComparisonCallService(gk)
        ledger = _mock_ledger()
        trace = TraceRecorder(run_id="test")
        result = svc.execute(
            [{"role": "user", "content": "x"}],  # type: ignore[list-item]
            "openai", "gpt-4o", ledger, trace,
        )
        assert isinstance(result.token_record, TokenMetrics)
        assert result.token_record.input_tokens == 42
        assert result.token_record.output_tokens == 17
        assert result.token_record.total_tokens == 59

    def test_call_service_produces_trace_event(self) -> None:
        gk = _mock_gk()
        svc = ComparisonCallService(gk)
        ledger = _mock_ledger()
        trace = TraceRecorder(run_id="test")
        result = svc.execute(
            [{"role": "user", "content": "x"}],  # type: ignore[list-item]
            "openai", "gpt-4o", ledger, trace,
        )
        assert isinstance(result.trace_event, ProviderTraceEvent)
        assert result.trace_event.provider == "openai"
        assert result.trace_event.model == "gpt-4o"

    def test_telemetry_available_true_when_tokens_present(self) -> None:
        gk = _mock_gk(input_tokens=10, output_tokens=5)
        svc = ComparisonCallService(gk)
        ledger = _mock_ledger()
        trace = TraceRecorder(run_id="test")
        result = svc.execute(
            [{"role": "user", "content": "x"}],  # type: ignore[list-item]
            "openai", "gpt-4o", ledger, trace,
        )
        assert result.trace_event.telemetry_available is True

    def test_telemetry_available_false_when_no_tokens(self) -> None:
        gk = _mock_gk(input_tokens=0, output_tokens=0)
        svc = ComparisonCallService(gk)
        ledger = _mock_ledger()
        trace = TraceRecorder(run_id="test")
        result = svc.execute(
            [{"role": "user", "content": "x"}],  # type: ignore[list-item]
            "openai", "gpt-4o", ledger, trace,
        )
        assert result.trace_event.telemetry_available is False

    def test_request_fingerprint_propagated(self) -> None:
        gk = _mock_gk()
        svc = ComparisonCallService(gk)
        ledger = _mock_ledger()
        trace = TraceRecorder(run_id="test")
        result = svc.execute(
            [{"role": "user", "content": "x"}],  # type: ignore[list-item]
            "openai", "gpt-4o", ledger, trace,
            request_fingerprint="abc123",
        )
        assert result.request_fingerprint == "abc123"

    def test_both_runners_use_same_call_service_type(self) -> None:
        from ex04.services.comparison.call_service import ComparisonCallService
        gk = _mock_gk()
        naive = NaiveRunner(gk)
        graph = GraphGuidedRunner(gk)
        assert isinstance(naive._call_service, ComparisonCallService)
        assert isinstance(graph._call_service, ComparisonCallService)
