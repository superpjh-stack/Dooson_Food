'use client'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api/client'

export interface Notification {
  id: number
  type: string
  severity: 'CRITICAL' | 'WARNING' | 'INFO'
  title: string
  body: string
  created_at: string
  is_read: boolean
}

export function useNotifications(limit = 10) {
  return useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const { data } = await apiClient.get<Notification[]>('/api/v1/notifications', { params: { limit } })
      return data
    },
    refetchInterval: 15_000,
    staleTime: 10_000,
  })
}
