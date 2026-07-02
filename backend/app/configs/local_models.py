"""Configuration for local LLM models.

Each model is a GGUF file downloaded from Hugging Face and run via llama-cpp-python
inside the backend process — no external Ollama or other services required.
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
    hf_repo: str
    hf_filename: str
    format: str  # always "gguf" for inference
    context_length: int
    quantization: str


LOCAL_MODELS: dict[str, dict[str, ModelInfo]] = {
    "very_light": {
        "tinyllama-1.1b": ModelInfo(
            name="TinyLlama-1.1B-Chat-v1.0",
            params="1.1B",
            tier="very_light",
            requirements=ModelRequirements(ram_gb=3.0, cpu_cores=2, disk_gb=1.0, gpu_vram_gb=None),
            hf_repo="TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
            hf_filename="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            format="gguf",
            context_length=2048,
            quantization="Q4_K_M",
        ),
        "phi-3-mini-2.7b": ModelInfo(
            name="Phi-3-mini (Q4)",
            params="3.8B",
            tier="very_light",
            requirements=ModelRequirements(ram_gb=4.0, cpu_cores=2, disk_gb=3.0, gpu_vram_gb=None),
            hf_repo="bartowski/Phi-3-mini-4k-instruct-GGUF",
            hf_filename="Phi-3-mini-4k-instruct-Q4_K_M.gguf",
            format="gguf",
            context_length=4096,
            quantization="Q4_K_M",
        ),
    },
    "light": {
        "phi-3-mini-3.8b": ModelInfo(
            name="Phi-3-mini-3.8B",
            params="3.8B",
            tier="light",
            requirements=ModelRequirements(ram_gb=6.0, cpu_cores=4, disk_gb=3.0, gpu_vram_gb=None),
            hf_repo="bartowski/Phi-3-mini-4k-instruct-GGUF",
            hf_filename="Phi-3-mini-4k-instruct-Q4_K_M.gguf",
            format="gguf",
            context_length=4096,
            quantization="Q4_K_M",
        ),
        "qwen-1.5-1.8b": ModelInfo(
            name="Qwen-1.5-1.8B-Chat",
            params="1.8B",
            tier="light",
            requirements=ModelRequirements(ram_gb=4.0, cpu_cores=4, disk_gb=2.0, gpu_vram_gb=None),
            hf_repo="Qwen/Qwen1.5-1.8B-Chat-GGUF",
            hf_filename="qwen1_5-1.8b-chat-q4_k_m.gguf",
            format="gguf",
            context_length=32768,
            quantization="Q4_K_M",
        ),
    },
    "medium": {
        "phi-3-medium-4b": ModelInfo(
            name="Phi-3-medium-4B",
            params="4B",
            tier="medium",
            requirements=ModelRequirements(ram_gb=8.0, cpu_cores=6, disk_gb=5.0, gpu_vram_gb=4.0),
            hf_repo="bartowski/Phi-3-medium-4k-instruct-GGUF",
            hf_filename="Phi-3-medium-4k-instruct-Q4_K_M.gguf",
            format="gguf",
            context_length=4096,
            quantization="Q4_K_M",
        ),
        "qwen-1.5-7b": ModelInfo(
            name="Qwen-1.5-7B-Chat",
            params="7B",
            tier="medium",
            requirements=ModelRequirements(ram_gb=12.0, cpu_cores=6, disk_gb=6.0, gpu_vram_gb=6.0),
            hf_repo="Qwen/Qwen1.5-7B-Chat-GGUF",
            hf_filename="qwen1_5-7b-chat-q4_k_m.gguf",
            format="gguf",
            context_length=32768,
            quantization="Q4_K_M",
        ),
    },
}


def get_model_info(model_id: str) -> ModelInfo | None:
    """Get model information by ID."""
    for tier_models in LOCAL_MODELS.values():
        if model_id in tier_models:
            return tier_models[model_id]
    return None


def get_models_by_tier(tier: str) -> dict[str, ModelInfo]:
    """Get all models for a specific tier."""
    return LOCAL_MODELS.get(tier, {})


def get_all_models() -> dict[str, ModelInfo]:
    """Get all available models."""
    all_models: dict[str, ModelInfo] = {}
    for tier_models in LOCAL_MODELS.values():
        all_models.update(tier_models)
    return all_models


def get_recommended_model(ram_gb: float, cpu_cores: int, has_gpu: bool) -> str | None:
    """Get recommended model based on system specs."""
    if has_gpu and ram_gb >= 8.0 and cpu_cores >= 6:
        medium_models = get_models_by_tier("medium")
        if medium_models:
            return next(iter(medium_models))

    if ram_gb >= 6.0 and cpu_cores >= 4:
        light_models = get_models_by_tier("light")
        if light_models:
            return next(iter(light_models))

    if ram_gb >= 3.0 and cpu_cores >= 2:
        very_light_models = get_models_by_tier("very_light")
        if very_light_models:
            return next(iter(very_light_models))

    return None


def can_run_model(
    model_id: str, ram_gb: float, cpu_cores: int, has_gpu: bool, gpu_vram_gb: float = 0
) -> tuple[bool, str, str | None, dict[str, str | float | int] | None]:
    """Check if system can run a specific model.

    Returns:
        (can_run, reason, reason_code, reason_params)
    """
    model_info = get_model_info(model_id)
    if not model_info:
        return False, f"Model {model_id} not found", "local_model_not_found", {"model_id": model_id}

    req = model_info["requirements"]

    if ram_gb < req["ram_gb"]:
        return (
            False,
            f"Insufficient RAM: {ram_gb}GB < {req['ram_gb']}GB required",
            "local_model_insufficient_ram",
            {"ram_gb": round(ram_gb, 1), "required_gb": req["ram_gb"]},
        )

    if cpu_cores < req["cpu_cores"]:
        return (
            False,
            f"Insufficient CPU cores: {cpu_cores} < {req['cpu_cores']} required",
            "local_model_insufficient_cpu",
            {"cpu_cores": cpu_cores, "required_cores": req["cpu_cores"]},
        )

    if req["gpu_vram_gb"] and (not has_gpu or gpu_vram_gb < req["gpu_vram_gb"]):
        return (
            False,
            f"Insufficient GPU VRAM: {gpu_vram_gb}GB < {req['gpu_vram_gb']}GB required",
            "local_model_insufficient_vram",
            {"vram_gb": round(gpu_vram_gb, 1), "required_gb": req["gpu_vram_gb"]},
        )

    return True, "System meets requirements", "local_model_meets_requirements", None
