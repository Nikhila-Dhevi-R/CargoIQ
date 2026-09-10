import json
from typing import Dict, Any, List
from app.mcp.server import mcp_server

class ContextBuilder:
    @staticmethod
    def build_general_context() -> str:
        kpis = mcp_server.get_risk_summary()
        behaviours = mcp_server.get_behaviour_statistics()
        zones = mcp_server.get_zone_statistics()
        recent_incidents = mcp_server.search_incidents(limit=10)

        lines = [
            "=== CURRENT WAREHOUSE OPERATIONAL SUMMARY ===",
            f"- Total Videos Analysed: {kpis.get('total_videos_analysed', 0)}",
            f"- Total Handling Events: {kpis.get('total_handling_events', 0)}",
            f"- Risk Events (Medium/High/Critical): {kpis.get('risk_events', 0)}",
            f"- Critical Events: {kpis.get('critical_events', 0)}",
            f"- High Risk Events: {kpis.get('high_risk_events', 0)}",
            f"- Potentially Preventable Incidents: {kpis.get('potentially_preventable_incidents', 0)}",
            "",
            "=== BEHAVIOUR FREQUENCY ==="
        ]
        for b in behaviours:
            lines.append(f"- {b['behaviour']}: {b['count']} events (Avg Risk: {b['avg_risk']})")

        lines.append("")
        lines.append("=== ZONE RISK DISTRIBUTION ===")
        for z in zones:
            lines.append(f"- {z['zone']}: {z['count']} incidents (Avg Risk: {z['avg_risk']})")

        lines.append("")
        lines.append("=== RECENT DETECTED INCIDENTS ===")
        for inc in recent_incidents:
            lines.append(f"- Event #{inc['id']} [{inc['timestamp']}] in {inc['zone']}: {inc['behaviour']} ({inc['object_id']}) - Risk {inc['risk_score']} ({inc['risk_level']})")

        return "\n".join(lines)
