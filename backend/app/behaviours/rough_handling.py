from typing import Dict, Any, Optional, List
from app.intelligence.object_memory import ObjectHistory

class RoughHandlingBehaviour:
    CODE = "ROUGH_HANDLING"
    NAME = "Rough Handling / Excessive Impact"
    SEVERITY = "HIGH"

    @classmethod
    def analyze(cls, obj: ObjectHistory) -> Optional[Dict[str, Any]]:
        """
        Detects sudden aggressive acceleration or violent push/impact.
        """
        if len(obj.history) < 6:
            return None

        recent = list(obj.history)[-6:]
        speeds = [f["speed"] for f in recent]
        
        # Calculate jerk (change in acceleration/speed over short interval)
        max_speed = max(speeds)
        min_speed = min(speeds)
        delta_speed = max_speed - min_speed

        if delta_speed > 90.0 and max_speed > 100.0:
            evidence = [
                f"Abrupt velocity impulse detected (Δv={round(delta_speed, 1)} px/s)",
                "Excessive manual kinetic transfer to product",
                "High risk of package corner crushing or internal component shock"
            ]
            return {
                "behaviour": cls.CODE,
                "behaviour_name": cls.NAME,
                "severity": cls.SEVERITY,
                "confidence": 0.85,
                "duration": 1.0,
                "evidence": evidence,
                "recommendation": "Inspect affected carton for shock damage and coach handling team on gentle placement procedures."
            }
        return None
