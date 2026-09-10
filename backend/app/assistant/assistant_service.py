import json
from typing import Dict, Any, Optional, List
from app.core.logging import logger
from app.mcp.server import mcp_server
from app.assistant.ollama_client import ollama_client
from app.assistant.prompts import SYSTEM_PROMPT, INCIDENT_EXPLAIN_PROMPT, SHIFT_SUMMARY_PROMPT
from app.assistant.context_builder import ContextBuilder

class AssistantService:
    @classmethod
    async def chat(cls, message: str, video_id: Optional[int] = None, event_id: Optional[int] = None) -> Dict[str, Any]:
        msg_lower = message.lower()
        context_str = ContextBuilder.build_general_context()

        # Specific event targeted
        if event_id:
            event_data = mcp_server.get_incident(event_id)
            context_str += f"\n\n=== TARGET INCIDENT (EVENT #{event_id}) ===\n{json.dumps(event_data, indent=2)}"

        user_prompt = f"""WAREHOUSE INTELLIGENCE DATA:
{context_str}

SUPERVISOR QUESTION:
{message}

Please provide an accurate, grounded, actionable answer based strictly on the data above. If the data does not contain the answer, say 'I don't have enough evidence in the analysed warehouse data to answer that.'"""

        # Call Ollama
        llm_reply = await ollama_client.generate_response(SYSTEM_PROMPT, user_prompt)

        citations = []
        if "event" in msg_lower or event_id:
            citations.append(f"Event #{event_id}" if event_id else "Incident Database")
        citations.append("CargoIQ operational intelligence")

        if llm_reply:
            return {
                "reply": llm_reply,
                "citations": citations,
                "confidence": 0.95
            }

        # Deterministic fallback response synthesis if LLM offline
        return cls._synthesize_fallback_reply(message, msg_lower)

    @classmethod
    async def explain_incident(cls, event_id: int) -> Dict[str, Any]:
        inc = mcp_server.get_incident(event_id)
        if "error" in inc:
            return {"error": inc["error"]}

        rule = mcp_server.get_sop_rule(inc.get("behaviour", ""))
        evidence_list = inc.get("evidence", [])
        evidence_str = "\n".join([f"  - {e}" for e in evidence_list])

        prompt = INCIDENT_EXPLAIN_PROMPT.format(
            event_id=event_id,
            behaviour_name=inc.get("behaviour_name", "Handling Anomaly"),
            object_id=inc.get("object_id", "Unknown"),
            timestamp=inc.get("timestamp", "00:00"),
            risk_score=inc.get("risk_score", 0),
            risk_level=inc.get("risk_level", "MEDIUM"),
            zone=inc.get("zone", "General Area"),
            evidence_str=evidence_str,
            sop_name=rule.get("name", "Standard Handling Guideline"),
            sop_desc=rule.get("description", "Material must be handled safely."),
            recommendation=inc.get("recommendation", "Review handling procedure.")
        )

        llm_text = await ollama_client.generate_response(SYSTEM_PROMPT, prompt)

        if not llm_text:
            # High-quality structured fallback
            what = f"CargoIQ observed {inc.get('behaviour_name')} involving {inc.get('object_id')} in {inc.get('zone')}."
            why = "The observation meets configured operational-risk conditions; it does not confirm physical product damage."
            rec = inc.get("recommendation") or "Review the handling procedure and inspect the item where operationally appropriate."
            llm_text = f"**1. WHAT HAPPENED:**\n{what}\n\n**2. WHY IT WAS RISKY:**\n{why}\n\n**3. EVIDENCE:**\n{evidence_str}\n\n**4. RELEVANT SOP:**\n{rule.get('name', 'General Handling SOP')}\n\n**5. RECOMMENDED SUPERVISOR ACTION:**\n{rec}"

        return {
            "event_id": event_id,
            "what_happened": f"Observed {inc.get('behaviour_name')} involving {inc.get('object_id')} in {inc.get('zone')}.",
            "why_risky": f"Assessed at {inc.get('risk_score')}/100 ({inc.get('risk_level')}) from deterministic motion, duration, spatial, repetition, and location factors.",
            "evidence": evidence_list,
            "sop_rule": inc.get("behaviour", "GENERAL"),
            "sop_rule_name": rule.get("name", "Handling Standard"),
            "recommendation": inc.get("recommendation", "Inspect carton before transit."),
            "full_explanation": llm_text
        }

    @classmethod
    async def generate_shift_summary(cls, video_id: Optional[int] = None) -> Dict[str, Any]:
        kpis = mcp_server.get_risk_summary()
        behaviours = mcp_server.get_behaviour_statistics()
        zones = mcp_server.get_zone_statistics()
        patterns = mcp_server.get_repeated_patterns()
        recommendations = mcp_server.get_recommendations()

        top_behaviour = behaviours[0]["behaviour"] if behaviours else "None"
        top_zone = zones[0]["zone"] if zones else "Loading Bay 1"

        summary_data = f"""Total Handling Events Analysed: {kpis.get('total_handling_events', 0)}
Potential Risk Events: {kpis.get('risk_events', 0)}
Critical Severity Events: {kpis.get('critical_events', 0)}
High Severity Events: {kpis.get('high_risk_events', 0)}
Medium Severity Events: {kpis.get('medium_risk_events', 0)}
Low Severity Events: {kpis.get('low_risk_events', 0)}
Most Frequent Risky Behaviour: {top_behaviour}
Highest-Risk Zone Hotspot: {top_zone}
Recurring Patterns: {'; '.join([p['description'] for p in patterns])}
Recommended Actions: {'; '.join(recommendations)}"""

        prompt = SHIFT_SUMMARY_PROMPT.format(shift_data=summary_data)
        llm_text = await ollama_client.generate_response(SYSTEM_PROMPT, prompt)

        if not llm_text:
            llm_text = f"""### Warehouse Operational Shift Summary

**Executive Overview:**
A total of {kpis.get('total_handling_events', 0)} material movements were continuously monitored. The system identified {kpis.get('risk_events', 0)} potential risk events ({kpis.get('critical_events', 0)} Critical, {kpis.get('high_risk_events', 0)} High).

**Operational Hotspots:**
- **Prevalent Violation:** {top_behaviour} was the most frequently observed non-compliance.
- **Risk Hotspot:** {top_zone} recorded the highest density of high-risk handling events.

**Supervisor Preventive Recommendations:**
1. Verify equipment availability (hand pallet trucks and dollies) to prevent manual dragging.
2. Conduct targeted refresher briefing with unloading crews on gentle staging.
3. Inspect recently unloaded pallet units for edge overhang and corner crushing."""

        return {
            "shift_title": "Shift Operational Intelligence Briefing",
            "total_events": kpis.get("total_handling_events", 0),
            "risk_events": kpis.get("risk_events", 0),
            "critical": kpis.get("critical_events", 0),
            "high": kpis.get("high_risk_events", 0),
            "medium": kpis.get("medium_risk_events", 0),
            "low": kpis.get("low_risk_events", 0),
            "most_frequent_behaviour": top_behaviour,
            "highest_risk_incident": f"Critical Handling Anomaly in {top_zone}",
            "highest_risk_zone": top_zone,
            "recurring_patterns": [p["description"] for p in patterns],
            "recommendations": recommendations,
            "full_summary_text": llm_text
        }

    @classmethod
    def _synthesize_fallback_reply(cls, message: str, msg_lower: str) -> Dict[str, Any]:
        kpis = mcp_server.get_risk_summary()
        zones = mcp_server.get_zone_statistics()
        behaviours = mcp_server.get_behaviour_statistics()

        if "serious" in msg_lower or "critical" in msg_lower or "high risk" in msg_lower:
            high_incidents = mcp_server.search_incidents(risk_level="HIGH", limit=5)
            crit_incidents = mcp_server.search_incidents(risk_level="CRITICAL", limit=5)
            all_high = crit_incidents + high_incidents
            if all_high:
                reply = f"There are {len(all_high)} serious incidents recorded:\n" + "\n".join([
                    f"- **Event #{inc['id']}** at {inc['timestamp']} in {inc['zone']}: {inc['behaviour']} ({inc['object_id']}) with Risk Score {inc['risk_score']}/100 ({inc['risk_level']})."
                    for inc in all_high[:4]
                ])
            else:
                reply = "No critical or high-risk incidents have been recorded in the analysed video sessions."
            return {"reply": reply, "citations": ["Incident database", "CargoIQ risk engine"], "confidence": 0.95}

        elif "drag" in msg_lower:
            rule = mcp_server.get_sop_rule("DRAG_PRODUCT")
            reply = f"**Dragging Product** is a potential handling risk because sustained floor contact can increase packaging wear. According to CargoIQ SOP: *'{rule.get('recommendation', 'Use suitable handling equipment.')}'*"
            return {"reply": reply, "citations": ["CargoIQ SOP rule: DRAG_PRODUCT"], "confidence": 0.95}

        elif "zone" in msg_lower or "loading bay" in msg_lower or "hotspot" in msg_lower:
            if zones:
                top = zones[0]
                reply = f"**{top['zone']}** has the highest operational risk profile, accounting for {top['count']} incidents with an average risk score of {top['avg_risk']}/100."
            else:
                reply = "Zone distribution data is currently being populated as warehouse video feeds are processed."
            return {"reply": reply, "citations": ["Zone Risk Analytics"], "confidence": 0.95}

        elif "behaviour" in msg_lower or "frequent" in msg_lower or "common" in msg_lower:
            if behaviours:
                top = behaviours[0]
                reply = f"The most frequent risky behaviour observed is **{top['behaviour']}** with {top['count']} recorded occurrences."
            else:
                reply = "No specific behaviour anomalies have been detected yet."
            return {"reply": reply, "citations": ["Behaviour Frequency Engine"], "confidence": 0.95}

        else:
            return {
                "reply": f"Based on warehouse telemetry: {kpis.get('total_handling_events', 0)} movements have been analysed with {kpis.get('risk_events', 0)} potential risk events ({kpis.get('critical_events', 0)} Critical, {kpis.get('high_risk_events', 0)} High). You can ask me about specific incidents, SOP rules, zone hazards, or shift summaries.",
                "citations": ["CargoIQ operational data"],
                "confidence": 0.90
            }
