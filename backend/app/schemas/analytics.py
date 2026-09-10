from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class OverviewKPIs(BaseModel):
    total_videos_analysed: int
    total_handling_events: int
    risk_events: int
    critical_events: int
    high_risk_events: int
    medium_risk_events: int
    low_risk_events: int
    potentially_preventable_incidents: int
    reviewed_count: int

class BehaviourStat(BaseModel):
    behaviour: str
    count: int
    avg_risk: float

class ZoneStat(BaseModel):
    zone: str
    count: int
    avg_risk: float

class TrendItem(BaseModel):
    time: str
    score: int
    level: str
    behaviour: str

class AnalyticsOverviewResponse(BaseModel):
    kpis: OverviewKPIs
    behaviours: List[BehaviourStat]
    zones: List[ZoneStat]
    trends: List[TrendItem]
