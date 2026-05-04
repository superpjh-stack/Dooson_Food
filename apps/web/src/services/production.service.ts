import { apiClient } from '@/lib/api/client'
import type { ProductionLine, WorkOrder, WorkOrderListResponse } from '@/lib/api/types'

export const productionService = {
  async listWorkOrders(params?: { status?: string; skip?: number; limit?: number }) {
    const { data } = await apiClient.get<WorkOrderListResponse>('/api/v1/production/work-orders', {
      params,
    })
    return data
  },

  async getWorkOrder(id: string) {
    const { data } = await apiClient.get<WorkOrder>(`/api/v1/production/work-orders/${id}`)
    return data
  },

  async startWorkOrder(id: string) {
    const { data } = await apiClient.post<WorkOrder>(`/api/v1/production/work-orders/${id}/start`)
    return data
  },

  async completeWorkOrder(id: string, actual_qty: number) {
    const { data } = await apiClient.post<WorkOrder>(
      `/api/v1/production/work-orders/${id}/complete`,
      { actual_qty }
    )
    return data
  },

  async listProductionLines() {
    const { data } = await apiClient.get<ProductionLine[]>('/api/v1/production/lines')
    return data
  },

  async listProcesses(lineId?: number) {
    const { data } = await apiClient.get('/api/v1/production/processes', {
      params: { line_id: lineId },
    })
    return data
  },
}
