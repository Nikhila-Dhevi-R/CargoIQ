import pytest
from app.risk.risk_engine import RiskEngine
from app.intelligence.geometry import calculate_iou, calculate_support_ratio, point_in_polygon
from app.sop.rule_loader import RuleLoader
from app.sop.rule_engine import RuleEngine
from app.behaviours.overhang import PalletOverhangBehaviour
from app.intelligence.object_memory import ObjectMemory

def test_geometry_iou():
    boxA = [10, 10, 50, 50]
    boxB = [10, 10, 50, 50]
    assert calculate_iou(boxA, boxB) == 1.0

    boxC = [100, 100, 150, 150]
    assert calculate_iou(boxA, boxC) == 0.0

def test_geometry_support_ratio():
    # Carton sitting flush on pallet
    carton = [100, 100, 200, 150]
    pallet = [100, 150, 200, 180]
    ratio = calculate_support_ratio(carton, pallet)
    assert ratio >= 0.95

    # Overhang: carton wider than pallet on right side
    carton_overhang = [100, 100, 250, 150] # width 150
    pallet_base = [100, 150, 200, 180]     # pallet width 100
    ratio_oh = calculate_support_ratio(carton_overhang, pallet_base)
    assert ratio_oh < 0.90
    assert ratio_oh > 0.50

def test_point_in_polygon():
    poly = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]
    assert point_in_polygon((0.5, 0.5), poly) is True
    assert point_in_polygon((1.5, 0.5), poly) is False

def test_risk_engine_deterministic():
    # Critical drop scenario
    crit_risk = RiskEngine.calculate_risk(
        behaviour_severity="HIGH",
        motion_intensity=0.9,
        duration_s=2.0,
        spatial_factor=0.8,
        repetition_count=2,
        zone="Loading Bay 1"
    )
    assert crit_risk["level"] in ["HIGH", "CRITICAL"]
    assert 55 <= crit_risk["score"] <= 100
    assert len(crit_risk["factors"]) == 6

    # Low severity scenario
    low_risk = RiskEngine.calculate_risk(
        behaviour_severity="LOW",
        motion_intensity=0.1,
        duration_s=1.0,
        spatial_factor=0.1,
        repetition_count=1,
        zone="Dispatch Area"
    )
    assert low_risk["level"] in ["LOW", "MEDIUM"]
    assert low_risk["score"] < 55

def test_sop_rules_loaded():
    rules = RuleLoader.load_rules()
    assert len(rules) >= 10
    assert "DROP_PRODUCT" in rules
    assert "DRAG_PRODUCT" in rules
    assert "PALLET_OVERHANG" in rules
    assert "IMPROPER_STAGING" in rules
    assert "STACK_ORDER" in rules

def test_pallet_overhang_behaviour():
    carton_overhang = [100, 100, 250, 150]
    pallet_base = [100, 150, 200, 180]
    res = PalletOverhangBehaviour.analyze(carton_overhang, pallet_base, threshold=0.90)
    assert res is not None
    assert res["behaviour"] == "PALLET_OVERHANG"
    assert res["severity"] == "HIGH"
