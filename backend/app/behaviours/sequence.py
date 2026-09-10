from typing import Dict, Any, Optional, List

class SequenceBehaviour:
    CODE = "UNSAFE_SEQUENCE"
    NAME = "Unsafe Loading Sequence"
    SEVERITY = "HIGH"

    @classmethod
    def analyze(cls, elevated_box: List[float], perimeter_supported: bool) -> Optional[Dict[str, Any]]:
        """
        Detects upper tier staged without perimeter support underneath.
        """
        if not perimeter_supported:
            evidence = [
                "Elevated placement attempted without foundational perimeter interlocking",
                "Reverse sequence stacking violates warehouse safety protocol",
                "Hazardous overhang exposed to forklift corridor"
            ]
            return {
                "behaviour": cls.CODE,
                "behaviour_name": cls.NAME,
                "severity": cls.SEVERITY,
                "confidence": 0.88,
                "duration": 2.5,
                "evidence": evidence,
                "recommendation": "Enforce bottom-up, back-to-front loading sequence before placing elevated tier units."
            }
        return None
