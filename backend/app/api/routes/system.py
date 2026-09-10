import shutil
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.database import get_db
from app.assistant.ollama_client import ollama_client
from app.core.config import settings
from app.perception.detector import WarehouseDetector

router = APIRouter(prefix="/system", tags=["System Health"])

@router.get("/health")
async def get_system_health(db: Session = Depends(get_db)):
    # 1. Database check
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    # 2. Ollama check
    ollama_ok = await ollama_client.is_available()
    ollama_status = "healthy" if ollama_ok else "offline"

    # 3. Vision model check. Do not claim a model is loaded merely because a
    # configuration value exists; the detector itself reports no observations
    # when the model cannot run.
    try:
        from ultralytics import YOLO  # noqa: F401
        vision_status = "available" if WarehouseDetector.configured_model_exists() else "unavailable"
    except Exception:
        vision_status = "unavailable"

    # 4. FFmpeg check (via system or imageio_ffmpeg)
    ffmpeg_available = False
    if shutil.which("ffmpeg"):
        ffmpeg_available = True
    else:
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe:
                ffmpeg_available = True
        except Exception:
            ffmpeg_available = False

    return {
        "success": True,
        "data": {
            "backend": "healthy",
            "database": db_status,
            "ollama": ollama_status,
            "vision_model": vision_status,
            "ffmpeg": "available" if ffmpeg_available else "unavailable",
            "active_model": settings.OLLAMA_MODEL,
            "yolo_model": settings.YOLO_MODEL,
            "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
            "clip_pre_seconds": settings.CLIP_PRE_SECONDS,
            "clip_post_seconds": settings.CLIP_POST_SECONDS,
        },
        "error": None
    }
