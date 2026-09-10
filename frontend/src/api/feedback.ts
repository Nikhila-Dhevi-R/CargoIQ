import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from './client';
import { FeedbackItem, FeedbackSummary } from '../types';

export function useFeedbackSummary() {
  return useQuery<FeedbackSummary>({
    queryKey: ['feedback-summary'],
    queryFn: () => apiRequest<FeedbackSummary>('/feedback/summary'),
    refetchInterval: 5000
  });
}

export function useFeedbackList(limit: number = 50) {
  return useQuery<FeedbackItem[]>({
    queryKey: ['feedback-list', limit],
    queryFn: () => apiRequest<FeedbackItem[]>(`/feedback?limit=${limit}`)
  });
}

export function useSubmitFeedback() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      eventId,
      feedbackType,
      comment,
      userId
    }: {
      eventId: number;
      feedbackType: 'correct' | 'incorrect' | 'unsure';
      comment?: string;
      userId?: string;
    }) => {
      return apiRequest<FeedbackItem>('/feedback', {
        method: 'POST',
        body: JSON.stringify({
          event_id: eventId,
          feedback_type: feedbackType,
          comment,
          user_id: userId || 'Supervisor'
        })
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedback-summary'] });
      queryClient.invalidateQueries({ queryKey: ['feedback-list'] });
    }
  });
}
