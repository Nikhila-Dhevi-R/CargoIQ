from fastapi import APIRouter, HTTPException
from app.sop.rule_loader import RuleLoader
from app.intelligence.zones import DEFAULT_ZONES

router = APIRouter(prefix="/sop", tags=["SOP Rules"])

@router.get("/rules")
def list_sop_rules():
    rules = RuleLoader.list_rules()
    return {
        "success": True,
        "data": rules,
        "error": None
    }

@router.get("/rules/{rule_code}")
def get_sop_rule(rule_code: str):
    rule = RuleLoader.get_rule(rule_code.upper())
    if not rule:
        raise HTTPException(status_code=404, detail=f"SOP Rule '{rule_code}' not found.")
    return {
        "success": True,
        "data": rule,
        "error": None
    }

@router.get("/zones")
def list_warehouse_zones():
    return {
        "success": True,
        "data": DEFAULT_ZONES,
        "error": None
    }
