import yaml
from pathlib import Path
from typing import Dict, Any, List

RULES_PATH = Path(__file__).resolve().parent / "godrej_rules.yaml"

class RuleLoader:
    _rules_cache: Dict[str, Any] = {}

    @classmethod
    def load_rules(cls, force_reload: bool = False) -> Dict[str, Any]:
        if not cls._rules_cache or force_reload:
            if RULES_PATH.exists():
                with open(RULES_PATH, "r", encoding="utf-8") as f:
                    cls._rules_cache = yaml.safe_load(f) or {}
            else:
                cls._rules_cache = {}
        return cls._rules_cache

    @classmethod
    def get_rule(cls, code: str) -> Dict[str, Any]:
        rules = cls.load_rules()
        return rules.get(code, {})

    @classmethod
    def list_rules(cls) -> List[Dict[str, Any]]:
        rules = cls.load_rules()
        return list(rules.values())
