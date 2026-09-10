import { useQuery } from '@tanstack/react-query';
import { apiRequest } from './client';
import { SystemHealth } from '../types';

export function useSystemHealth() {
  return useQuery<SystemHealth>({
    queryKey: ['system-health'],
    queryFn: () => apiRequest<SystemHealth>('/system/health'),
    refetchInterval: 6000
  });
}
