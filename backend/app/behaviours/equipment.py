from typing import Dict, Any, Optional, List

class EquipmentBehaviour:
    CODE = "INCORRECT_EQUIPMENT"
    NAME = "Incorrect Handling Equipment / Manual Handling"
    SEVERITY = "MEDIUM"

    @classmethod
    def analyze(cls, box: List[float], operator_count: int, equipment_detected: bool) -> Optional[Dict[str, Any]]:
        """
        Detects oversized/heavy profile carton handled by single operator without mechanical equipment.
        """
        w = box[2] - box[0]
        h = box[3] - box[1]
        area = w * h

        # Large profile carton (> 35000 px area) handled alone without equipment
        if area > 35000 and operator_count == 1 and not equipment_detected:
            evidence = [
                f"Bulky carton footprint ({int(w)}x{int(h)} px) handled manually by solo operator",
                "Absence of mechanical handling aid (hydraulic hand truck, trolley, or scissor lift)",
                "High ergonomic strain and acute drop/puncture risk"
            ]
            return {
                "behaviour": cls.CODE,
                "behaviour_name": cls.NAME,
                "severity": cls.SEVERITY,
                "confidence": 0.86,
                "duration": 3.0,
                "evidence": evidence,
                "recommendation": "Deploy mobile hand trolley or require team-lift procedure for heavy bulky loads."
            }
        return None
