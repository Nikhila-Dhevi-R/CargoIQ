import json
from typing import Optional, List, Dict, Any
from app.database.database import SessionLocal
from app.database.models import Event, SopRule, Video
from app.database.repositories.incident_repo import IncidentRepository
from app.database.repositories.analytics_repo import AnalyticsRepository
from app.database.repositories.sop_repo import SopRepository
from app.sop.rule_loader import RuleLoader

class CargoIQMcpServer:
    """
    CargoIQ FastMCP structured operational tool layer.
    Provides strictly read-only, audited query tools for the grounded AI assistant.
    """
    def __init__(self):
        self.db_factory = SessionLocal

    def get_incident(self, event_id: int) -> Dict[str, Any]:
        """Retrieves full details for a specific incident by its event ID."""
        with self.db_factory() as db:
            repo = IncidentRepository(db)
            event = repo.get_by_id(event_id)
            if not event:
                return {"error": f"Event #{event_id} not found."}
            return {
                "id": event.id,
                "video_id": event.video_id,
                "timestamp": event.timestamp,
                "behaviour": event.behaviour,
                "behaviour_name": event.behaviour_name,
                "object_id": event.object_id,
                "risk_score": event.risk_score,
                "risk_level": event.risk_level,
                "zone": event.zone,
                "evidence": json.loads(event.evidence_json or "[]"),
                "recommendation": event.recommendation,
                "review_status": event.review_status,
                "factors": json.loads(event.factors_json or "[]")
            }

    def search_incidents(
        self,
        behaviour: Optional[str] = None,
        risk_level: Optional[str] = None,
        zone: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Filters incidents by behaviour name, risk level (CRITICAL, HIGH, MEDIUM, LOW), or warehouse zone."""
        with self.db_factory() as db:
            repo = IncidentRepository(db)
            events = repo.get_all(risk_level=risk_level, behaviour=behaviour, zone=zone, limit=limit)
            return [
                {
                    "id": e.id,
                    "timestamp": e.timestamp,
                    "behaviour": e.behaviour_name,
                    "object_id": e.object_id,
                    "risk_score": e.risk_score,
                    "risk_level": e.risk_level,
                    "zone": e.zone,
                    "review_status": e.review_status
                }
                for e in events
            ]

    def get_risk_summary(self) -> Dict[str, Any]:
        """Returns overall KPI metrics and risk counts."""
        with self.db_factory() as db:
            repo = AnalyticsRepository(db)
            return repo.get_overview()

    def get_behaviour_statistics(self) -> List[Dict[str, Any]]:
        """Returns distribution and frequency of detected handling behaviours."""
        with self.db_factory() as db:
            repo = AnalyticsRepository(db)
            return repo.get_behaviour_distribution()

    def get_zone_statistics(self) -> List[Dict[str, Any]]:
        """Returns risk distribution and incident volume broken down by warehouse zone."""
        with self.db_factory() as db:
            repo = AnalyticsRepository(db)
            return repo.get_zone_distribution()

    def get_sop_rule(self, rule_code: str) -> Dict[str, Any]:
        """Fetches standard operating procedure guidelines and requirements for a specific rule."""
        rule = RuleLoader.get_rule(rule_code.upper())
        if not rule:
            # Try fuzzy match
            all_rules = RuleLoader.load_rules()
            for k, v in all_rules.items():
                if rule_code.lower() in v.get("name", "").lower():
                    return v
            return {"error": f"SOP Rule '{rule_code}' not recognized."}
        return rule

    def get_incident_evidence(self, event_id: int) -> Dict[str, Any]:
        """Extracts algorithmic evidence chain for a specific incident."""
        inc = self.get_incident(event_id)
        if "error" in inc:
            return inc
        return {
            "event_id": event_id,
            "evidence": inc.get("evidence", []),
            "factors": inc.get("factors", []),
            "sop_violation": inc.get("behaviour_name")
        }

    def get_repeated_patterns(self) -> List[Dict[str, Any]]:
        """Identifies recurring violation hotspots across warehouse zones."""
        with self.db_factory() as db:
            repo = AnalyticsRepository(db)
            zones = repo.get_zone_distribution()
            behaviours = repo.get_behaviour_distribution()
            patterns = []
            if zones:
                top_z = zones[0]
                patterns.append({
                    "pattern_type": "Zone Concentration",
                    "description": f"Zone '{top_z['zone']}' accounts for {top_z['count']} handling anomalies with average risk {top_z['avg_risk']}."
                })
            if behaviours:
                top_b = behaviours[0]
                patterns.append({
                    "pattern_type": "Prevalent Non-Compliance",
                    "description": f"'{top_b['behaviour']}' is the most frequent observed violation with {top_b['count']} events recorded."
                })
            return patterns

    def get_recommendations(self) -> List[str]:
        """Provides operational supervisor recommendations derived from observed violations."""
        with self.db_factory() as db:
            repo = AnalyticsRepository(db)
            behaviours = repo.get_behaviour_distribution()
            recs = [
                "Enforce gentle staging protocols during peak shift unloading.",
                "Verify hand trolley and pallet jack availability in active staging zones."
            ]
            for b in behaviours:
                if "Drag" in b["behaviour"]:
                    recs.append("Deploy dedicated hydraulic dollies in Staging Zone B to eliminate manual dragging.")
                if "Drop" in b["behaviour"]:
                    recs.append("Conduct immediate carton integrity inspection on recently unloaded bay lots.")
                if "Overhang" in b["behaviour"]:
                    recs.append("Check pallet wrap alignment before forklift transit to eliminate corner overhang.")
            return list(dict.fromkeys(recs))[:5]

mcp_server = CargoIQMcpServer()
