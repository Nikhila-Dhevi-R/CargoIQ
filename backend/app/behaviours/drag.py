from typing import Dict, Any, Optional, List
from app.intelligence.object_memory import ObjectHistory

class DragBehaviour:
    CODE = "DRAG_PRODUCT"
    NAME = "Dragging Product"
    SEVERITY = "MEDIUM"

    @classmethod
    def analyze(cls, obj: ObjectHistory, current_time_s: float, frame_height: int) -> Optional[Dict[str, Any]]:
        """
        Detects product dragged across floor:
        - Near floor
        - Sustained horizontal velocity for > 1.0s
        - Operator present/pulling
        """
        if len(obj.history) < 15:
            return None

        recent = list(obj.history)[-15:]
        latest = recent[-1]

        # Check floor contact
        if latest["bbox"][3] < frame_height * 0.60:
            return None

        # Check sustained horizontal motion
        avg_vx = sum([abs(f["vx"]) for f in recent]) / len(recent)
        avg_vy = sum([abs(f["vy"]) for f in recent]) / len(recent)

        # Operator present
        operator_present = obj.last_near_person_time > 0 and (current_time_s - obj.last_near_person_time < 2.0)

        if operator_present and avg_vx > 25.0 and avg_vy < 18.0:
            evidence = [
                "Object bottom maintained continuous floor contact",
                f"Sustained horizontal friction drag ({round(avg_vx, 1)} px/s lateral motion)",
                "Lack of mobile material handling equipment (trolley / pallet jack)",
                "Manual operator pulling action identified"
            ]
            return {
                "behaviour": cls.CODE,
                "behaviour_name": cls.NAME,
                "severity": cls.SEVERITY,
                "confidence": 0.88,
                "duration": 2.4,
                "evidence": evidence,
                "recommendation": "Use suitable trolley or hand pallet truck instead of manually dragging cartons to prevent base rupture."
            }
        return None
