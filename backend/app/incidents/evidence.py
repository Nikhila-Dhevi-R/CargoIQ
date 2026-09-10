from typing import List, Dict, Any

class EvidenceBuilder:
    @staticmethod
    def build_evidence(
        behaviour: str,
        specific_evidence: List[str],
        zone: str,
        risk_score: int,
        track_label: str
    ) -> List[str]:
        curated = list(specific_evidence)
        curated.append(f"Recorded in designated warehouse area: {zone}")
        curated.append(f"Deterministic algorithmic risk score: {risk_score}/100")
        return curated
