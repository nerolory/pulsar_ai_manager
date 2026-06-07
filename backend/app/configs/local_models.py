"""Configuration for local LLM models.

This module defines available local LLM models with their characteristics,
requirements, and download sources.
"""

from typing import TypedDict, Literal


class ModelRequirements(TypedDict):
    """Minimum hardware requirements for a model."""
    ram_gb: float
    cpu_cores: int
    disk_gb: float
    gpu_vram_gb: float | None


class ModelInfo(TypedDict):
    """Information about a local LLM model."""
    name: str
    params: str
    tier: Literal["very_light", "light", "medium"]
    requirements: ModelRequirements
    download_url: str
    format: str  # "gguf", "safetensors", "pytorch"
    context_length: int
    quantization: str  # "4bit", "8bit", "fp16"


LOCAL_MODELS: dict[str, dict[str, ModelInfo]] = {
    "very_light": {
        "tinyllama-1.1b": ModelInfo(
            name="TinyLlama-1.1B-Chat-v1.0",
            params="1.1B",
            tier="very_light",
            requirements=ModelRequirements(
                ram_gb=3.0,
                cpu_cores=2,
                disk_gb=3.0,
                gpu_vram_gb=None
            ),
            download_url="https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            format="gguf",
            context_length=2048,
            quantization="4bit"
        ),
        "phi-3-mini-2.7b": ModelInfo(
            name="Phi-3-mini-2.7B",
            params="2.7B",
            tier="very_light",
            requirements=ModelRequirements(
                ram_gb=4.0,
                cpu_cores=2,
                disk_gb=4.0,
                gpu_vram_gb=None
            ),
            download_url="https://huggingface.co/microsoft/Phi-3-mini-4k-instruct",
            format="gguf",
            context_length=4096,
            quantization="4bit"
        )
    },
    "light": {
        "phi-3-mini-3.8b": ModelInfo(
            name="Phi-3-mini-3.8B",
            params="3.8B",
            tier="light",
            requirements=ModelRequirements(
                ram_gb=6.0,
                cpu_cores=4,
                disk_gb=6.0,
                gpu_vram_gb=4.0
            ),
            download_url="https://huggingface.co/microsoft/Phi-3-mini-4k-instruct",
            format="gguf",
            context_length=4096,
            quantization="4bit"
        ),
        "qwen-1.5-1.8b": ModelInfo(
            name="Qwen-1.5-1.8B-Chat",
            params="1.8B",
            tier="light",
            requirements=ModelRequirements(
                ram_gb=4.0,
                cpu_cores=4,
                disk_gb=4.0,
                gpu_vram_gb=None
            ),
            download_url="https://huggingface.co/Qwen/Qwen1.5-1.8B-Chat",
            format="gguf",
            context_length=32768,
            quantization="4bit"
        )
    },
    "medium": {
        "phi-3-medium-4b": ModelInfo(
            name="Phi-3-medium-4B",
            params="4B",
            tier="medium",
            requirements=ModelRequirements(
                ram_gb=8.0,
                cpu_cores=6,
                disk_gb=8.0,
                gpu_vram_gb=6.0
            ),
            download_url="https://huggingface.co/microsoft/Phi-3-medium-4k-instruct",
            format="safetensors",
            context_length=4096,
            quantization="4bit"
        ),
        "qwen-1.5-7b": ModelInfo(
            name="Qwen-1.5-7B-Chat",
            params="7B",
            tier="medium",
            requirements=ModelRequirements(
                ram_gb=12.0,
                cpu_cores=6,
                disk_gb=12.0,
                gpu_vram_gb=8.0
            ),
            download_url="https://huggingface.co/Qwen/Qwen1.5-7B-Chat",
            format="safetensors",
            context_length=32768,
            quantization="4bit"
        )
    }
}


def get_model_info(model_id: str) -> ModelInfo | None:
    """Get model information by ID.
    
    Args:
        model_id: Model identifier (e.g., "phi-3-mini-3.8b")
        
    Returns:
        ModelInfo if found, None otherwise
    """
    for tier_models in LOCAL_MODELS.values():
        if model_id in tier_models:
            return tier_models[model_id]
    return None


def get_models_by_tier(tier: str) -> dict[str, ModelInfo]:
    """Get all models for a specific tier.
    
    Args:
        tier: Hardware tier ("very_light", "light", "medium")
        
    Returns:
        Dictionary of model_id -> ModelInfo
    """
    return LOCAL_MODELS.get(tier, {})


def get_all_models() -> dict[str, ModelInfo]:
    """Get all available models.
    
    Returns:
        Dictionary of model_id -> ModelInfo
    """
    all_models = {}
    for tier_models in LOCAL_MODELS.values():
        all_models.update(tier_models)
    return all_models


def get_recommended_model(ram_gb: float, cpu_cores: int, has_gpu: bool) -> str | None:
    """Get recommended model based on system specs.
    
    Args:
        ram_gb: Available RAM in GB
        cpu_cores: Number of CPU cores
        has_gpu: Whether GPU is available
        
    Returns:
        Model ID of recommended model, or None if no model fits
    """
    # Try medium tier first
    if has_gpu and ram_gb >= 8.0 and cpu_cores >= 6:
        medium_models = get_models_by_tier("medium")
        if medium_models:
            return list(medium_models.keys())[0]
    
    # Try light tier
    if ram_gb >= 6.0 and cpu_cores >= 4:
        light_models = get_models_by_tier("light")
        if light_models:
            return list(light_models.keys())[0]
    
    # Try very light tier
    if ram_gb >= 3.0 and cpu_cores >= 2:
        very_light_models = get_models_by_tier("very_light")
        if very_light_models:
            return list(very_light_models.keys())[0]
    
    return None


def can_run_model(model_id: str, ram_gb: float, cpu_cores: int, has_gpu: bool, gpu_vram_gb: float = 0) -> tuple[bool, str]:
    """Check if system can run a specific model.
    
    Args:
        model_id: Model identifier
        ram_gb: Available RAM in GB
        cpu_cores: Number of CPU cores
        has_gpu: Whether GPU is available
        gpu_vram_gb: Available GPU VRAM in GB
        
    Returns:
        Tuple of (can_run, reason)
    """
    model_info = get_model_info(model_id)
    if not model_info:
        return False, f"Model {model_id} not found"
    
    req = model_info["requirements"]
    
    # Check RAM
    if ram_gb < req["ram_gb"]:
        return False, f"Insufficient RAM: {ram_gb}GB < {req['ram_gb']}GB required"
    
    # Check CPU cores
    if cpu_cores < req["cpu_cores"]:
        return False, f"Insufficient CPU cores: {cpu_cores} < {req['cpu_cores']} required"
    
    # Check GPU VRAM if required
    if req["gpu_vram_gb"] and (not has_gpu or gpu_vram_gb < req["gpu_vram_gb"]):
        return False, f"Insufficient GPU VRAM: {gpu_vram_gb}GB < {req['gpu_vram_gb']}GB required"
    
    return True, "System meets requirements"
