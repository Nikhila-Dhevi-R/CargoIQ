import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.models import Event

class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Event:
        if isinstance(kwargs.get("evidence_json"), list):
            kwargs["evidence_json"] = json.dumps(kwargs["evidence_json"])
        if isinstance(kwargs.get("factors_json"), list):
            kwargs["factors_json"] = json.dumps(kwargs["factors_json"])
        if isinstance(kwargs.get("metadata_json"), dict):
            kwargs["metadata_json"] = json.dumps(kwargs["metadata_json"])

        event = Event(**kwargs)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_by_id(self, event_id: int) -> Optional[Event]:
        return self.db.query(Event).filter(Event.id == event_id).first()

    def get_by_video(self, video_id: int) -> List[Event]:
        return self.db.query(Event).filter(Event.video_id == video_id).order_by(Event.timestamp_seconds.asc()).all()

    def get_all(
        self,
        video_id: Optional[int] = None,
        risk_level: Optional[str] = None,
        behaviour: Optional[str] = None,
        zone: Optional[str] = None,
        review_status: Optional[str] = None,
        limit: int = 100
    ) -> List[Event]:
        query = self.db.query(Event)
        if video_id:
            query = query.filter(Event.video_id == video_id)
        if risk_level:
            query = query.filter(Event.risk_level == risk_level.upper())
        if behaviour:
            query = query.filter(Event.behaviour == behaviour.upper())
        if zone:
            query = query.filter(Event.zone == zone)
        if review_status:
            query = query.filter(Event.review_status == review_status.upper())
        return query.order_by(desc(Event.created_at)).limit(limit).all()

    def update_review(self, event_id: int, status: str, notes: Optional[str] = None) -> Optional[Event]:
        event = self.get_by_id(event_id)
        if event:
            event.review_status = status.upper()
            if notes is not None:
                event.review_notes = notes
            self.db.commit()
            self.db.refresh(event)
        return event

    def get_risk_counts(self) -> Dict[str, int]:
        events = self.db.query(Event.risk_level).all()
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "SAFE": 0}
        for (lvl,) in events:
            if lvl in counts:
                counts[lvl] += 1
        return counts
