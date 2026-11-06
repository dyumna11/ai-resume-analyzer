import os
import uuid
import re
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from config import STORAGE_DIR, MAX_UPLOAD_SIZE

PDF_MAGIC_BYTES = b"%PDF-"


def sanitize_filename(filename: str) -> str:
    """Sanitize the original filename to prevent directory traversal or control characters."""
    base_name = os.path.basename(filename)
    # Strip any characters that are not alphanumeric, spaces, hyphens, underscores, or periods
    cleaned = re.sub(r"[^\w\s\.-]", "_", base_name).strip()
    return cleaned or "resume.pdf"


def validate_pdf_content(content: bytes) -> None:
    """Validate that the content is a genuine PDF by checking magic header bytes and size."""
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if len(content) > MAX_UPLOAD_SIZE:
        max_mb = MAX_UPLOAD_SIZE // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {max_mb}MB."
        )

    if not content.startswith(PDF_MAGIC_BYTES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Uploaded file is not a valid PDF document."
        )


async def save_uploaded_resume(file: UploadFile) -> Tuple[str, str, bytes]:
    """
    Validate, sanitize, and safely save an uploaded PDF resume to disk.
    Returns (safe_display_filename, safe_absolute_filepath, file_content_bytes).
    """
    # Check mime type and extension
    filename = file.filename or "resume.pdf"
    clean_display_name = sanitize_filename(filename)

    if not clean_display_name.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF (.pdf) files are supported."
        )

    content = await file.read()
    validate_pdf_content(content)

    # Generate a unique UUID-based safe storage filename
    unique_filename = f"{uuid.uuid4().hex}.pdf"
    secure_path = (STORAGE_DIR / unique_filename).resolve()

    # Prevent path traversal: ensure secure_path is strictly inside STORAGE_DIR
    if not str(secure_path).startswith(str(STORAGE_DIR.resolve())):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid destination storage path."
        )

    with open(secure_path, "wb") as f:
        f.write(content)

    return clean_display_name, str(secure_path), content


def delete_stored_file(file_path: str) -> None:
    """Safely delete a stored resume file from disk."""
    try:
        resolved = Path(file_path).resolve()
        # Ensure file is inside STORAGE_DIR before deleting
        if str(resolved).startswith(str(STORAGE_DIR.resolve())) and resolved.exists():
            resolved.unlink(missing_ok=True)
    except Exception:
        pass

