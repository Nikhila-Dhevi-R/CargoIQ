import uuid
import asyncio
import json
from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db, SessionLocal
from app.database.repositories.video_repo import VideoRepository
from app.database.repositories.incident_repo import IncidentRepository
from app.ingestion.upload import save_uploaded_video
from app.ingestion.url_loader import download_video_from_url
from app.ingestion.metadata import extract_video_metadata
from app.ingestion.frame_extractor import generate_thumbnail
from app.services.analysis_service import VideoAnalysisService
from app.incidents.event_manager import EventManager

router = APIRouter(prefix="/videos", tags=["Videos"])

def run_async_analysis(video_id: int, job_id: str):
    db = SessionLocal()
    try:
        service = VideoAnalysisService(db)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(service.run_analysis(video_id, job_id))
        loop.close()
    finally:
        db.close()

@router.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    auto_analyse: bool = Form(False),
    db: Session = Depends(get_db)
):
    saved_path, filename = save_uploaded_video(file)
    meta = extract_video_metadata(saved_path)
    thumb_path = generate_thumbnail(saved_path, f"thumb_{Path(filename).stem}")

    repo = VideoRepository(db)
    video = repo.create(
        filename=filename,
        original_name=file.filename,
        file_path=saved_path,
        thumbnail_path=thumb_path,
        duration=meta["duration"],
        fps=meta["fps"],
        width=meta["width"],
        height=meta["height"],
        frame_count=meta["frame_count"],
        source_type="upload",
        status="ready"
    )

    job_id = None
    if auto_analyse:
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        repo.create_job(job_id=job_id, video_id=video.id, total_frames=video.frame_count)
        repo.update_status(video.id, status="processing")
        background_tasks.add_task(run_async_analysis, video.id, job_id)

    return {
        "success": True,
        "data": {
            "video_id": video.id,
            "filename": video.filename,
            "original_name": video.original_name,
            "duration": video.duration,
            "fps": video.fps,
            "width": video.width,
            "height": video.height,
            "thumbnail_path": video.thumbnail_path,
            "job_id": job_id
        },
        "error": None
    }

@router.post("/url")
async def upload_video_url(
    payload: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing required 'url' parameter.")

    saved_path, filename = await download_video_from_url(url)
    meta = extract_video_metadata(saved_path)
    thumb_path = generate_thumbnail(saved_path, f"thumb_{Path(filename).stem}")

    repo = VideoRepository(db)
    video = repo.create(
        filename=filename,
        original_name=url.split("/")[-1].split("?")[0] or "web_video.mp4",
        file_path=saved_path,
        thumbnail_path=thumb_path,
        duration=meta["duration"],
        fps=meta["fps"],
        width=meta["width"],
        height=meta["height"],
        frame_count=meta["frame_count"],
        source_type="url",
        source_url=url,
        status="ready"
    )

    auto_analyse = payload.get("auto_analyse", False)
    job_id = None
    if auto_analyse:
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        repo.create_job(job_id=job_id, video_id=video.id, total_frames=video.frame_count)
        repo.update_status(video.id, status="processing")
        background_tasks.add_task(run_async_analysis, video.id, job_id)

    return {
        "success": True,
        "data": {
            "video_id": video.id,
            "filename": video.filename,
            "duration": video.duration,
            "thumbnail_path": video.thumbnail_path,
            "job_id": job_id
        },
        "error": None
    }

@router.post("/{video_id}/analyse")
async def start_analysis(
    video_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    repo = VideoRepository(db)
    video = repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video #{video_id} not found.")

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    repo.create_job(job_id=job_id, video_id=video.id, total_frames=video.frame_count)
    repo.update_status(video_id, status="processing")
    background_tasks.add_task(run_async_analysis, video.id, job_id)

    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "video_id": video_id,
            "status": "queued",
            "total_frames": video.frame_count
        },
        "error": None
    }

@router.get("")
def list_videos(limit: int = 50, db: Session = Depends(get_db)):
    repo = VideoRepository(db)
    videos = repo.get_all(limit=limit)
    return {
        "success": True,
        "data": [
            {
                "id": v.id,
                "filename": v.filename,
                "original_name": v.original_name,
                "duration": v.duration,
                "fps": v.fps,
                "width": v.width,
                "height": v.height,
                "status": v.status,
                "file_path": v.file_path,
                "processed_path": v.processed_path,
                "thumbnail_path": v.thumbnail_path,
                "created_at": v.created_at.isoformat() if v.created_at else None
            }
            for v in videos
        ],
        "error": None
    }

@router.get("/{video_id}")
def get_video(video_id: int, db: Session = Depends(get_db)):
    repo = VideoRepository(db)
    v = repo.get_by_id(video_id)
    if not v:
        raise HTTPException(status_code=404, detail="Video not found.")
    return {
        "success": True,
        "data": {
            "id": v.id,
            "filename": v.filename,
            "original_name": v.original_name,
            "duration": v.duration,
            "fps": v.fps,
            "width": v.width,
            "height": v.height,
            "status": v.status,
            "file_path": v.file_path,
            "processed_path": v.processed_path,
            "thumbnail_path": v.thumbnail_path,
            "created_at": v.created_at.isoformat() if v.created_at else None
        },
        "error": None
    }

@router.get("/{video_id}/status")
def get_video_status(video_id: int, db: Session = Depends(get_db)):
    repo = VideoRepository(db)
    v = repo.get_by_id(video_id)
    if not v:
        raise HTTPException(status_code=404, detail="Video not found.")

    # Relationships are not guaranteed to be ordered.  Fetch the job explicitly
    # so a dashboard reconnects to the analysis currently in progress.
    latest_job = max(v.analysis_jobs, key=lambda job: job.created_at) if v.analysis_jobs else None
    
    return {
        "success": True,
        "data": {
            "video_id": v.id,
            "status": v.status,
            "latest_job": {
                "job_id": latest_job.id,
                "status": latest_job.status,
                "progress": latest_job.progress,
                "current_frame": latest_job.current_frame,
                "total_frames": latest_job.total_frames,
                "step_description": latest_job.step_description,
                "error_message": latest_job.error_message,
            } if latest_job else None
        },
        "error": None
    }

@router.get("/{video_id}/events")
def get_video_events(video_id: int, db: Session = Depends(get_db)):
    repo = IncidentRepository(db)
    events = repo.get_by_video(video_id)
    return {
        "success": True,
        "data": [
            {
                "id": e.id,
                "video_id": e.video_id,
                "timestamp": e.timestamp,
                "timestamp_seconds": e.timestamp_seconds,
                "behaviour": e.behaviour,
                "behaviour_name": e.behaviour_name,
                "object_id": e.object_id,
                "risk_score": e.risk_score,
                "risk_level": e.risk_level,
                "zone": e.zone,
                "evidence": json.loads(e.evidence_json) if isinstance(e.evidence_json, str) and e.evidence_json.startswith("[") else [],
                "recommendation": e.recommendation,
                "clip_path": e.clip_path,
                "review_status": e.review_status,
                "review_notes": e.review_notes,
                "severity": e.severity,
                "duration": e.duration,
                "factors": json.loads(e.factors_json) if isinstance(e.factors_json, str) and e.factors_json.startswith("[") else [],
                "metadata": json.loads(e.metadata_json) if isinstance(e.metadata_json, str) and e.metadata_json.startswith("{") else {},
                "display_label": EventManager.display_label(e.behaviour),
                "confidence": e.confidence,
                "created_at": e.created_at.isoformat() if e.created_at else None
            }
            for e in events
        ],
        "error": None
    }
