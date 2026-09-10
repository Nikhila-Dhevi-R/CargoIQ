from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class FeedbackCreate(BaseModel):
    event_id: int
    feedback_type: str = Field(..., description="correct, incorrect, or unsure")
    comment: Optional[str] = None
    user_id: Optional[str] = "Supervisor"

class FeedbackResponse(BaseModel):
    id: int
    event_id: int
    feedback_type: str
    comment: Optional[str] = None
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackSummaryResponse(BaseModel):
    total_feedback: int
    correct_count: int
    incorrect_count: int
    unsure_count: int
    accuracy_rate: float
    most_disputed: List[Dict[str, Any]]
