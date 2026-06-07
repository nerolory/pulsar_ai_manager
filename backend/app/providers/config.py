"""Provider configuration constants.

This file contains the single source of truth for all LLM providers.
Used across schemas, routes, and frontend (via API).
"""

from typing import List, Dict

# List of all supported providers
PROVIDERS = [
    "openrouter",
    "vsellm",
    "openai",
    "anthropic",
    "groq",
    "cerebras",
    "qwen",
    "mistral",
    "gemini",
    "gigachat",
    "mock",
]

# Provider metadata for frontend
PROVIDER_METADATA: Dict[str, Dict[str, str]] = {
    "vsellm": {
        "name": "VseLLM",
        "desc": "GPT-4o, Claude, Gemini и другие · api.vsellm.ru",
        "key_placeholder": "sk-...",
        "default_model": "openai/gpt-4o-mini",
        "base_url": "https://api.vsellm.ru/v1",
    },
    "openrouter": {
        "name": "OpenRouter",
        "desc": "Qwen3, LLaMA 3.3, Mistral и 200+ моделей · Бесплатные доступны",
        "key_placeholder": "sk-or-v1-...",
        "default_model": "qwen/qwen3-235b-a22b:free",
        "base_url": "https://openrouter.ai/api/v1",
    },
    "openai": {
        "name": "OpenAI",
        "desc": "GPT-4o, GPT-4.1, o1 — требуется API-ключ",
        "key_placeholder": "sk-proj-...",
        "default_model": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1",
    },
    "anthropic": {
        "name": "Anthropic",
        "desc": "Claude 3.5 Sonnet, Opus, Haiku — нативный API",
        "key_placeholder": "sk-ant-...",
        "default_model": "claude-3-5-sonnet-20241022",
        "base_url": "https://api.anthropic.com",
    },
    "groq": {
        "name": "Groq",
        "desc": "Llama 3.1, Mixtral — сверхбыстрая инференция",
        "key_placeholder": "gsk_...",
        "default_model": "llama-3.1-70b-versatile",
        "base_url": "https://api.groq.com/openai/v1",
    },
    "cerebras": {
        "name": "Cerebras",
        "desc": "Llama 3.1, GPT-OSS — высокая скорость",
        "key_placeholder": "...",
        "default_model": "llama3.1-70b",
        "base_url": "https://api.cerebras.ai/v1",
    },
    "qwen": {
        "name": "Qwen (Alibaba)",
        "desc": "Qwen 3 Max, 3.6 Plus — 1M токенов бесплатно/90 дней",
        "key_placeholder": "sk-...",
        "default_model": "qwen-max",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    },
    "mistral": {
        "name": "Mistral AI",
        "desc": "Mistral Large, Mixtral — нативный API",
        "key_placeholder": "...",
        "default_model": "mistral-large-latest",
        "base_url": "https://api.mistral.ai/v1",
    },
    "gemini": {
        "name": "Google Gemini",
        "desc": "Gemini 2.0 Flash, Pro — нативный API",
        "key_placeholder": "...",
        "default_model": "gemini-2.0-flash-exp",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
    },
    "gigachat": {
        "name": "GigaChat",
        "desc": "GigaChat от Сбера — отложен (технический долг)",
        "key_placeholder": "...",
        "default_model": "",
        "base_url": "",
    },
    "mock": {
        "name": "Mock (тест)",
        "desc": "Тестовый провайдер без ключа — для разработки",
        "key_placeholder": "",
        "default_model": "",
        "base_url": "",
    },
}

# Base URL to provider mapping for auto-detection
BASE_URL_TO_PROVIDER: Dict[str, str] = {
    "api.vsellm.ru": "vsellm",
    "openrouter.ai": "openrouter",
    "api.openai.com": "openai",
    "api.anthropic.com": "anthropic",
    "api.groq.com": "groq",
    "api.cerebras.ai": "cerebras",
    "dashscope.aliyuncs.com": "qwen",
    "api.mistral.ai": "mistral",
    "generativelanguage.googleapis.com": "gemini",
}

# OpenAI-compatible providers (for custom base URLs)
OPENAI_COMPATIBLE_PROVIDERS = [
    "vsellm",
    "openrouter",
    "openai",
    "groq",
    "cerebras",
    "qwen",
    "mistral",
]

# Human-readable model names for display when no models are cached
PROVIDER_MODEL_NAMES: Dict[str, str] = {
    "vsellm": "GPT-4o",
    "openrouter": "Qwen 3",
    "openai": "GPT-4o",
    "anthropic": "Claude 3.5 Sonnet",
    "groq": "Llama 3.1",
    "cerebras": "Llama 3.1",
    "qwen": "Qwen 3",
    "mistral": "Mistral Large",
    "gemini": "Gemini",
    "gigachat": "GigaChat",
    "mock": "Mock Model",
}
