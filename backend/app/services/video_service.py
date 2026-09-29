import os
import uuid
import tempfile
from fastapi import UploadFile

from app.core.config import settings
from app.core.logging import logger
from app.core.errors import VideoValidationError


async def validate_and_save_upload(file: UploadFile) -> str:
    """Validate the uploaded video and save it to a temporary path."""
    if not file.filename:
        raise VideoValidationError("No filename provided.")

    extension = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if extension not in settings.allowed_extensions_list:
        raise VideoValidationError(
            f"Unsupported file type: '.{extension}'. "
            f"Allowed: {settings.allowed_extensions_list}"
        )

    content = await file.read()
    if len(content) == 0:
        raise VideoValidationError("Uploaded file is empty.")

    if len(content) > settings.max_upload_bytes:
        raise VideoValidationError(
            f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    temp_dir = tempfile.gettempdir()
    unique_name = f"realeyes_{uuid.uuid4().hex}.{extension}"
    temp_path = os.path.join(temp_dir, unique_name)

    with open(temp_path, "wb") as f:
        f.write(content)

    logger.info(f"Saved upload to {temp_path} ({len(content)} bytes)")
    return temp_path


def cleanup_temp_file(file_path: str) -> None:
    """Safely delete a temporary file after inference."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to clean up {file_path}: {e}")