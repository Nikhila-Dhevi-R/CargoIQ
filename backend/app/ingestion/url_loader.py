import uuid
from pathlib import Path
import httpx
from fastapi import HTTPException
from app.core.config import UPLOADS_DIR
from app.core.logging import logger

async def download_video_from_url(url: str) -> tuple[str, str]:
    """
    Downloads direct video URL into storage/uploads/.
    Returns (saved_file_path, filename).
    """
    url_clean = url.strip()
    if not url_clean.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL scheme. Must start with http:// or https://"
        )

    # Check extension or test head request
    ext = ".mp4"
    if url_clean.endswith((".avi", ".mov", ".mkv", ".mp4")):
        ext = Path(url_clean.split("?")[0]).suffix.lower()

    unique_id = uuid.uuid4().hex[:10]
    filename = f"url_{unique_id}{ext}"
    dest_path = UPLOADS_DIR / filename

    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            resp = await client.get(url_clean)
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to fetch video URL. HTTP status: {resp.status_code}"
                )

            with open(dest_path, "wb") as f:
                f.write(resp.content)

            if dest_path.stat().st_size < 1000:
                dest_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=400,
                    detail="Downloaded video file is empty or corrupted."
                )

            return str(dest_path), filename
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading video from URL {url}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Unable to access or download video from URL: {str(e)}"
        )
