"""Registry of free LLM providers and their model groups.

Note: Limits are now fetched dynamically from provider APIs.
This registry only contains provider identification and grouping information.
"""

FREE_MODELS = {
    # Russian providers (no VPN required)
    "gigachat": {
        "provider": "gigachat",
        "is_free": True,
        "region": "ru",
        "model_group_id": "gigachat",
    },
    "yandexgpt": {
        "provider": "yandexgpt",
        "is_free": True,
        "region": "ru",
        "model_group_id": "yandexgpt",
    },
    "protalk": {
        "provider": "protalk",
        "is_free": True,
        "region": "ru",
        "model_group_id": "protalk",
    },
    
    # International providers
    "groq": {
        "provider": "groq",
        "is_free": True,
        "region": "global",
        "model_group_id": "groq",
    },
    "cerebras": {
        "provider": "cerebras",
        "is_free": True,
        "region": "global",
        "model_group_id": "cerebras",
    },
    "openrouter": {
        "provider": "openrouter",
        "is_free": True,
        "region": "global",
        "model_group_id": "openrouter",
    },
    "qwen": {
        "provider": "qwen",
        "is_free": True,
        "region": "global",
        "model_group_id": "qwen",
    },
    "gemini": {
        "provider": "gemini",
        "is_free": True,
        "region": "global",
        "model_group_id": "gemini",
    },
    "mistral": {
        "provider": "mistral",
        "is_free": True,
        "region": "global",
        "model_group_id": "mistral",
    },
    "huggingface": {
        "provider": "huggingface",
        "is_free": True,
        "region": "global",
        "model_group_id": "huggingface",
    },
}

MODEL_GROUPS = {
    "gigachat": {
        "id": "gigachat",
        "name": "GigaChat",
        "description": "Russian LLM by Sber",
    },
    "yandexgpt": {
        "id": "yandexgpt",
        "name": "YandexGPT",
        "description": "Russian LLM by Yandex",
    },
    "protalk": {
        "id": "protalk",
        "name": "ProTalk",
        "description": "Russian LLM platform",
    },
    "groq": {
        "id": "groq",
        "name": "Groq",
        "description": "Fast inference platform",
    },
    "cerebras": {
        "id": "cerebras",
        "name": "Cerebras",
        "description": "Fast inference platform",
    },
    "openrouter": {
        "id": "openrouter",
        "name": "OpenRouter",
        "description": "Multi-provider LLM router",
    },
    "qwen": {
        "id": "qwen",
        "name": "Qwen",
        "description": "Alibaba Cloud LLM",
    },
    "gemini": {
        "id": "gemini",
        "name": "Gemini",
        "description": "Google LLM",
    },
    "mistral": {
        "id": "mistral",
        "name": "Mistral",
        "description": "Mistral AI LLM",
    },
    "huggingface": {
        "id": "huggingface",
        "name": "Hugging Face",
        "description": "Hugging Face Inference API",
    },
}


def get_free_models() -> dict:
    """Get all free models registry."""
    return FREE_MODELS


def get_model_groups() -> dict:
    """Get all model groups."""
    return MODEL_GROUPS


def is_model_free(model_id: str) -> bool:
    """Check if a model is free."""
    for provider, data in FREE_MODELS.items():
        if model_id.startswith(provider):
            return data["is_free"]
    return False


def get_model_group(model_id: str) -> str | None:
    """Get model group ID for a model."""
    for provider, data in FREE_MODELS.items():
        if model_id.startswith(provider):
            return data.get("model_group_id")
    return None
