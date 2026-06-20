"""Tests for active Phase 4 agent nodes."""

from __future__ import annotations

from pathlib import Path

from ex04.services.agent.nodes.analysis import BugAnalysisNode
from ex04.services.agent.nodes.fix import FixGenerationNode
from ex04.services.agent.nodes.knowledge import KnowledgeLoadNode
from ex04.services.agent.nodes.rootcause import RootCauseNode
from ex04.services.agent.nodes.suspect import SuspectRankingNode
from ex04.services.agent.nodes.verify import VerificationNode
from ex04.shared.types_results import ProviderResponse, Suspect


class FakeGatekeeper:
    """Minimal Gatekeeper fake returning a deterministic response."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.calls: list[tuple[str, list[dict[str, str]]]] = []

    def send(self, provider: str, messages: list[dict[str, str]]) -> ProviderResponse:
        """Capture request and return a canned response."""
        self.calls.append((provider, messages))
        return ProviderResponse(
            text=self.text,
            input_tokens=7,
            output_tokens=5,
            model="fake-model",
            provider=provider,
        )

    def get_call_log(self) -> list[dict]:
        """Return no call log entries; unused by node tests."""
        return []

    def get_queue_status(self) -> dict:
        """Return an idle queue; unused by node tests."""
        return {"queue_size": 0}


def test_knowledge_load_reads_graph_file_and_vault(tmp_path: Path) -> None:
    """Knowledge node loads bounded graph and vault context."""
    graph = tmp_path / "graph.json"
    graph.write_text('{"nodes": ["PaymentService"]}', encoding="utf-8")
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "index.md").write_text("# Index\nPaymentService", encoding="utf-8")

    result = KnowledgeLoadNode(context_limit=200)({"graph_context": str(graph), "vault_context": str(vault)})

    assert "PaymentService" in result["graph_context"]
    assert "index.md" in result["vault_context"]


def test_bug_analysis_calls_gatekeeper_and_populates_suspects() -> None:
    """Bug analysis uses Gatekeeper and parses suspect locations."""
    gatekeeper = FakeGatekeeper("Likely issue in app.py:10-12 because payment fails")
    result = BugAnalysisNode(gatekeeper, "fake")({"bug_report": "payment fails"})

    assert gatekeeper.calls
    assert result["suspects"] == [
        Suspect("app.py", 10, 12, 1.0, "Likely issue in app.py:10-12 because payment fails")
    ]
    assert result["token_usage"].total_tokens == 12


def test_suspect_ranking_orders_and_limits() -> None:
    """Suspect ranking sorts by score and trims to max_suspects."""
    suspects = [
        Suspect("low.py", 1, 1, 0.1, "other"),
        Suspect("high.py", 1, 1, 0.9, "payment failure"),
    ]
    result = SuspectRankingNode(max_suspects=1)({"bug_report": "payment failure", "suspects": suspects})

    assert result["suspects"] == [suspects[1]]


def test_rootcause_calls_gatekeeper_and_sets_text() -> None:
    """Root cause node writes model response to state."""
    gatekeeper = FakeGatekeeper("The cache key ignores user id.")
    result = RootCauseNode(gatekeeper, "fake")({"bug_report": "bad cache", "inspected_code": "code"})

    assert gatekeeper.calls
    assert result["root_cause"] == "The cache key ignores user id."


def test_fix_generation_applies_file_find_replace(tmp_path: Path) -> None:
    """Fix node applies a simple FILE/FIND/REPLACE response."""
    source = tmp_path / "app.py"
    source.write_text("value = old_name\n", encoding="utf-8")
    response = "FILE:\napp.py\nFIND:\nold_name\nREPLACE:\nnew_name"

    result = FixGenerationNode(tmp_path, FakeGatekeeper(response), "fake")({})

    assert result["fix_applied"] is True
    assert "-value = old_name" in result["fix_diff"]
    assert "+value = new_name" in result["fix_diff"]
    assert "new_name" in source.read_text(encoding="utf-8")


def test_verification_runs_command_and_populates_results() -> None:
    """Verification node records subprocess status and increments iterations."""
    result = VerificationNode(command=["true"])({"iterations": 1})

    assert result["iterations"] == 2
    assert result["test_results"]["passed"] is True
    assert result["test_results"]["failed"] == 0
