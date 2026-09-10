from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories.analytics_repo import AnalyticsRepository

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview")
def get_analytics_overview(db: Session = Depends(get_db)):
    repo = AnalyticsRepository(db)
    kpis = repo.get_overview()
    behaviours = repo.get_behaviour_distribution()
    zones = repo.get_zone_distribution()
    trends = repo.get_risk_trends()

    return {
        "success": True,
        "data": {
            "kpis": kpis,
            "behaviours": behaviours,
            "zones": zones,
            "trends": trends
        },
        "error": None
    }

@router.get("/behaviours")
def get_behaviour_stats(db: Session = Depends(get_db)):
    repo = AnalyticsRepository(db)
    return {
        "success": True,
        "data": repo.get_behaviour_distribution(),
        "error": None
    }

@router.get("/zones")
def get_zone_stats(db: Session = Depends(get_db)):
    repo = AnalyticsRepository(db)
    return {
        "success": True,
        "data": repo.get_zone_distribution(),
        "error": None
    }

@router.get("/trends")
def get_risk_trends(db: Session = Depends(get_db)):
    repo = AnalyticsRepository(db)
    return {
        "success": True,
        "data": repo.get_risk_trends(),
        "error": None
    }
