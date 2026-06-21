"""Tests for shared LLM node helpers."""

from __future__ import annotations

from ex04.services.agent.deps import NodeDeps
from ex04.services.agent.nodes.common import call_llm, context_for_prompt, state_with_tokens
from ex04.shared.types_metrics import TokenMetrics
from ex04.shared.types_results import ProviderResponse


class FakeGatekeeper:
    """Gatekeeper fake for shared LLM helper tests."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, list[dict[str, str]]]] = []

    def send(self, provider: str, messages: list[dict[str, str]]) -> ProviderResponse:
        self.calls.append((provider, messages))
        return ProviderResponse(
            text="ok",
            input_tokens=3,
            output_tokens=4,
            provider=provider,
            model="fake-model",
        )


def test_call_llm_uses_gatekeeper_provider_and_prompt() -> None:
    gatekeeper = FakeGatekeeper()
    deps = NodeDeps(gatekeeper=gatekeeper, provider="fake")

    response = call_llm(deps, {}, "analysis", "prompt text")

    assert response.text == "ok"
    assert gatekeeper.calls == [("fake", [{"role": "user", "content": "prompt text"}])]


def test_state_with_tokens_matches_existing_token_accounting() -> None:
    state = {"token_usage": TokenMetrics(input_tokens=10, output_tokens=2, total_tokens=12)}
    response = ProviderResponse(input_tokens=3, output_tokens=4, provider="fake", model="m")

    updated = state_with_tokens(state, response)

    assert updated["token_usage"] == TokenMetrics(
        input_tokens=13,
        output_tokens=6,
        total_tokens=19,
        provider="fake",
        model="m",
    )


def test_context_for_prompt_limits_mode_difference_to_context() -> None:
    graph_state = {"mode": "graph", "graph_context": "graph", "vault_context": "vault"}
    naive_state = {"mode": "naive", "source_context": "source"}

    assert context_for_prompt(graph_state) == "graph\n\nvault"
    assert context_for_prompt(naive_state) == "source"
