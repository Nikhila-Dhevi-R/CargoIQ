from typing import Dict, Any, Optional, List
from app.intelligence.geometry import calculate_iou

class StackingBehaviour:
    CODE = "STACK_ORDER"
    NAME = "Incorrect Stack Order"
    SEVERITY = "MEDIUM"

    @classmethod
    def analyze(cls, top_box: List[float], bottom_box: List[float]) -> Optional[Dict[str, Any]]:
        """
        Detects top box significantly larger than bottom box:
        - top box sits on bottom box (top_box[3] approx bottom_box[1])
        - top width / bottom width > 1.2
        """
        top_w = top_box[2] - top_box[0]
        bottom_w = bottom_box[2] - bottom_box[0]
        
        # Check if vertically adjacent
        is_above = abs(top_box[3] - bottom_box[1]) < 30.0 and top_box[1] < bottom_box[1]
        horizontal_overlap = max(0.0, min(top_box[2], bottom_box[2]) - max(top_box[0], bottom_box[0]))

        if is_above and horizontal_overlap > 20.0:
            if top_w > bottom_w * 1.25:
                ratio_pct = int(round((top_w / bottom_w) * 100))
                evidence = [
                    f"Top unit horizontal footprint exceeds base support unit by {ratio_pct - 100}%",
                    "Inverse pyramid weight distribution detected in vertical column",
                    "Base carton subjected to excessive compressive load"
                ]
                return {
                    "behaviour": cls.CODE,
                    "behaviour_name": cls.NAME,
                    "severity": cls.SEVERITY,
                    "confidence": 0.87,
                    "duration": 3.0,
                    "evidence": evidence,
                    "recommendation": "Restack column with broader, heavier cartons at the bottom layer and lighter items on upper tiers."
                }
        return None
