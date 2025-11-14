import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type { Event, Report, Alert, Sentiment, CityStats, AnalyticsData } from '@/types';

export function useEvents(params?: Parameters<typeof apiClient.getEvents>[0]) {
  return useQuery({
    queryKey: ['events', params],
    queryFn: () => apiClient.getEvents(params),
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 20000,
  });
}

export function useEventById(id: string) {
  return useQuery({
    queryKey: ['event', id],
    queryFn: () => apiClient.getEventById(id),
    enabled: !!id,
  });
}

export function useReports(params?: Parameters<typeof apiClient.getReports>[0]) {
  return useQuery({
    queryKey: ['reports', params],
    queryFn: () => apiClient.getReports(params),
    refetchInterval: 60000,
  });
}

export function useCreateReport() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: FormData) => apiClient.createReport(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
  });
}

export function useAlerts(params?: Parameters<typeof apiClient.getAlerts>[0]) {
  return useQuery({
    queryKey: ['alerts', params],
    queryFn: () => apiClient.getAlerts(params),
    refetchInterval: 30000,
  });
}

export function useSentiments(params?: Parameters<typeof apiClient.getSentiments>[0]) {
  return useQuery({
    queryKey: ['sentiments', params],
    queryFn: () => apiClient.getSentiments(params),
    refetchInterval: 60000,
  });
}

export function useCityStats() {
  return useQuery({
    queryKey: ['cityStats'],
    queryFn: () => apiClient.getCityStats(),
    refetchInterval: 30000,
  });
}

export function useAnalytics(params?: Parameters<typeof apiClient.getAnalytics>[0]) {
  return useQuery({
    queryKey: ['analytics', params],
    queryFn: () => apiClient.getAnalytics(params),
    staleTime: 300000, // 5 minutes
  });
}

export function useSubscriptions(userId: string) {
  return useQuery({
    queryKey: ['subscriptions', userId],
    queryFn: () => apiClient.getSubscriptions(userId),
    enabled: !!userId,
  });
}

export function useCreateSubscription() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: Parameters<typeof apiClient.createSubscription>[0]) =>
      apiClient.createSubscription(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] });
    },
  });
}

export function useDeleteSubscription() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => apiClient.deleteSubscription(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] });
    },
  });
}
