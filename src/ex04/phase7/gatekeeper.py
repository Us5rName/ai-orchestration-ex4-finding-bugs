"""Deterministic gatekeeper for keyless Phase 7 evidence runs."""

from __future__ import annotations

from typing import Any

from ex04.providers.interface import Message
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types_results import ProviderResponse


class Phase7Gatekeeper(GatekeeperInterface):
    """Return structured responses that drive the real agent workflow keylessly."""

    def __init__(self) -> None:
        self._calls: list[dict[str, Any]] = []

    def send(self, provider: str, messages: list[Message]) -> ProviderResponse:
        """Return the response matching the requested agent node prompt."""
        prompt = messages[-1]["content"]
        text = _response_for(prompt)
        input_tokens, output_tokens = _token_counts(prompt, text)
        response = ProviderResponse(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider=provider,
            model="phase7-deterministic",
        )
        self._calls.append({
            "provider": provider,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        })
        return response

    def get_call_log(self) -> list[dict[str, Any]]:
        """Return Phase 7 model-call telemetry."""
        return list(self._calls)

    def get_queue_status(self) -> dict[str, Any]:
        """Return an idle queue status for the deterministic runner."""
        return {"queue_size": 0, "is_processing": False, "rate_limited": False}


def _response_for(prompt: str) -> str:
    if "Respond with JSON only" in prompt:
        return _comparison_payload()
    if prompt.startswith("Identify suspect Python locations"):
        return (
            "The mutable default list is in snippets/foobar.py:8-10; "
            "foo() appends to the same list across calls."
        )
    if prompt.startswith("You are a code reviewer"):
        return (
            "The function foo uses bar=[] as a default argument. That list is "
            "created once and reused, so repeated calls retain previous values."
        )
    if prompt.startswith("Explain the root cause"):
        return (
            "foo() stores state in a mutable default argument. The default list "
            "is shared between calls, so the second call returns two values."
        )
    if prompt.startswith("Propose a fix"):
        return "\n".join([
            "FILE:",
            "snippets/foobar.py",
            "FIND:",
            "def foo(bar=[]):",
            '    bar.append("baz")',
            "    return bar",
            "REPLACE:",
            "def foo(bar=None):",
            "    if bar is None:",
            "        bar = []",
            '    bar.append("baz")',
            "    return bar",
        ])
    return ""


def _comparison_payload() -> str:
    return (
        '{"root_cause":"foo() uses a mutable default list that persists across calls.",'
        '"suspected_files":["snippets/foobar.py"],'
        '"suspected_symbols":["foo"],'
        '"confidence":"high",'
        '"evidence":[{"file":"snippets/foobar.py","line_start":8,"line_end":10,'
        '"symbol":"foo","reason":"bar=[] is allocated once and reused."}],'
        '"patch":"Change foo(bar=[]) to foo(bar=None) and allocate a new list inside."}'
    )


def _token_counts(prompt: str, text: str) -> tuple[int, int]:
    if "Respond with JSON only" not in prompt:
        return max(1, len(prompt.split())), max(1, len(text.split()))
    if "Graph entities" in prompt:
        return 180, 42
    return 620, 42
