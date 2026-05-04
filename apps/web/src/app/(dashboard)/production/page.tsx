'use client'

import { useQueryClient } from '@tanstack/react-query'
import { TopBar } from '@/components/layout/TopBar'
import { KpiCard } from '@/components/kpi/KpiCard'
import { useWorkOrders } from '@/hooks/use-work-orders'
import { productionService } from '@/services/production.service'
import type { WorkOrderStatus } from '@/lib/api/types'

const STATUS_LABEL: Record<WorkOrderStatus, string> = {
  PLANNED: '계획',
  IN_PROGRESS: '진행중',
  COMPLETED: '완료',
  CANCELLED: '취소',
}

const STATUS_COLOR: Record<WorkOrderStatus, string> = {
  PLANNED: 'bg-info-bg text-info border-info/30',
  IN_PROGRESS: 'bg-success-bg text-success border-success/30',
  COMPLETED: 'bg-muted text-muted-foreground border-border',
  CANCELLED: 'bg-critical-bg text-critical border-critical/30',
}

function StatusBadge({ status }: { status: WorkOrderStatus }) {
  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium border ${STATUS_COLOR[status]}`}>
      {STATUS_LABEL[status]}
    </span>
  )
}

function ProgressBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0
  return (
    <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
      <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${pct}%` }} />
    </div>
  )
}

export default function ProductionPage() {
  const queryClient = useQueryClient()
  const { data: workOrderData, isLoading } = useWorkOrders()
  const workOrders = workOrderData?.items ?? []

  const planned = workOrders.filter((w) => w.status === 'PLANNED').length
  const inProgress = workOrders.filter((w) => w.status === 'IN_PROGRESS').length
  const completed = workOrders.filter((w) => w.status === 'COMPLETED').length

  const handleStart = async (id: string) => {
    await productionService.startWorkOrder(id)
    queryClient.invalidateQueries({ queryKey: ['work-orders'] })
  }

  return (
    <div className="flex flex-col min-h-full">
      <TopBar title="생산관리" />
      <div className="flex-1 p-6 space-y-6">
        <div className="grid grid-cols-3 gap-4">
          <KpiCard label="계획 작업지시" value={String(planned)} icon="📋" color="blue" />
          <KpiCard label="진행중" value={String(inProgress)} icon="⚙" color="orange" />
          <KpiCard label="완료" value={String(completed)} icon="✓" color="green" />
        </div>

        <div className="rounded-lg border bg-card shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/40">
                <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">WO 코드</th>
                <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">상태</th>
                <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">계획 수량</th>
                <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">실적 수량</th>
                <th className="text-left px-4 py-2.5 font-medium text-muted-foreground w-36">진행률</th>
                <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">계획 시작일</th>
                <th className="text-left px-4 py-2.5 font-medium text-muted-foreground" />
              </tr>
            </thead>
            <tbody>
              {isLoading
                ? Array.from({ length: 3 }).map((_, i) => (
                    <tr key={i} className="border-b">
                      {Array.from({ length: 7 }).map((_, j) => (
                        <td key={j} className="px-4 py-3">
                          <div className="animate-pulse bg-border h-4 rounded w-full" />
                        </td>
                      ))}
                    </tr>
                  ))
                : workOrders.length === 0
                ? (
                    <tr>
                      <td colSpan={7} className="px-4 py-8 text-center text-sm text-muted-foreground">
                        등록된 작업지시가 없습니다
                      </td>
                    </tr>
                  )
                : workOrders.map((wo) => (
                    <tr key={wo.id} className="border-b last:border-0 hover:bg-muted/20 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs">{wo.code}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={wo.status} />
                      </td>
                      <td className="px-4 py-3 text-right tabular-nums text-xs">
                        {Number(wo.planned_qty).toLocaleString()} {wo.unit}
                      </td>
                      <td className="px-4 py-3 text-right tabular-nums text-xs">
                        {Number(wo.actual_qty).toLocaleString()} {wo.unit}
                      </td>
                      <td className="px-4 py-3">
                        <ProgressBar value={Number(wo.actual_qty)} max={Number(wo.planned_qty)} />
                      </td>
                      <td className="px-4 py-3 text-xs text-muted-foreground">
                        {new Date(wo.planned_start).toLocaleDateString('ko-KR')}
                      </td>
                      <td className="px-4 py-3">
                        {wo.status === 'PLANNED' && (
                          <button
                            onClick={() => handleStart(wo.id)}
                            className="text-xs px-2 py-1 rounded border border-primary text-primary hover:bg-primary hover:text-primary-foreground transition-colors"
                          >
                            작업 시작
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
