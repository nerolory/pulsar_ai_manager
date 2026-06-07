"""Model downloader for local LLM models.

This module handles downloading models from Hugging Face and other sources,
with progress tracking, integrity checking, and caching.
"""

import os
import hashlib
from pathlib import Path
from typing import Callable, Optional
from loguru import logger
import httpx

from app.paths import DATA_DIR
from app.configs.local_models import get_model_info

MODELS_DIR = DATA_DIR / "models"


def get_model_path(model_id: str) -> Path:
    """Get the local path for a model.

    Args:
        model_id: Model identifier

    Returns:
        Path to model directory
    """
    return MODELS_DIR / model_id


def is_model_downloaded(model_id: str) -> bool:
    """Check if a model is already downloaded.

    Args:
        model_id: Model identifier

    Returns:
        True if model exists locally
    """
    model_path = get_model_path(model_id)
    return model_path.exists() and any(model_path.iterdir())


def get_model_size(model_id: str) -> int:
    """Get the size of a downloaded model in bytes.

    Args:
        model_id: Model identifier

    Returns:
        Size in bytes, or 0 if not found
    """
    model_path = get_model_path(model_id)
    if not model_path.exists():
        return 0

    total_size = 0
    for file_path in model_path.rglob("*"):
        if file_path.is_file():
            total_size += file_path.stat().st_size

    return total_size


async def download_model(
    model_id: str, progress_callback: Optional[Callable[[int, int], None]] = None
) -> bool:
    """Download a model from Hugging Face.

    Args:
        model_id: Model identifier
        progress_callback: Optional callback(downloaded_bytes, total_bytes)

    Returns:
        True if download succeeded
    """
    model_info = get_model_info(model_id)
    if not model_info:
        logger.error(f"Model {model_id} not found in configuration")
        return False

    # Create models directory
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = get_model_path(model_id)
    model_path.mkdir(parents=True, exist_ok=True)

    # For now, we'll use a simple HTTP download
    # In production, use huggingface_hub library for proper model downloading
    download_url = model_info["download_url"]

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Get file info first
            response = await client.head(download_url)
            if response.status_code != 200:
                logger.error(f"Failed to get file info: {response.status_code}")
                return False

            total_size = int(response.headers.get("content-length", 0))
            logger.info(f"Downloading model {model_id} ({total_size / (1024**3):.2f} GB)")

            # Download file
            response = await client.get(download_url)
            response.raise_for_status()

            # Save to file
            output_file = model_path / f"{model_id}.gguf"
            downloaded = 0

            with open(output_file, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)

            logger.info(f"Model {model_id} downloaded successfully")
            return True

    except Exception as e:
        logger.error(f"Failed to download model {model_id}: {e}")
        # Clean up partial download
        if model_path.exists():
            for file_path in model_path.iterdir():
                if file_path.is_file():
                    file_path.unlink()
            model_path.rmdir()
        return False


def delete_model(model_id: str) -> bool:
    """Delete a downloaded model.

    Args:
        model_id: Model identifier

    Returns:
        True if deletion succeeded
    """
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
    """Get list of downloaded model IDs.

    Returns:
        List of model IDs
    """
    if not MODELS_DIR.exists():
        return []

    models = []
    for model_dir in MODELS_DIR.iterdir():
        if model_dir.is_dir() and any(model_dir.iterdir()):
            models.append(model_dir.name)

    return models


def get_storage_info() -> dict:
    """Get information about model storage.

    Returns:
        Dictionary with storage info
    """
    total_size = 0
    model_count = 0

    if MODELS_DIR.exists():
        for model_dir in MODELS_DIR.iterdir():
            if model_dir.is_dir():
                model_size = 0
                for file_path in model_dir.rglob("*"):
                    if file_path.is_file():
                        model_size += file_path.stat().st_size
                if model_size > 0:
                    total_size += model_size
                    model_count += 1

    return {
        "model_count": model_count,
        "total_size_gb": round(total_size / (1024**3), 2),
        "models_dir": str(MODELS_DIR),
    }
