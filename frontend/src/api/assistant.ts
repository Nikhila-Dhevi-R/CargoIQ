import { useMutation } from '@tanstack/react-query';
import { apiRequest } from './client';

export interface ChatPayload {
  message: string;
  video_id?: number;
  event_id?: number;
}

export function useSendAssistantMessage() {
  return useMutation({
    mutationFn: async (payload: ChatPayload) => {
      return apiRequest<{
        reply: string;
        citations: string[];
        confidence: number;
      }>('/assistant/chat', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
    }
  });
}

export function useExplainIncident() {
  return useMutation({
    mutationFn: async (eventId: number) => {
      return apiRequest<{
        event_id: number;
        what_happened: string;
        why_risky: string;
        evidence: string[];
        sop_rule: string;
        sop_rule_name: string;
        recommendation: string;
        full_explanation: string;
      }>('/assistant/explain', {
        method: 'POST',
        body: JSON.stringify({ event_id: eventId })
      });
    }
  });
}

export function useGenerateShiftSummary() {
  return useMutation({
    mutationFn: async (videoId?: number) => {
      return apiRequest<{
        shift_title: string;
        total_events: number;
        risk_events: number;
        critical: number;
        high: number;
        medium: number;
        low: number;
        most_frequent_behaviour: string;
        highest_risk_incident: string;
        highest_risk_zone: string;
        recurring_patterns: string[];
        recommendations: string[];
        full_summary_text: string;
      }>('/assistant/summary', {
        method: 'POST',
        body: JSON.stringify({ video_id: videoId })
      });
    }
  });
}
