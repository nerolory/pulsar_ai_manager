"""Global provider state management.

This module re-exports set_provider/get_provider from the new
core.provider_registry module for backward compatibility.
All existing imports of `from app.state import ...` continue to work.
"""

from app.core.provider_registry import set_provider, get_provider  # noqa: F401
