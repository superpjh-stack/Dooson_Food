'use client'
import { useQuery } from '@tanstack/react-query'
import { lotService } from '@/services/lot.service'

export function useLotTraceBackward(lotId: string | null) {
  return useQuery({
    queryKey: ['lot-trace-backward', lotId],
    queryFn: () => lotService.traceBackward(lotId!),
    enabled: lotId !== null,
    staleTime: 60_000,
  })
}

export function useLotTraceForward(lotId: string | null) {
  return useQuery({
    queryKey: ['lot-trace-forward', lotId],
    queryFn: () => lotService.traceForward(lotId!),
    enabled: lotId !== null,
    staleTime: 60_000,
  })
}
