"""Helpers for resolving multimodal image URLs to provider-native formats."""

from __future__ import annotations

import base64
import mimetypes
import re
from pathlib import Path
from typing import List, Union

import httpx

from app.paths import UPLOADS_DIR
from app.schemas import ContentPart

_DATA_URL_RE = re.compile(r"^data:([^;]+);base64,(.+)$", re.DOTALL)


def _safe_upload_path(file_id: str) -> Path | None:
    """Resolve upload file path and ensure it stays inside UPLOADS_DIR."""
    if not file_id or ".." in file_id or file_id.startswith(("/", "\\")):
        return None
    base = UPLOADS_DIR.resolve()
    path = (UPLOADS_DIR / file_id).resolve()
    try:
        path.relative_to(base)
    except ValueError:
        return None
    return path


async def resolve_image_base64(url: str) -> tuple[str, str]:
    """Resolve an image URL to (media_type, base64_data).

    Supports data URLs, local upload paths (/api/v1/uploads/...) and http(s) URLs.
    """
    if not url:
        raise ValueError("empty image url")

    data_match = _DATA_URL_RE.match(url.strip())
    if data_match:
        return data_match.group(1), data_match.group(2)

    file_id = url.rsplit("/", 1)[-1] if "/uploads/" in url else None
    if file_id:
        path = _safe_upload_path(file_id)
        if path and path.exists() and path.is_file():
            media_type, _ = mimetypes.guess_type(str(path))
            data = path.read_bytes()
            return media_type or "image/jpeg", base64.b64encode(data).decode("ascii")

    if url.startswith(("http://", "https://")):
        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            response = await client.get(url)
            response.raise_for_status()
            media_type = response.headers.get("content-type", "image/jpeg").split(";")[0].strip()
            return media_type, base64.b64encode(response.content).decode("ascii")

    raise ValueError(f"Unsupported image URL: {url[:120]}")


async def to_data_url(url: str) -> str:
    """Convert any supported image URL to a data: URL."""
    if _DATA_URL_RE.match(url.strip()):
        return url.strip()
    media_type, b64 = await resolve_image_base64(url)
    return f"data:{media_type};base64,{b64}"


async def to_openai_content(content: Union[str, List[ContentPart]]) -> Union[str, list[dict]]:
    """Convert message content to OpenAI-compatible format with resolved images."""
    if isinstance(content, str):
        return content

    parts: list[dict] = []
    for part in content:
        if part.type == "text":
            parts.append({"type": "text", "text": part.text or ""})
        elif part.type == "image_url" and part.image_url:
            data_url = await to_data_url(part.image_url.url)
            parts.append({"type": "image_url", "image_url": {"url": data_url}})
    return parts


async def to_mistral_content(content: Union[str, List[ContentPart]]) -> Union[str, list[dict]]:
    """Convert message content to Mistral multimodal format."""
    if isinstance(content, str):
        return content

    parts: list[dict] = []
    for part in content:
        if part.type == "text":
            parts.append({"type": "text", "text": part.text or ""})
        elif part.type == "image_url" and part.image_url:
            data_url = await to_data_url(part.image_url.url)
            parts.append({"type": "image_url", "image_url": data_url})
    return parts
