import { useQuery } from '@tanstack/react-query';
import { apiRequest } from './client';
import { AnalyticsOverview, BehaviourStat, ZoneStat, TrendItem } from '../types';

export function useAnalyticsOverview() {
  return useQuery<AnalyticsOverview>({
    queryKey: ['analytics-overview'],
    queryFn: () => apiRequest<AnalyticsOverview>('/analytics/overview'),
    refetchInterval: 5000
  });
}

export function useBehaviourStats() {
  return useQuery<BehaviourStat[]>({
    queryKey: ['analytics-behaviours'],
    queryFn: () => apiRequest<BehaviourStat[]>('/analytics/behaviours')
  });
}

export function useZoneStats() {
  return useQuery<ZoneStat[]>({
    queryKey: ['analytics-zones'],
    queryFn: () => apiRequest<ZoneStat[]>('/analytics/zones')
  });
}

export function useRiskTrends() {
  return useQuery<TrendItem[]>({
    queryKey: ['analytics-trends'],
    queryFn: () => apiRequest<TrendItem[]>('/analytics/trends')
  });
}
