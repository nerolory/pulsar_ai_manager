"""Storage module — backward-compatible re-export from StorageService.

All existing `from app.storage import ...` imports continue to work.
New code should use StorageService directly.
"""

from app.services.storage_service import StorageService

_service = StorageService()

# Backward-compatible function exports
save_provider_config = _service.save_provider_config
load_provider_config = _service.load_provider_config
load_provider_config_for = _service.load_provider_config_for
_load_yaml = _service._load_yaml
