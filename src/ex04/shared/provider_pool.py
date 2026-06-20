"""Provider Pool — builds and caches provider instances from config.

Centralises per-provider configuration (model, base_url, max_tokens,
api_key_env) and caches instances so the gatekeeper does not rebuild a fresh
SDK client (and re-load a tokenizer) on every call. Each provider uses its own
settings instead of a single shared default.

Implementation: Phase 4 (T4.002, extracted from gatekeeper)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from ex04.providers.types import ProviderConfig

if TYPE_CHECKING:
    from ex04.providers.interface import ProviderInterface


class ProviderPool:
    """Lazily build and cache LLM provider instances keyed by provider name.

    Attributes:
        _configs: Per-provider configuration dicts.
        _instances: Cache of constructed provider instances.
    """

    def __init__(self, provider_configs: dict[str, dict[str, Any]] | None = None) -> None:
        """Store per-provider config; instances are created lazily on first use.

        Args:
            provider_configs: Mapping of provider name to its config dict
                (any of 'model', 'base_url', 'max_tokens', 'api_key_env').
        """
        self._configs = provider_configs or {}
        self._instances: dict[str, ProviderInterface] = {}

    def get(self, provider: str) -> ProviderInterface:
        """Return a cached provider instance, creating it on first request.

        Args:
            provider: Provider name (e.g. 'openai', 'anthropic').

        Returns:
            A configured ProviderInterface instance.
        """
        if provider not in self._instances:
            # Lazy import avoids a circular dependency at module load time.
            from ex04.providers.factory import ProviderFactory

            self._instances[provider] = ProviderFactory.create(provider, self._config_for(provider))
        return self._instances[provider]

    def model_for(self, provider: str) -> str | None:
        """Return the configured model for a provider, or None for its default.

        Args:
            provider: Provider name to look up.

        Returns:
            The configured model identifier, or None when unconfigured.
        """
        return self._configs.get(provider, {}).get("model")

    def _config_for(self, provider: str) -> ProviderConfig:
        """Build the provider config, defaulting api_key_env to <PROVIDER>_API_KEY.

        Args:
            provider: Provider name to build config for.

        Returns:
            A config dict suitable for ProviderFactory.create.
        """
        config = dict(self._configs.get(provider, {}))
        config.setdefault("api_key_env", f"{provider.upper()}_API_KEY")
        return cast(ProviderConfig, config)
