import re
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB


class UploadValidationError(Exception):
    pass


def _safe_filename(name: str) -> str:
    name = Path(name).name  # strip any directory components
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name or "resume"


def validate_upload(file: UploadFile) -> str:
    """Returns the lowercase file extension, or raises UploadValidationError."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UploadValidationError(
            f"Unsupported file type '{ext or 'unknown'}'. Only PDF and DOCX are accepted."
        )
    return ext


def save_upload(file: UploadFile, raw_bytes: bytes) -> str:
    """Persist the uploaded file to disk with a unique name; returns the path."""
    if len(raw_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise UploadValidationError(f"File exceeds {MAX_FILE_SIZE_MB}MB limit.")
    if len(raw_bytes) == 0:
        raise UploadValidationError("Uploaded file is empty.")

    ext = Path(file.filename or "").suffix.lower()
    unique_name = f"{uuid.uuid4().hex}_{_safe_filename(file.filename or 'resume')}"
    dest = UPLOAD_DIR / unique_name
    dest.write_bytes(raw_bytes)
    return str(dest)
