"""Provider service is unavailable."""

from .provider_error import ProviderError


class ProviderUnavailableError(ProviderError):
    """Provider service is unavailable."""
    pass
