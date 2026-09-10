import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.repositories.incident_repo import IncidentRepository
from app.schemas.incident import IncidentReviewRequest
from app.core.config import CLIPS_DIR
from app.incidents.event_manager import EventManager

router = APIRouter(prefix="/events", tags=["Incidents & Events"])

def parse_json_safely(val, default):
    if not val:
        return default
    try:
        return json.loads(val)
    except Exception:
        return default

@router.get("")
def list_events(
    video_id: Optional[int] = None,
    risk_level: Optional[str] = None,
    behaviour: Optional[str] = None,
    zone: Optional[str] = None,
    review_status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    repo = IncidentRepository(db)
    events = repo.get_all(
        video_id=video_id,
        risk_level=risk_level,
        behaviour=behaviour,
        zone=zone,
        review_status=review_status,
        limit=limit
    )

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
                "evidence": parse_json_safely(e.evidence_json, []),
                "recommendation": e.recommendation,
                "clip_path": e.clip_path,
                "review_status": e.review_status,
                "review_notes": e.review_notes,
                "confidence": e.confidence,
                "severity": e.severity,
                "duration": e.duration,
                "factors": parse_json_safely(e.factors_json, []),
                "sop_rule_code": e.sop_rule_code,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "metadata": parse_json_safely(e.metadata_json, {}),
                "display_label": EventManager.display_label(e.behaviour)
            }
            for e in events
        ],
        "error": None
    }

@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    repo = IncidentRepository(db)
    e = repo.get_by_id(event_id)
    if not e:
        raise HTTPException(status_code=404, detail=f"Incident #{event_id} not found.")

    return {
        "success": True,
        "data": {
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
            "evidence": parse_json_safely(e.evidence_json, []),
            "recommendation": e.recommendation,
            "clip_path": e.clip_path,
            "review_status": e.review_status,
            "review_notes": e.review_notes,
            "confidence": e.confidence,
            "severity": e.severity,
            "duration": e.duration,
            "factors": parse_json_safely(e.factors_json, []),
            "sop_rule_code": e.sop_rule_code,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "metadata": parse_json_safely(e.metadata_json, {}),
            "display_label": EventManager.display_label(e.behaviour)
        },
        "error": None
    }

@router.get("/{event_id}/replay")
def get_event_replay(event_id: int, db: Session = Depends(get_db)):
    repo = IncidentRepository(db)
    e = repo.get_by_id(event_id)
    if not e:
        raise HTTPException(status_code=404, detail="Incident not found.")

    clip_file = e.clip_path
    if not clip_file or not Path(clip_file).exists():
        # Look in CLIPS_DIR
        default_clip = CLIPS_DIR / f"replay_event_{event_id}.mp4"
        if default_clip.exists():
            clip_file = str(default_clip)
        else:
            raise HTTPException(status_code=404, detail="Replay clip not yet generated or available.")

    return FileResponse(clip_file, media_type="video/mp4", filename=f"replay_incident_{event_id}.mp4")

@router.patch("/{event_id}/review")
def review_event(event_id: int, req: IncidentReviewRequest, db: Session = Depends(get_db)):
    repo = IncidentRepository(db)
    status_clean = req.status.upper()
    if status_clean not in ["REVIEWED", "DISMISSED", "UNREVIEWED"]:
        raise HTTPException(status_code=400, detail="Status must be REVIEWED, DISMISSED, or UNREVIEWED.")

    updated = repo.update_review(event_id, status_clean, req.notes)
    if not updated:
        raise HTTPException(status_code=404, detail="Incident not found.")

    return {
        "success": True,
        "data": {
            "id": updated.id,
            "review_status": updated.review_status,
            "review_notes": updated.review_notes
        },
        "error": None
    }
