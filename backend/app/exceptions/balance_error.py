"""Insufficient balance or credits."""

from .provider_error import ProviderError


class BalanceError(ProviderError):
    """Insufficient balance or credits."""

    pass
