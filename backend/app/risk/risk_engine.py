from typing import Dict, Any, List, Tuple

class RiskEngine:
    """
    Deterministic Risk Calculation Engine (0-100 score).
    Factors:
      - Behaviour severity: 35%
      - Motion / impact: 20%
      - Duration: 10%
      - Spatial configuration: 15%
      - Repetition: 10%
      - Location / context: 10%
    """

    SEVERITY_WEIGHTS = {
        "CRITICAL": 35,
        "HIGH": 30,
        "MEDIUM": 18,
        "LOW": 10,
        "SAFE": 0
    }

    ZONE_RISK_WEIGHTS = {
        "Loading Bay 1": 10,
        "Loading Bay 2": 9,
        "General Walkway": 9,
        "Staging Zone A": 6,
        "Staging Zone B": 7,
        "Dispatch Area": 5
    }

    @classmethod
    def calculate_risk(
        cls,
        behaviour_severity: str,
        motion_intensity: float = 0.5, # 0.0 to 1.0
        duration_s: float = 1.0,
        spatial_factor: float = 0.5,    # 0.0 to 1.0 (e.g. lack of support, lean angle)
        repetition_count: int = 1,
        zone: str = "General Walkway"
    ) -> Dict[str, Any]:
        factors = []

        # 1. Behaviour Severity (Max 35)
        sev_contrib = cls.SEVERITY_WEIGHTS.get(behaviour_severity.upper(), 18)
        factors.append({
            "name": "Behaviour severity",
            "contribution": sev_contrib,
            "description": f"Baseline severity weight for {behaviour_severity}"
        })

        # 2. Motion / Impact (Max 20)
        # Higher acceleration or velocity increases risk
        motion_contrib = int(round(min(1.0, max(0.0, motion_intensity)) * 20))
        factors.append({
            "name": "Motion impact",
            "contribution": motion_contrib,
            "description": f"Dynamic acceleration and velocity profile ({round(motion_intensity * 100)}% threshold)"
        })

        # 3. Duration (Max 10)
        dur_contrib = int(round(min(10.0, max(2.0, duration_s * 2.0))))
        factors.append({
            "name": "Duration",
            "contribution": dur_contrib,
            "description": f"Sustained violation exposure ({round(duration_s, 1)}s)"
        })

        # 4. Spatial configuration (Max 15)
        spatial_contrib = int(round(min(1.0, max(0.0, spatial_factor)) * 15))
        factors.append({
            "name": "Spatial configuration",
            "contribution": spatial_contrib,
            "description": "Base overhang, support area deficit or vertical stack stability"
        })

        # 5. Repetition (Max 10)
        rep_contrib = min(10, (repetition_count - 1) * 3 + 2)
        factors.append({
            "name": "Repetition",
            "contribution": rep_contrib,
            "description": f"Incident recurrence factor (observed {repetition_count} times)"
        })

        # 6. Location / context (Max 10)
        zone_contrib = cls.ZONE_RISK_WEIGHTS.get(zone, 6)
        factors.append({
            "name": "Location context",
            "contribution": zone_contrib,
            "description": f"Warehouse operational hazard zone ({zone})"
        })

        total_score = sum(f["contribution"] for f in factors)
        total_score = min(100, max(0, total_score))

        if total_score >= 80:
            level = "CRITICAL"
        elif total_score >= 55:
            level = "HIGH"
        elif total_score >= 30:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "score": total_score,
            "level": level,
            "factors": factors
        }
