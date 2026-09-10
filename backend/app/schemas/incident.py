from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class FactorBreakdown(BaseModel):
    name: str
    contribution: int
    description: Optional[str] = None

class IncidentBase(BaseModel):
    video_id: int
    timestamp: str
    timestamp_seconds: float
    behaviour: str
    behaviour_name: str
    object_id: str
    risk_score: int
    risk_level: str
    zone: str
    evidence: List[str]
    recommendation: str
    sop_rule_code: Optional[str] = None
    confidence: float = 0.85
    severity: str = "HIGH"
    duration: float = 1.0

class IncidentResponse(BaseModel):
    id: int
    video_id: int
    timestamp: str
    timestamp_seconds: float
    behaviour: str
    behaviour_name: str
    object_id: str
    risk_score: int
    risk_level: str
    zone: str
    evidence: List[str]
    recommendation: str
    clip_path: Optional[str] = None
    review_status: str
    review_notes: Optional[str] = None
    confidence: float
    severity: str
    duration: float
    factors: List[FactorBreakdown]
    sop_rule_code: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class IncidentReviewRequest(BaseModel):
    status: str = Field(..., description="REVIEWED or DISMISSED")
    notes: Optional[str] = None
