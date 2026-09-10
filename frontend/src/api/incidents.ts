import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from './client';
import { Incident, ReviewStatus } from '../types';

interface IncidentFilters {
  videoId?: number;
  riskLevel?: string;
  behaviour?: string;
  zone?: string;
  reviewStatus?: string;
  limit?: number;
}

export function useIncidents(filters?: IncidentFilters) {
  const params = new URLSearchParams();
  if (filters?.videoId) params.append('video_id', String(filters.videoId));
  if (filters?.riskLevel && filters.riskLevel !== 'ALL') params.append('risk_level', filters.riskLevel);
  if (filters?.behaviour && filters.behaviour !== 'ALL') params.append('behaviour', filters.behaviour);
  if (filters?.zone && filters.zone !== 'ALL') params.append('zone', filters.zone);
  if (filters?.reviewStatus && filters.reviewStatus !== 'ALL') params.append('review_status', filters.reviewStatus);
  if (filters?.limit) params.append('limit', String(filters.limit));

  const queryStr = params.toString() ? `?${params.toString()}` : '';

  return useQuery<Incident[]>({
    queryKey: ['incidents', filters],
    queryFn: () => apiRequest<Incident[]>(`/events${queryStr}`),
    refetchInterval: 3000
  });
}

export function useIncident(id?: number) {
  return useQuery<Incident>({
    queryKey: ['incident', id],
    queryFn: () => apiRequest<Incident>(`/events/${id}`),
    enabled: !!id
  });
}

export function useReviewIncident() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, status, notes }: { id: number; status: ReviewStatus; notes?: string }) => {
      return apiRequest<Incident>(`/events/${id}/review`, {
        method: 'PATCH',
        body: JSON.stringify({ status, notes })
      });
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      queryClient.invalidateQueries({ queryKey: ['incident', data.id] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    }
  });
}
