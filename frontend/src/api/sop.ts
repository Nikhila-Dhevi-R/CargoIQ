import { useQuery } from '@tanstack/react-query';
import { apiRequest } from './client';
import { SopRule } from '../types';

export function useSopRules() {
  return useQuery<SopRule[]>({
    queryKey: ['sop-rules'],
    queryFn: () => apiRequest<SopRule[]>('/sop/rules')
  });
}

export function useSopRule(code?: string) {
  return useQuery<SopRule>({
    queryKey: ['sop-rule', code],
    queryFn: () => apiRequest<SopRule>(`/sop/rules/${code}`),
    enabled: !!code
  });
}

export function useWarehouseZones() {
  return useQuery<any[]>({
    queryKey: ['warehouse-zones'],
    queryFn: () => apiRequest<any[]>('/sop/zones')
  });
}
