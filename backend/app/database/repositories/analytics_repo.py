from typing import Dict, Any, List
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import Event, Video, Feedback

class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> Dict[str, Any]:
        total_videos = self.db.query(func.count(Video.id)).scalar() or 0
        total_events = self.db.query(func.count(Event.id)).scalar() or 0
        
        risk_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "SAFE": 0}
        levels = self.db.query(Event.risk_level, func.count(Event.id)).group_by(Event.risk_level).all()
        for lvl, cnt in levels:
            if lvl in risk_counts:
                risk_counts[lvl] = cnt
        
        # Risk events = Medium + High + Critical
        risk_events = risk_counts["MEDIUM"] + risk_counts["HIGH"] + risk_counts["CRITICAL"]
        # Potentially preventable = incidents flagged with high or critical or improper handling
        preventable = risk_counts["CRITICAL"] + risk_counts["HIGH"]
        
        # Reviewed count
        reviewed_count = self.db.query(func.count(Event.id)).filter(Event.review_status == "REVIEWED").scalar() or 0
        
        return {
            "total_videos_analysed": total_videos,
            "total_handling_events": total_events,
            "risk_events": risk_events,
            "critical_events": risk_counts["CRITICAL"],
            "high_risk_events": risk_counts["HIGH"],
            "medium_risk_events": risk_counts["MEDIUM"],
            "low_risk_events": risk_counts["LOW"],
            "potentially_preventable_incidents": preventable,
            "reviewed_count": reviewed_count
        }

    def get_behaviour_distribution(self) -> List[Dict[str, Any]]:
        results = self.db.query(
            Event.behaviour_name,
            func.count(Event.id).label("count"),
            func.avg(Event.risk_score).label("avg_risk")
        ).group_by(Event.behaviour_name).order_by(func.count(Event.id).desc()).all()
        
        return [
            {
                "behaviour": r[0] or "Unknown",
                "count": int(r[1]),
                "avg_risk": round(float(r[2] or 0), 1)
            }
            for r in results
        ]

    def get_zone_distribution(self) -> List[Dict[str, Any]]:
        results = self.db.query(
            Event.zone,
            func.count(Event.id).label("count"),
            func.avg(Event.risk_score).label("avg_risk")
        ).group_by(Event.zone).order_by(func.count(Event.id).desc()).all()
        
        return [
            {
                "zone": r[0] or "General",
                "count": int(r[1]),
                "avg_risk": round(float(r[2] or 0), 1)
            }
            for r in results
        ]

    def get_risk_trends(self) -> List[Dict[str, Any]]:
        # Order by video / created_at
        events = self.db.query(
            Event.timestamp,
            Event.risk_score,
            Event.risk_level,
            Event.behaviour_name
        ).order_by(Event.id.asc()).limit(30).all()
        
        return [
            {
                "time": e[0],
                "score": e[1],
                "level": e[2],
                "behaviour": e[3]
            }
            for e in events
        ]
