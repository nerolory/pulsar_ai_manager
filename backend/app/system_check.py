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
    reason_code: str
    reason_params: dict[str, str | float | int] | None
    description_code: str


# Minimum requirements for each tier
REQUIREMENTS = {
    "very_light": {
        "ram_gb": 4,
        "cpu_cores": 2,
        "disk_gb": 5,
        "description_code": "system_check_very_light",
    },
    "light": {
        "ram_gb": 8,
        "cpu_cores": 4,
        "disk_gb": 10,
        "description_code": "system_check_light",
    },
    "medium": {
        "ram_gb": 16,
        "cpu_cores": 6,
        "disk_gb": 20,
        "description_code": "system_check_medium",
    },
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

    # Check for manual GPU override from environment
    import os

    manual_gpu_name = os.environ.get("MANUAL_GPU_NAME")
    manual_gpu_vram = os.environ.get("MANUAL_GPU_VRAM")

    if manual_gpu_name and manual_gpu_vram:
        gpu_available = True
        gpu_name = manual_gpu_name
        gpu_vram_gb = float(manual_gpu_vram)
        logger.info(f"Using manual GPU override: {gpu_name} ({gpu_vram_gb}GB)")
    else:
        # 1. Try pynvml (NVIDIA, works natively on host)
        try:
            import pynvml

            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                gpu_available = True
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                gpu_name = pynvml.nvmlDeviceGetName(handle)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_vram_gb = mem_info.total / (1024**3)
                logger.info(f"NVIDIA GPU detected via pynvml: {gpu_name}")
            pynvml.nvmlShutdown()
        except Exception:
            pass

        # 2. If not found, try nvidia-smi (works on host, fails in Docker without GPU passthrough)
        if not gpu_available:
            try:
                import subprocess

                result = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=name,memory.total",
                        "--format=csv,noheader,nounits",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    parts = result.stdout.strip().split(",")
                    if len(parts) >= 2:
                        gpu_available = True
                        gpu_name = parts[0].strip()
                        gpu_vram_gb = float(parts[1].strip()) / 1024  # MiB -> GB
                        logger.info(f"NVIDIA GPU detected via nvidia-smi: {gpu_name}")
            except Exception as e:
                logger.debug(f"nvidia-smi failed: {e}")

        # 3. Fallback: WMI for Windows (detects NVIDIA, AMD, Intel — any GPU)
        if not gpu_available and platform.system() == "Windows":
            try:
                import subprocess

                result = subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        "Get-WmiObject Win32_VideoController | Select-Object -First 1 Name,AdapterRAM | ConvertTo-Csv -NoTypeInformation",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    lines = [
                        l.strip().strip('"') for l in result.stdout.strip().split("\n") if l.strip()
                    ]
                    if len(lines) >= 2:
                        header = [h.strip().strip('"') for h in lines[0].split(",")]
                        values = [v.strip().strip('"') for v in lines[1].split(",")]
                        row = dict(zip(header, values))
                        name = row.get("Name", "")
                        vram_bytes = row.get("AdapterRAM", "0")
                        if name and name != "NULL":
                            gpu_available = True
                            gpu_name = name
                            try:
                                gpu_vram_gb = int(vram_bytes) / (1024**3)
                            except Exception:
                                gpu_vram_gb = 0
                            logger.info(f"GPU detected via WMI: {gpu_name}")
            except Exception as e:
                logger.debug(f"WMI GPU detection failed: {e}")

        # 4. Fallback: /sys/class/drm for Linux (AMD, Intel, NVIDIA)
        if not gpu_available and platform.system() == "Linux":
            try:
                import subprocess

                result = subprocess.run(["lspci", "-v"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split("\n"):
                        if "VGA compatible" in line or "3D controller" in line:
                            if any(v in line for v in ["NVIDIA", "AMD", "ATI", "Intel"]):
                                gpu_available = True
                                gpu_name = line.split(":")[-1].strip()
                                logger.info(f"GPU detected via lspci: {gpu_name}")
                                break
            except Exception as e:
                logger.debug(f"lspci GPU detection failed: {e}")

    # Disk
    disk = psutil.disk_usage("/")
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
        architecture=architecture,
    )


def check_hardware_tier(specs: SystemSpecs) -> HardwareTier:
    """Determine hardware capability tier based on system specs."""
    # Check medium tier
    if (
        specs["total_ram_gb"] >= REQUIREMENTS["medium"]["ram_gb"]
        and specs["cpu_cores"] >= REQUIREMENTS["medium"]["cpu_cores"]
        and specs["disk_free_gb"] >= REQUIREMENTS["medium"]["disk_gb"]
    ):
        return HardwareTier(
            tier="medium",
            can_run_local_llm=True,
            recommended_model="Phi-3-medium (3.8B) or Qwen-1.5-7B",
            reason="System meets medium tier requirements",
            reason_code="system_check_tier_medium",
            reason_params=None,
            description_code=REQUIREMENTS["medium"]["description_code"],
        )

    # Check light tier
    if (
        specs["total_ram_gb"] >= REQUIREMENTS["light"]["ram_gb"]
        and specs["cpu_cores"] >= REQUIREMENTS["light"]["cpu_cores"]
        and specs["disk_free_gb"] >= REQUIREMENTS["light"]["disk_gb"]
    ):
        return HardwareTier(
            tier="light",
            can_run_local_llm=True,
            recommended_model="Phi-3-mini (3.8B) quantized",
            reason="System meets light tier requirements",
            reason_code="system_check_tier_light",
            reason_params=None,
            description_code=REQUIREMENTS["light"]["description_code"],
        )

    # Check very light tier
    if (
        specs["total_ram_gb"] >= REQUIREMENTS["very_light"]["ram_gb"]
        and specs["cpu_cores"] >= REQUIREMENTS["very_light"]["cpu_cores"]
        and specs["disk_free_gb"] >= REQUIREMENTS["very_light"]["disk_gb"]
    ):
        return HardwareTier(
            tier="very_light",
            can_run_local_llm=True,
            recommended_model="TinyLlama (1.1B) or Phi-3-mini (Q4)",
            reason="System meets very light tier requirements",
            reason_code="system_check_tier_very_light",
            reason_params=None,
            description_code=REQUIREMENTS["very_light"]["description_code"],
        )

    # Unsupported
    return HardwareTier(
        tier="unsupported",
        can_run_local_llm=False,
        recommended_model=None,
        reason=(
            f"Insufficient resources: RAM {specs['total_ram_gb']:.1f}GB "
            f"(min {REQUIREMENTS['very_light']['ram_gb']}GB), CPU cores {specs['cpu_cores']} "
            f"(min {REQUIREMENTS['very_light']['cpu_cores']})"
        ),
        reason_code="system_check_tier_unsupported",
        reason_params={
            "ram": round(specs["total_ram_gb"], 1),
            "min_ram": REQUIREMENTS["very_light"]["ram_gb"],
            "cpu_cores": specs["cpu_cores"],
            "min_cpu": REQUIREMENTS["very_light"]["cpu_cores"],
        },
        description_code="system_check_error",
    )


def check_cpu_features() -> dict[str, bool]:
    """Check CPU features for LLM performance."""
    features = {"avx": False, "avx2": False, "sse": False, "sse2": False}

    try:
        import cpuinfo

        info = cpuinfo.get_cpu_info()
        flags = info.get("flags", [])

        features["avx"] = "avx" in flags
        features["avx2"] = "avx2" in flags
        features["sse"] = "sse" in flags
        features["sse2"] = "sse2" in flags
    except ImportError:
        logger.debug("py-cpuinfo not installed, CPU feature detection skipped")
    except Exception as e:
        logger.debug(f"CPU feature detection failed: {e}")

    return features
