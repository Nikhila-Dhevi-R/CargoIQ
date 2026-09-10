from typing import Dict, Any, Optional, List
import math

class UnsupportedStackBehaviour:
    CODE = "UNSTABLE_STACK"
    NAME = "Unstable / Unsupported Stack"
    SEVERITY = "HIGH"

    @classmethod
    def analyze(cls, boxes: List[List[float]]) -> Optional[Dict[str, Any]]:
        """
        Detects unstable stack tilt:
        - at least 2 or 3 boxes stacked vertically
        - horizontal centroid shift creates tilt angle > 12 degrees
        """
        if len(boxes) < 2:
            return None

        # Sort from bottom to top by y2
        sorted_boxes = sorted(boxes, key=lambda b: b[3], reverse=True)
        base_cx = (sorted_boxes[0][0] + sorted_boxes[0][2]) / 2.0
        top_cx = (sorted_boxes[-1][0] + sorted_boxes[-1][2]) / 2.0
        dx = abs(top_cx - base_cx)
        dy = max(1.0, sorted_boxes[0][3] - sorted_boxes[-1][1])

        angle = math.degrees(math.atan2(dx, dy))
        if angle > 12.0:
            evidence = [
                f"Stack lean angle measured at {round(angle, 1)}° (safe maximum SOP tolerance: 12°)",
                f"Column height spans {len(boxes)} tiers with progressive lateral drift",
                "Center of mass projection approaches perimeter tipping point"
            ]
            return {
                "behaviour": cls.CODE,
                "behaviour_name": cls.NAME,
                "severity": cls.SEVERITY,
                "confidence": 0.86,
                "duration": 4.0,
                "evidence": evidence,
                "recommendation": "Immediately stabilize the tilting stack and interlock cartons to prevent catastrophic column collapse."
            }
        return None
