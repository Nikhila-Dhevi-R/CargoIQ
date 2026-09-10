from typing import List, Dict, Any

class RiskFactors:
    @staticmethod
    def format_breakdown(factors: List[Dict[str, Any]]) -> str:
        return ", ".join([f"{f['name']}: {f['contribution']}pts" for f in factors])
