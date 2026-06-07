"""Voice routes: audio transcription (STT) via Whisper."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from loguru import logger

router = APIRouter(prefix="/voice", tags=["voice"])

ALLOWED_AUDIO_TYPES = {
    "audio/webm", "audio/ogg", "audio/wav", "audio/mp4",
    "audio/mpeg", "audio/mp3", "audio/x-m4a", "audio/m4a",
}
MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25 MB (Whisper API limit)


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio using OpenAI Whisper API.

    Args:
        file: Audio file (webm, ogg, wav, mp4, mp3, m4a).

    Returns:
        dict: Transcribed text.

    Raises:
        HTTPException: 415 for unsupported types, 413 for oversized files,
                       503 if no provider configured or provider doesn't support Whisper.
    """
    content_type = file.content_type or ""
    # Allow any audio/* type as browser may send audio/webm;codecs=opus
    if not content_type.startswith("audio/") and content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported audio type: {content_type}")

    data = await file.read()
    if len(data) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=413, detail="Audio file too large (max 25 MB)")

    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")

    try:
        from app.routes.settings import get_provider
        from openai import AsyncOpenAI
        import io

        # Try to use active provider's API key for Whisper
        provider = get_provider()

        # Determine API key and base URL for Whisper
        api_key = None
        base_url = None

        if provider is not None:
            # Extract client info from provider
            if hasattr(provider, '_client'):
                client = provider._client
                api_key = client.api_key
                # Only use OpenAI-compatible base URLs
                base_url_str = str(client.base_url) if client.base_url else None
                # Whisper is only available on OpenAI and compatible APIs
                if base_url_str and "openai.com" not in base_url_str:
                    # Try with OpenAI directly
                    base_url = None

        if not api_key:
            raise HTTPException(
                status_code=503,
                detail="Whisper transcription requires an OpenAI-compatible provider with a valid API key"
            )

        whisper_client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        # Determine file extension from content type
        ext_map = {
            "audio/webm": "webm",
            "audio/ogg": "ogg",
            "audio/wav": "wav",
            "audio/mp4": "mp4",
            "audio/mpeg": "mp3",
            "audio/mp3": "mp3",
            "audio/x-m4a": "m4a",
            "audio/m4a": "m4a",
        }
        # Strip codecs suffix: "audio/webm;codecs=opus" -> "audio/webm"
        base_ct = content_type.split(";")[0].strip()
        ext = ext_map.get(base_ct, "webm")

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
