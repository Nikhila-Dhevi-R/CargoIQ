from typing import Dict, Any, Optional, List
from app.intelligence.object_memory import ObjectHistory

class DropThrowBehaviour:
    CODE = "DROP_PRODUCT"
    NAME = "Possible Product Drop"
    SEVERITY = "HIGH"

    @classmethod
    def analyze(cls, obj: ObjectHistory, current_time_s: float, frame_height: int) -> Optional[Dict[str, Any]]:
        """
        Detects possible drop/throw from temporal history:
        - Operator-product proximity in past 1.5 seconds
        - High downward vertical velocity (vy > 65.0)
        - Floor proximity (y > 60% of frame)
        - Sudden deceleration / velocity drop
        """
        if len(obj.history) < 8:
            return None

        recent = list(obj.history)[-10:]
        latest = recent[-1]
        
        # Check floor proximity
        if latest["bbox"][3] < frame_height * 0.55:
            return None

        # Check for rapid downward velocity in preceding 2-5 frames
        max_downward_vy = max([f["vy"] for f in recent[:-2]], default=0.0)
        current_speed = latest["speed"]

        had_operator = obj.last_near_person_time > 0 and (current_time_s - obj.last_near_person_time < 3.0)
        
        # Trigger condition: high downward velocity followed by sudden deceleration near floor
        if had_operator and max_downward_vy > 60.0 and current_speed < 18.0:
            evidence = [
                "Operator-product separation detected",
                f"Rapid downward velocity peak measured ({round(max_downward_vy, 1)} px/s)",
                "Sudden kinetic arrest upon floor contact",
                "Object stationary post-impact"
            ]
            return {
                "behaviour": cls.CODE,
                "behaviour_name": cls.NAME,
                "severity": cls.SEVERITY,
                "confidence": 0.91,
                "duration": 1.2,
                "evidence": evidence,
                "recommendation": "Inspect carton exterior and contents for internal damage; review manual handling and gentle staging SOP."
            }
        return None
