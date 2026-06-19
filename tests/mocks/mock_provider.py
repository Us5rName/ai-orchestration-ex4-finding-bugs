"""Mock Provider — canned LLM responses for testing.

Implements ProviderInterface with deterministic canned responses
so tests can run without real API calls.
"""

from __future__ import annotations

from ex04.providers.interface import ProviderInterface
from ex04.shared.types import ProviderResponse


class MockProvider(ProviderInterface):
    """Mock implementation of ProviderInterface with canned responses.

    Returns consistent canned responses regardless of input, enabling
    deterministic tests without hitting real LLM APIs.
    """

    def chat(
        self, messages: list[dict], model: str = "mock-model", base_url: str | None = None
    ) -> ProviderResponse:
        """Return a canned chat response.

        Args:
            messages: Message list (ignored in mock).
            model: Model name (used in response).
            base_url: Base URL (ignored in mock).

        Returns:
            ProviderResponse with canned text and token counts.
        """
        return ProviderResponse(
            text="This is a canned mock response for testing.",
            input_tokens=100,
            output_tokens=50,
            model=model,
            provider="mock",
        )

    def count_tokens(self, text: str) -> int:
        """Return a mock token count.

        Args:
            text: Input text (ignored in mock).

        Returns:
            Fixed token count of 42.
        """
        return 42
