import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import SopRule, Zone

class SopRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[SopRule]:
        return self.db.query(SopRule).all()

    def get_by_code(self, code: str) -> Optional[SopRule]:
        return self.db.query(SopRule).filter(SopRule.code == code).first()

    def upsert(self, code: str, name: str, severity: str, conditions: dict, recommendation: str, description: str = "") -> SopRule:
        rule = self.get_by_code(code)
        if not rule:
            rule = SopRule(
                code=code,
                name=name,
                severity=severity,
                conditions_json=json.dumps(conditions),
                recommendation=recommendation,
                description=description,
                is_active=True
            )
            self.db.add(rule)
        else:
            rule.name = name
            rule.severity = severity
            rule.conditions_json = json.dumps(conditions)
            rule.recommendation = recommendation
            rule.description = description
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def get_zones(self) -> List[Zone]:
        return self.db.query(Zone).filter(Zone.is_active == True).all()

    def upsert_zone(self, name: str, polygon: list, description: str = "", color: str = "#3b82f6") -> Zone:
        zone = self.db.query(Zone).filter(Zone.name == name).first()
        if not zone:
            zone = Zone(
                name=name,
                polygon_json=json.dumps(polygon),
                description=description,
                color=color,
                is_active=True
            )
            self.db.add(zone)
        else:
            zone.polygon_json = json.dumps(polygon)
            zone.description = description
            zone.color = color
        self.db.commit()
        self.db.refresh(zone)
        return zone
