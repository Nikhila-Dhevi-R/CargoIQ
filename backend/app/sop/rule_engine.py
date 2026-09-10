import re
from typing import Dict, Any, Optional
from app.sop.rule_loader import RuleLoader

class RuleEngine:
    def __init__(self):
        self.rules = RuleLoader.load_rules()

    def evaluate_behaviour(self, behaviour_code: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        rule = self.rules.get(behaviour_code)
        if not rule:
            return None

        conditions = rule.get("conditions", {})
        all_passed = True
        evidence_list = []

        # Evaluate against context
        for key, expected in conditions.items():
            actual = context.get(key)
            if isinstance(expected, bool):
                if actual != expected:
                    all_passed = False
                    break
            elif isinstance(expected, str):
                comparison = re.fullmatch(r"\s*(>=|<=|>|<)\s*(-?\d+(?:\.\d+)?)\s*", expected)
                if not comparison:
                    continue
                if actual is None:
                    all_passed = False
                    break
                operator, threshold = comparison.groups()
                actual_number, expected_number = float(actual), float(threshold)
                matches = {
                    ">": actual_number > expected_number,
                    ">=": actual_number >= expected_number,
                    "<": actual_number < expected_number,
                    "<=": actual_number <= expected_number,
                }[operator]
                if not matches:
                    all_passed = False
                    break

        if not all_passed:
            return None

        # Build evidence strings using templates
        templates = rule.get("evidence_templates", [])
        for tmpl in templates:
            try:
                ev = tmpl.format(**context)
                evidence_list.append(ev)
            except Exception:
                evidence_list.append(tmpl)

        return {
            "code": rule.get("code"),
            "name": rule.get("name"),
            "severity": rule.get("severity", "HIGH"),
            "evidence": evidence_list,
            "recommendation": rule.get("recommendation", "")
        }
