"""System requirements checker for local LLM support.

This module checks if the system meets the requirements for running local LLM models.
"""

import platform
import psutil
from typing import Literal, TypedDict
from loguru import logger


class SystemSpecs(TypedDict):
    """System specifications."""
    total_ram_gb: float
    available_ram_gb: float
    cpu_cores: int
    cpu_threads: int
    cpu_freq_ghz: float
    gpu_available: bool
    gpu_name: str | None
    gpu_vram_gb: float | None
    disk_free_gb: float
    os_name: str
    os_version: str
    architecture: str


class HardwareTier(TypedDict):
    """Hardware capability tier."""
    tier: Literal["very_light", "light", "medium", "unsupported"]
    can_run_local_llm: bool
    recommended_model: str | None
    reason: str


# Minimum requirements for each tier
REQUIREMENTS = {
    "very_light": {
        "ram_gb": 4,
        "cpu_cores": 2,
        "disk_gb": 5,
        "description": "Very light: < 1GB RAM, CPU only (базовые ответы)"
    },
    "light": {
        "ram_gb": 8,
        "cpu_cores": 4,
        "disk_gb": 10,
        "description": "Light: 2-4GB RAM, CPU only (расширенные ответы)"
    },
    "medium": {
        "ram_gb": 16,
        "cpu_cores": 6,
        "disk_gb": 20,
        "description": "Medium: 8GB RAM, CPU/GPU (полноценный помощник)"
    }
}


def get_system_specs() -> SystemSpecs:
    """Get current system specifications."""
    # RAM
    ram = psutil.virtual_memory()
    total_ram_gb = ram.total / (1024**3)
    available_ram_gb = ram.available / (1024**3)
    
    # CPU
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    cpu_freq_ghz = cpu_freq.max / 1000 if cpu_freq else 0.0
    
    # GPU
    gpu_available = False
    gpu_name = None
    gpu_vram_gb = None
    
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_available = True
            gpu = gpus[0]
            gpu_name = gpu.name
            gpu_vram_gb = gpu.memoryTotal / 1024
    except ImportError:
        logger.debug("GPUtil not installed, GPU detection skipped")
    except Exception as e:
        logger.debug(f"GPU detection failed: {e}")
    
    # Disk
    disk = psutil.disk_usage('/')
    disk_free_gb = disk.free / (1024**3)
    
    # OS
    os_name = platform.system()
    os_version = platform.version()
    architecture = platform.machine()
    
    return SystemSpecs(
        total_ram_gb=round(total_ram_gb, 2),
        available_ram_gb=round(available_ram_gb, 2),
        cpu_cores=cpu_cores,
        cpu_threads=cpu_threads,
        cpu_freq_ghz=round(cpu_freq_ghz, 2),
        gpu_available=gpu_available,
        gpu_name=gpu_name,
        gpu_vram_gb=round(gpu_vram_gb, 2) if gpu_vram_gb else None,
        disk_free_gb=round(disk_free_gb, 2),
        os_name=os_name,
        os_version=os_version,
        architecture=architecture
    )


def check_hardware_tier(specs: SystemSpecs) -> HardwareTier:
    """Determine hardware capability tier based on system specs."""
    # Check medium tier
    if (specs["total_ram_gb"] >= REQUIREMENTS["medium"]["ram_gb"] and
        specs["cpu_cores"] >= REQUIREMENTS["medium"]["cpu_cores"] and
        specs["disk_free_gb"] >= REQUIREMENTS["medium"]["disk_gb"]):
        return HardwareTier(
            tier="medium",
            can_run_local_llm=True,
            recommended_model="Phi-3-medium (3.8B) or Qwen-1.5B",
            reason="System meets medium tier requirements"
        )
    
    # Check light tier
    if (specs["total_ram_gb"] >= REQUIREMENTS["light"]["ram_gb"] and
        specs["cpu_cores"] >= REQUIREMENTS["light"]["cpu_cores"] and
        specs["disk_free_gb"] >= REQUIREMENTS["light"]["disk_gb"]):
        return HardwareTier(
            tier="light",
            can_run_local_llm=True,
            recommended_model="Phi-3-mini (3.8B) quantized",
            reason="System meets light tier requirements"
        )
    
    # Check very light tier
    if (specs["total_ram_gb"] >= REQUIREMENTS["very_light"]["ram_gb"] and
        specs["cpu_cores"] >= REQUIREMENTS["very_light"]["cpu_cores"] and
        specs["disk_free_gb"] >= REQUIREMENTS["very_light"]["disk_gb"]):
        return HardwareTier(
            tier="very_light",
            can_run_local_llm=True,
            recommended_model="TinyLlama (1.1B) or Phi-3-mini (2.7B)",
            reason="System meets very light tier requirements"
        )
    
    # Unsupported
    return HardwareTier(
        tier="unsupported",
        can_run_local_llm=False,
        recommended_model=None,
        reason=f"Insufficient resources: RAM {specs['total_ram_gb']}GB (min {REQUIREMENTS['very_light']['ram_gb']}GB), CPU cores {specs['cpu_cores']} (min {REQUIREMENTS['very_light']['cpu_cores']})"
    )


def check_cpu_features() -> dict[str, bool]:
    """Check CPU features for LLM performance."""
    features = {
        "avx": False,
        "avx2": False,
        "sse": False,
        "sse2": False
    }
    
    try:
        import cpuinfo
        info = cpuinfo.get_cpu_info()
        flags = info.get('flags', [])
        
        features["avx"] = "avx" in flags
        features["avx2"] = "avx2" in flags
        features["sse"] = "sse" in flags
        features["sse2"] = "sse2" in flags
    except ImportError:
        logger.debug("py-cpuinfo not installed, CPU feature detection skipped")
    except Exception as e:
        logger.debug(f"CPU feature detection failed: {e}")
    
    return features
