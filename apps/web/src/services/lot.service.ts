import { apiClient } from '@/lib/api/client'
import type { Lot, LotTraceResponse, LotForwardTraceResponse, PaginatedResponse } from '@/lib/api/types'

export const lotService = {
  async list(params?: { status?: string; type?: string; skip?: number; limit?: number }) {
    const { data } = await apiClient.get<PaginatedResponse<Lot>>('/api/v1/lots', { params })
    return data
  },

  async get(id: string) {
    const { data } = await apiClient.get<Lot>(`/api/v1/lots/${id}`)
    return data
  },

  async traceBackward(id: string) {
    const { data } = await apiClient.get<LotTraceResponse>(`/api/v1/lots/${id}/trace/backward`)
    return data
  },

  async traceForward(id: string) {
    const { data } = await apiClient.get<LotForwardTraceResponse>(`/api/v1/lots/${id}/trace/forward`)
    return data
  },

  async hold(id: string, reason: string, held_by = 'system') {
    const { data } = await apiClient.patch<Lot>(`/api/v1/lots/${id}/hold`, null, {
      params: { reason, held_by },
    })
    return data
  },

  async release(id: string) {
    const { data } = await apiClient.patch<Lot>(`/api/v1/lots/${id}/release`)
    return data
  },
}
