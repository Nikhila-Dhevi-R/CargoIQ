from typing import Dict, Any, Optional, List
from app.intelligence.geometry import calculate_support_ratio

class PalletOverhangBehaviour:
    CODE = "PALLET_OVERHANG"
    NAME = "Pallet Overhang"
    SEVERITY = "HIGH"

    @classmethod
    def analyze(cls, carton_box: List[float], pallet_box: List[float], threshold: float = 0.90) -> Optional[Dict[str, Any]]:
        """
        Analyzes carton support ratio against underlying pallet.
        """
        support = calculate_support_ratio(carton_box, pallet_box)
        # Only triggers if carton is on or near pallet (support > 0.1) but below threshold
        if 0.10 <= support < threshold:
            support_pct = int(round(support * 100))
            evidence = [
                f"Base support ratio calculated at {support_pct}% (below safe minimum 90%)",
                "Carton overhangs pallet perimeter boundary",
                "Asymmetrical gravitational load induces tilt and corner crush risk"
            ]
            return {
                "behaviour": cls.CODE,
                "behaviour_name": cls.NAME,
                "severity": cls.SEVERITY,
                "confidence": 0.93,
                "duration": 2.0,
                "support_ratio": support,
                "evidence": evidence,
                "recommendation": "Reposition carton flush with pallet boundary to prevent edge crush during forklift transit."
            }
        return None
