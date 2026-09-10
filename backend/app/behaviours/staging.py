from typing import Dict, Any, Optional, List
from app.intelligence.geometry import centroid

class ImproperStagingBehaviour:
    CODE = "IMPROPER_STAGING"
    NAME = "Improper Staging"
    SEVERITY = "MEDIUM"

    @classmethod
    def analyze(cls, carton_box: List[float], current_zone: str, expected_zone: str = "Staging Zone A") -> Optional[Dict[str, Any]]:
        """
        Detects product staged in unauthorized area or transit walkway.
        """
        # If placed in general walkway or outside assigned staging
        if "Walkway" in current_zone or (current_zone not in ["Staging Zone A", "Staging Zone B", "Loading Bay 1", "Loading Bay 2", "Dispatch Area"]):
            evidence = [
                f"Product placed in unauthorized zone: '{current_zone}'",
                f"Expected designated staging area: '{expected_zone}'",
                "Obstruction detected in active forklift/personnel corridor",
                "Violation of warehouse line demarcation"
            ]
            return {
                "behaviour": cls.CODE,
                "behaviour_name": cls.NAME,
                "severity": cls.SEVERITY,
                "confidence": 0.89,
                "duration": 5.0,
                "evidence": evidence,
                "recommendation": f"Transfer carton to designated staging location ({expected_zone}) immediately to clear transit pathways."
            }
        return None
