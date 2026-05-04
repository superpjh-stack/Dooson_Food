import { apiClient } from '@/lib/api/client'
import type { CcpRecord, XRayResult } from '@/lib/api/types'

export const qualityService = {
  async listCcpRecords(params?: {
    lot_id?: string
    work_order_id?: string
    skip?: number
    limit?: number
  }) {
    const { data } = await apiClient.get<CcpRecord[]>('/api/v1/quality/ccp-records', { params })
    return data
  },

  async listXRayResults(params?: { lot_id?: string; result?: string }) {
    const { data } = await apiClient.get<XRayResult[]>('/api/v1/quality/xray-results', { params })
    return data
  },
}
