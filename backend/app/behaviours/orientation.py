from typing import Dict, Any, Optional, List

class OrientationBehaviour:
    CODE = "WRONG_ORIENTATION"
    NAME = "Wrong Product Orientation"
    SEVERITY = "LOW"

    @classmethod
    def analyze(cls, box: List[float], expected_orientation: str = "horizontal") -> Optional[Dict[str, Any]]:
        """
        Detects carton staged with wrong orientation (e.g. on edge instead of flat).
        """
        w = box[2] - box[0]
        h = box[3] - box[1]
        aspect_ratio = w / max(1.0, h)

        if expected_orientation == "horizontal" and aspect_ratio < 0.65:
            evidence = [
                f"Carton aspect ratio ({round(aspect_ratio, 2)}) indicates vertical placement on edge",
                "Violates 'This Side Up' packaging orientation protocol",
                "Risk of internal mechanical displacement"
            ]
            return {
                "behaviour": cls.CODE,
                "behaviour_name": cls.NAME,
                "severity": cls.SEVERITY,
                "confidence": 0.82,
                "duration": 2.0,
                "evidence": evidence,
                "recommendation": "Rotate carton to standard flat orientation according to exterior arrow markers."
            }
        return None
