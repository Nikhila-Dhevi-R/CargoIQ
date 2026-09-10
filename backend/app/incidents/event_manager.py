from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.database.models import Event
from app.database.repositories.incident_repo import IncidentRepository
from app.incidents.replay import generate_replay_clip
from app.core.logging import logger

class EventManager:
    def __init__(self, db: Session):
        self.db = db
        self.repo = IncidentRepository(db)
        # cooldown tracker: (object_id, behaviour) -> last_timestamp_seconds
        self.cooldowns: Dict[tuple, float] = {}
        self.COOLDOWN_SECONDS = 3.0

    def record_incident(
        self,
        video_id: int,
        source_video_path: str,
        timestamp_seconds: float,
        behaviour: str,
        behaviour_name: str,
        object_id: str,
        risk_score: int,
        risk_level: str,
        zone: str,
        evidence: List[str],
        recommendation: str,
        factors: List[Dict[str, Any]],
        duration: float = 2.0,
        frame_idx: int = 0,
        sop_rule_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Event]:
        key = (object_id, behaviour)
        last_t = self.cooldowns.get(key, -999.0)

        # Suppress duplicate rapid firing
        if (timestamp_seconds - last_t) < self.COOLDOWN_SECONDS:
            return None

        self.cooldowns[key] = timestamp_seconds

        # Format timestamp string MM:SS
        mins = int(timestamp_seconds // 60)
        secs = int(timestamp_seconds % 60)
        time_str = f"{mins:02d}:{secs:02d}"

        # Insert record into database
        event = self.repo.create(
            video_id=video_id,
            timestamp=time_str,
            timestamp_seconds=timestamp_seconds,
            behaviour=behaviour,
            behaviour_name=behaviour_name,
            object_id=object_id,
            risk_score=risk_score,
            risk_level=risk_level,
            zone=zone,
            evidence_json=evidence,
            recommendation=recommendation,
            confidence=0.88,
            severity="HIGH" if risk_score >= 55 else "MEDIUM",
            duration=duration,
            frame_start=max(0, frame_idx - 30),
            frame_end=frame_idx + 30,
            factors_json=factors,
            sop_rule_code=sop_rule_code or behaviour,
            metadata_json=metadata or {},
            review_status="UNREVIEWED"
        )

        # Generate replay clip
        try:
            clip_path = generate_replay_clip(
                source_video_path=source_video_path,
                event_id=event.id,
                timestamp_seconds=timestamp_seconds,
                duration_seconds=duration
            )
            if clip_path:
                event.clip_path = clip_path
                self.db.commit()
        except Exception as e:
            logger.error(f"Failed to generate replay clip for event #{event.id}: {e}")

        logger.info(f"Incident recorded: Event #{event.id} [{behaviour_name}] on {object_id} ({time_str}, Score: {risk_score})")
        return event

    @staticmethod
    def display_label(behaviour: str) -> str:
        """Short, operator-facing wording used consistently in video and live events."""
        return {
            "DROP_PRODUCT": "POSSIBLE DROP",
            "DRAG_PRODUCT": "DRAGGING DETECTED",
            "PALLET_OVERHANG": "PALLET OVERHANG",
            "IMPROPER_STAGING": "IMPROPER STAGING",
            "STACK_ORDER": "IMPROPER STACKING",
        }.get(behaviour, behaviour.replace("_", " "))
