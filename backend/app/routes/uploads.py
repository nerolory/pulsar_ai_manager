"""File upload routes for image attachments.

Supports uploading images with type and size validation,
and serving them back to clients.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from loguru import logger
import uuid
import mimetypes

from app.paths import UPLOADS_DIR

router = APIRouter(prefix="/uploads", tags=["uploads"])
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """Accept and store an uploaded image file.

    Args:
        file: Uploaded file object.

    Returns:
        dict: File id and public URL.

    Raises:
        HTTPException: 415 for unsupported types, 413 for oversized files.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported type: {file.content_type}")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    ext = mimetypes.guess_extension(file.content_type) or ".bin"
    if ext == ".jpe":
        ext = ".jpg"
    file_id = str(uuid.uuid4()) + ext
    dest = UPLOADS_DIR / file_id
    dest.write_bytes(data)

    logger.debug(f"Saved upload: {file_id} ({len(data)} bytes)")
    return {"id": file_id, "url": f"/api/v1/uploads/{file_id}"}


@router.get("/{file_id}")
async def get_file(file_id: str):
    """Serve a previously uploaded file by its identifier.

    Args:
        file_id: UUID-based file identifier.

    Returns:
        FileResponse: The requested file with appropriate media type.

    Raises:
        HTTPException: 404 if the file does not exist.
    """
    path = UPLOADS_DIR / file_id
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    media_type, _ = mimetypes.guess_type(str(path))
    return FileResponse(str(path), media_type=media_type or "application/octet-stream")
