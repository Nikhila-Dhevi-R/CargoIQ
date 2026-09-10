import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import UPLOADS_DIR, settings

def save_uploaded_video(file: UploadFile) -> tuple[str, str]:
    """
    Saves uploaded file safely.
    Returns (saved_file_path, unique_filename).
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in [".mp4", ".avi", ".mov", ".mkv"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported video format: '{ext}'. Please upload an MP4, AVI, or MOV file."
        )

    unique_id = uuid.uuid4().hex[:10]
    safe_name = f"upload_{unique_id}{ext}"
    dest_path = UPLOADS_DIR / safe_name

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return str(dest_path), safe_name
