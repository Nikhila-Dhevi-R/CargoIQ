from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import Feedback, Event

class FeedbackRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, event_id: int, feedback_type: str, comment: Optional[str] = None, user_id: str = "Supervisor") -> Feedback:
        feedback = Feedback(
            event_id=event_id,
            feedback_type=feedback_type.lower(),
            comment=comment,
            user_id=user_id
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def get_all(self, limit: int = 100) -> List[Feedback]:
        return self.db.query(Feedback).order_by(Feedback.created_at.desc()).limit(limit).all()

    def get_summary(self) -> Dict[str, Any]:
        total = self.db.query(func.count(Feedback.id)).scalar() or 0
        correct = self.db.query(func.count(Feedback.id)).filter(Feedback.feedback_type == "correct").scalar() or 0
        incorrect = self.db.query(func.count(Feedback.id)).filter(Feedback.feedback_type == "incorrect").scalar() or 0
        unsure = self.db.query(func.count(Feedback.id)).filter(Feedback.feedback_type == "unsure").scalar() or 0
        
        accuracy_rate = round((correct / total * 100), 1) if total > 0 else 100.0

        # Most disputed behaviours (where feedback_type == 'incorrect')
        disputed = self.db.query(
            Event.behaviour_name,
            func.count(Feedback.id).label("dispute_count")
        ).join(Feedback, Feedback.event_id == Event.id)\
         .filter(Feedback.feedback_type == "incorrect")\
         .group_by(Event.behaviour_name)\
         .order_by(func.count(Feedback.id).desc())\
         .limit(5).all()

        return {
            "total_feedback": total,
            "correct_count": correct,
            "incorrect_count": incorrect, # False positives
            "unsure_count": unsure,
            "accuracy_rate": accuracy_rate,
            "most_disputed": [{"behaviour": d[0], "count": d[1]} for d in disputed]
        }
