import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from './client';
import { Video, Incident, AnalysisJob } from '../types';

export interface VideoAnalysisStatus {
  video_id: number;
  status: Video['status'];
  latest_job: Pick<AnalysisJob, 'job_id' | 'status' | 'progress' | 'step_description'> | null;
}

export function useVideos() {
  return useQuery<Video[]>({
    queryKey: ['videos'],
    queryFn: () => apiRequest<Video[]>('/videos'),
    refetchInterval: 5000
  });
}

export function useVideo(id?: number) {
  return useQuery<Video>({
    queryKey: ['video', id],
    queryFn: () => apiRequest<Video>(`/videos/${id}`),
    enabled: !!id
  });
}

export function useVideoEvents(videoId?: number) {
  return useQuery<Incident[]>({
    queryKey: ['video-events', videoId],
    queryFn: () => apiRequest<Incident[]>(`/videos/${videoId}/events`),
    enabled: !!videoId,
    refetchInterval: 3000
  });
}

export function useVideoAnalysisStatus(videoId?: number) {
  return useQuery<VideoAnalysisStatus>({
    queryKey: ['video-status', videoId],
    queryFn: () => apiRequest<VideoAnalysisStatus>(`/videos/${videoId}/status`),
    enabled: !!videoId,
    refetchInterval: 1000
  });
}

export function useUploadVideo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ file, autoAnalyse }: { file: File; autoAnalyse?: boolean }) => {
      const formData = new FormData();
      formData.append('file', file);
      if (autoAnalyse) {
        formData.append('auto_analyse', 'true');
      }
      const res = await fetch('/api/videos/upload', {
        method: 'POST',
        body: formData
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(err.detail || 'Failed to upload video');
      }
      const data = await res.json();
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] });
    }
  });
}

export function useUploadVideoUrl() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ url, autoAnalyse }: { url: string; autoAnalyse?: boolean }) => {
      return apiRequest<any>('/videos/url', {
        method: 'POST',
        body: JSON.stringify({ url, auto_analyse: autoAnalyse })
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] });
    }
  });
}

export function useStartAnalysis() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (videoId: number) => {
      return apiRequest<AnalysisJob>(`/videos/${videoId}/analyse`, {
        method: 'POST'
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] });
    }
  });
}
