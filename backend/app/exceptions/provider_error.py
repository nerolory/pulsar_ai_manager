"""Base exception for provider errors."""

from typing import Optional


class ProviderError(Exception):
    """Base exception for provider errors."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
