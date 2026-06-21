"""Tests for PromptBuilder canonical prompt envelope."""

from __future__ import annotations

from ex04.services.comparison.context_bundle import (
    ContextBundle,
    ContextProvenance,
    ContextStrategy,
    SourceRef,
)
from ex04.services.comparison.prompt_builder import (
    PROMPT_ENVELOPE_VERSION,
    ComparisonPromptInput,
    PromptBuilder,
)


def _bundle(content: str, strategy: ContextStrategy = ContextStrategy.NAIVE) -> ContextBundle:
    prov = ContextProvenance(strategy=strategy, token_count=5, source_count=1)
    return ContextBundle(
        content=content,
        strategy=strategy,
        source_refs=(SourceRef(path="a.py", kind="file"),),
        provenance=prov,
    )


def _input(content: str, strategy: ContextStrategy = ContextStrategy.NAIVE) -> ComparisonPromptInput:
    return ComparisonPromptInput(
        system_prompt="You are an expert.",
        bug_report="null pointer in module X",
        context_bundle=_bundle(content, strategy),
    )


def test_builder_returns_single_user_message() -> None:
    pb = PromptBuilder()
    msgs = pb.build_messages(_input("some context"))
    assert len(msgs) == 1
    assert msgs[0]["role"] == "user"


def test_prompt_contains_system_prompt() -> None:
    pb = PromptBuilder()
    msgs = pb.build_messages(_input("ctx"))
    assert "You are an expert." in msgs[0]["content"]


def test_prompt_contains_bug_report() -> None:
    pb = PromptBuilder()
    msgs = pb.build_messages(_input("ctx"))
    assert "null pointer in module X" in msgs[0]["content"]


def test_prompt_contains_context_content() -> None:
    pb = PromptBuilder()
    msgs = pb.build_messages(_input("my special context text"))
    assert "my special context text" in msgs[0]["content"]


def test_equivalent_context_produces_identical_messages() -> None:
    """Same context content → identical messages regardless of call order."""
    pb = PromptBuilder()
    inp = _input("same context")
    assert pb.build_messages(inp) == pb.build_messages(inp)


def test_different_context_changes_only_context_section() -> None:
    """Different context content → only context part of message differs."""
    pb = PromptBuilder()
    msgs_a = pb.build_messages(_input("context A"))
    msgs_b = pb.build_messages(_input("context B"))
    content_a = msgs_a[0]["content"]
    content_b = msgs_b[0]["content"]
    # System prompt section is identical
    assert content_a.split("context A")[0] == content_b.split("context B")[0]
    # Suffix (schema) is identical
    assert content_a.split("context A")[1] == content_b.split("context B")[1]


def test_naive_and_graph_same_system_prompt_section() -> None:
    """Both strategies produce identical system-prompt sections."""
    pb = PromptBuilder()
    naive_inp = _input("ctx", ContextStrategy.NAIVE)
    graph_inp = ComparisonPromptInput(
        system_prompt="You are an expert.",
        bug_report="null pointer in module X",
        context_bundle=_bundle("ctx", ContextStrategy.GRAPH_GUIDED),
    )
    msgs_naive = pb.build_messages(naive_inp)
    msgs_graph = pb.build_messages(graph_inp)
    # With identical context content both messages are equal
    assert msgs_naive == msgs_graph


def test_version_constant_is_set() -> None:
    assert PROMPT_ENVELOPE_VERSION == "1.0"
    assert PromptBuilder.VERSION == PROMPT_ENVELOPE_VERSION


def test_custom_output_schema_is_embedded() -> None:
    pb = PromptBuilder()
    inp = ComparisonPromptInput(
        system_prompt="sys",
        bug_report="bug",
        context_bundle=_bundle("ctx"),
        output_schema="MY_SCHEMA",
    )
    msgs = pb.build_messages(inp)
    assert "MY_SCHEMA" in msgs[0]["content"]
