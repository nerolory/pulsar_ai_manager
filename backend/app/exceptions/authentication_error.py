"""Invalid API key or authentication failed."""

from .provider_error import ProviderError


class AuthenticationError(ProviderError):
    """Invalid API key or authentication failed."""
    pass
