'use client'
import { useQuery } from '@tanstack/react-query'
import { qualityService } from '@/services/quality.service'

export function useCcpRecords(lotId?: string, workOrderId?: string) {
  return useQuery({
    queryKey: ['ccp-records', lotId, workOrderId],
    queryFn: () => qualityService.listCcpRecords({ lot_id: lotId, work_order_id: workOrderId }),
    staleTime: 15_000,
  })
}
