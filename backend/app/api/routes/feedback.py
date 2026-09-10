from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories.feedback_repo import FeedbackRepository
from app.schemas.feedback import FeedbackCreate

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("")
def submit_feedback(req: FeedbackCreate, db: Session = Depends(get_db)):
    if req.feedback_type.lower() not in ["correct", "incorrect", "unsure"]:
        raise HTTPException(status_code=400, detail="Feedback type must be 'correct', 'incorrect', or 'unsure'.")

    repo = FeedbackRepository(db)
    fb = repo.create(
        event_id=req.event_id,
        feedback_type=req.feedback_type,
        comment=req.comment,
        user_id=req.user_id or "Supervisor"
    )
    return {
        "success": True,
        "data": {
            "id": fb.id,
            "event_id": fb.event_id,
            "feedback_type": fb.feedback_type,
            "comment": fb.comment,
            "created_at": fb.created_at.isoformat() if fb.created_at else None
        },
        "error": None
    }

@router.get("/summary")
def get_feedback_summary(db: Session = Depends(get_db)):
    repo = FeedbackRepository(db)
    summary = repo.get_summary()
    return {
        "success": True,
        "data": summary,
        "error": None
    }

@router.get("")
def list_feedback(limit: int = 50, db: Session = Depends(get_db)):
    repo = FeedbackRepository(db)
    items = repo.get_all(limit=limit)
    return {
        "success": True,
        "data": [
            {
                "id": f.id,
                "event_id": f.event_id,
                "feedback_type": f.feedback_type,
                "comment": f.comment,
                "user_id": f.user_id,
                "created_at": f.created_at.isoformat() if f.created_at else None
            }
            for f in items
        ],
        "error": None
    }
