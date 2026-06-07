"""Voice routes: audio transcription (STT) via Whisper."""

import io

from fastapi import APIRouter, UploadFile, File, HTTPException
from loguru import logger
from openai import AsyncOpenAI

from app.state import get_provider
from app.storage import load_provider_config

router = APIRouter(prefix="/voice", tags=["voice"])

ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/wav",
    "audio/mp4",
    "audio/mpeg",
    "audio/mp3",
    "audio/x-m4a",
    "audio/m4a",
}
MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25 MB (Whisper API limit)

_EXT_MAP = {
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/wav": "wav",
    "audio/mp4": "mp4",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/x-m4a": "m4a",
    "audio/m4a": "m4a",
}


def _resolve_api_key() -> str:
    """Resolve an API key from active provider or saved config.

    Returns:
        API key string.

    Raises:
        HTTPException: If no API key can be found.
    """
    api_key = None
    provider = get_provider()

    if provider is not None and hasattr(provider, "_client"):
        api_key = provider._client.api_key

    if not api_key:
        config = load_provider_config()
        if config:
            api_key = config.get("api_key")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Whisper transcription requires an OpenAI-compatible provider with a valid API key",
        )
    return api_key


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio using OpenAI Whisper API.

    Args:
        file: Audio file (webm, ogg, wav, mp4, mp3, m4a).

    Returns:
        dict: Transcribed text.

    Raises:
        HTTPException: 415 for unsupported types, 413 for oversized files,
                       503 if no provider configured.
    """
    content_type = file.content_type or ""
    if not content_type.startswith("audio/") and content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported audio type: {content_type}")

    data = await file.read()
    if len(data) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=413, detail="Audio file too large (max 25 MB)")

    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")

    try:
        api_key = _resolve_api_key()
        whisper_client = AsyncOpenAI(api_key=api_key)

        base_ct = content_type.split(";")[0].strip()
        ext = _EXT_MAP.get(base_ct, "webm")
        audio_file = (f"audio.{ext}", io.BytesIO(data), content_type)

        transcription = await whisper_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ru",
        )

        logger.info(f"Transcribed {len(data)} bytes -> {len(transcription.text)} chars")
        return {"text": transcription.text}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
