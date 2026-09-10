from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str
    video_id: Optional[int] = None
    event_id: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    grounding_data: Optional[Dict[str, Any]] = None
    citations: List[str] = Field(default_factory=list)
    confidence: float = 0.95

class IncidentExplainRequest(BaseModel):
    event_id: int

class IncidentExplainResponse(BaseModel):
    event_id: int
    what_happened: str
    why_risky: str
    evidence: List[str]
    sop_rule: str
    sop_rule_name: str
    recommendation: str
    full_explanation: str

class ShiftSummaryRequest(BaseModel):
    video_id: Optional[int] = None

class ShiftSummaryResponse(BaseModel):
    shift_title: str
    total_events: int
    risk_events: int
    critical: int
    high: int
    medium: int
    low: int
    most_frequent_behaviour: str
    highest_risk_incident: str
    highest_risk_zone: str
    recurring_patterns: List[str]
    recommendations: List[str]
    full_summary_text: str
