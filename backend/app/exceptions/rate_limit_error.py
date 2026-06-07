"""Rate limit exceeded."""

from .provider_error import ProviderError


class RateLimitError(ProviderError):
    """Rate limit exceeded."""
    pass
