"""Model downloader for local LLM models.

Downloads GGUF files from Hugging Face into backend/data/models/{model_id}/.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Callable, Optional

from loguru import logger

from app.paths import DATA_DIR
from app.configs.local_models import get_model_info

MODELS_DIR = DATA_DIR / "models"
MIN_GGUF_BYTES = 1_000_000  # 1 MB — reject HTML stubs / partial files


def get_model_path(model_id: str) -> Path:
    """Get the local directory for a model."""
    if not model_id or ".." in model_id or "/" in model_id or "\\" in model_id:
        raise ValueError(f"Invalid model id: {model_id}")
    path = (MODELS_DIR / model_id).resolve()
    if not path.is_relative_to(MODELS_DIR.resolve()):
        raise ValueError(f"Invalid model id: {model_id}")
    return path


def get_model_gguf_path(model_id: str) -> Path | None:
    """Return path to the downloaded GGUF file for a model, if present."""
    model_path = get_model_path(model_id)
    if not model_path.exists():
        return None

    model_info = get_model_info(model_id)
    if model_info:
        expected = model_path / model_info["hf_filename"]
        if expected.is_file() and expected.stat().st_size >= MIN_GGUF_BYTES:
            return expected

    for file_path in sorted(model_path.glob("*.gguf")):
        if file_path.is_file() and file_path.stat().st_size >= MIN_GGUF_BYTES:
            return file_path

    return None


def is_model_downloaded(model_id: str) -> bool:
    """Check if a valid GGUF file exists for the model."""
    return get_model_gguf_path(model_id) is not None


def get_model_size(model_id: str) -> int:
    """Get the size of a downloaded model in bytes."""
    gguf_path = get_model_gguf_path(model_id)
    return gguf_path.stat().st_size if gguf_path else 0


async def download_model(
    model_id: str, progress_callback: Optional[Callable[[int, int], None]] = None
) -> tuple[bool, str]:
    """Download a GGUF model file from Hugging Face.

    Returns:
        (success, message) — message is human-readable on failure.
    """
    model_info = get_model_info(model_id)
    if not model_info:
        msg = f"Model {model_id} not found in configuration"
        logger.error(msg)
        return False, msg

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = get_model_path(model_id)
    model_path.mkdir(parents=True, exist_ok=True)

    repo_id = model_info["hf_repo"]
    filename = model_info["hf_filename"]
    target = model_path / filename
    estimated_total = int(model_info["requirements"]["disk_gb"] * 1024**3)

    if target.is_file() and target.stat().st_size >= MIN_GGUF_BYTES:
        logger.info(f"Model {model_id} already downloaded at {target}")
        if progress_callback:
            size = target.stat().st_size
            progress_callback(size, size)
        return True, f"Model {model_id} already downloaded"

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        msg = "Missing huggingface_hub — rebuild backend: docker-compose build backend"
        logger.error(msg)
        return False, msg

    stop_polling = asyncio.Event()

    async def poll_partial_size() -> None:
        while not stop_polling.is_set():
            if target.is_file():
                done = target.stat().st_size
                if progress_callback:
                    progress_callback(done, estimated_total)
            await asyncio.sleep(0.4)

    poll_task = asyncio.create_task(poll_partial_size())

    try:
        def _download() -> str:
            token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
            return hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=str(model_path),
                token=token,
            )

        logger.info(f"Downloading {repo_id}/{filename} -> {model_path}")
        downloaded_path = await asyncio.to_thread(_download)
        path = Path(downloaded_path)

        if not path.is_file() or path.stat().st_size < MIN_GGUF_BYTES:
            msg = f"Downloaded file too small or missing ({path})"
            logger.error(msg)
            if path.is_file():
                path.unlink()
            return False, msg

        final_size = path.stat().st_size
        if progress_callback:
            progress_callback(final_size, final_size)

        size_mb = final_size / (1024**2)
        logger.info(f"Model {model_id} downloaded ({size_mb:.1f} MB)")
        return True, f"Model {model_id} downloaded ({size_mb:.0f} MB)"

    except Exception as e:
        msg = str(e)
        logger.error(f"Failed to download model {model_id}: {msg}")
        if target.is_file() and target.stat().st_size < MIN_GGUF_BYTES:
            target.unlink()
        return False, msg
    finally:
        stop_polling.set()
        await poll_task


def delete_model(model_id: str) -> bool:
    """Delete a downloaded model directory."""
    model_path = get_model_path(model_id)
    if not model_path.exists():
        return False

    try:
        for file_path in model_path.rglob("*"):
            if file_path.is_file():
                file_path.unlink()
        model_path.rmdir()
        logger.info(f"Model {model_id} deleted")
        return True
    except Exception as e:
        logger.error(f"Failed to delete model {model_id}: {e}")
        return False


def get_downloaded_models() -> list[str]:
    """Get list of model IDs with a valid GGUF on disk."""
    if not MODELS_DIR.exists():
        return []
    return [model_id for model_id in get_all_model_ids() if is_model_downloaded(model_id)]


def get_all_model_ids() -> list[str]:
    """List model directory names under MODELS_DIR."""
    if not MODELS_DIR.exists():
        return []
    return [d.name for d in MODELS_DIR.iterdir() if d.is_dir()]


def get_storage_info() -> dict:
    """Get information about model storage."""
    total_size = 0
    model_count = 0

    for model_id in get_all_model_ids():
        size = get_model_size(model_id)
        if size > 0:
            total_size += size
            model_count += 1

    return {
        "model_count": model_count,
        "total_size_gb": round(total_size / (1024**3), 2),
        "models_dir": str(MODELS_DIR),
    }
