'use client'
import { useQuery } from '@tanstack/react-query'
import { productionService } from '@/services/production.service'

export function useWorkOrders(status?: string) {
  return useQuery({
    queryKey: ['work-orders', status],
    queryFn: () => productionService.listWorkOrders({ status }),
    staleTime: 30_000,
  })
}
