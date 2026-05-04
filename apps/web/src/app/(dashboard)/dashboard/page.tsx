'use client'

import { TopBar } from '@/components/layout/TopBar'
import { KpiCard } from '@/components/kpi/KpiCard'
import { AlertItem } from '@/components/alerts/AlertItem'
import { LotStatusBadge } from '@/components/lot/LotStatusBadge'
import { useWorkOrders } from '@/hooks/use-work-orders'
import { useNotifications } from '@/hooks/use-notifications'
import type { WorkOrderStatus } from '@/lib/api/types'

const STATUS_LABEL: Record<WorkOrderStatus, string> = {
  PLANNED: '계획',
  IN_PROGRESS: '진행 중',
  COMPLETED: '완료',
  CANCELLED: '취소',
}

function WorkOrderStatusBadge({ status }: { status: WorkOrderStatus }) {
  const colorMap: Record<WorkOrderStatus, string> = {
    PLANNED: 'bg-info-bg text-info border-info/30',
    IN_PROGRESS: 'bg-warning-bg text-warning border-warning/30',
    COMPLETED: 'bg-success-bg text-success border-success/30',
    CANCELLED: 'bg-muted text-muted-foreground border-border',
  }
  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium border ${colorMap[status]}`}>
      {STATUS_LABEL[status]}
    </span>
  )
}

function ProgressBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0
  return (
    <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
      <div
        className="h-full rounded-full bg-primary transition-all"
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}


export default function DashboardPage() {
  const today = new Date().toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  })

  const { data: workOrderData, isLoading: woLoading } = useWorkOrders()
  const workOrders = workOrderData?.items ?? []

  const { data: notificationsData, isLoading: notifLoading } = useNotifications(10)
  const notifications = notificationsData ?? []

  const severityMap: Record<'CRITICAL' | 'WARNING' | 'INFO', 'critical' | 'warning' | 'info'> = {
    CRITICAL: 'critical',
    WARNING: 'warning',
    INFO: 'info',
  }

  return (
    <div className="flex flex-col min-h-full">
      <TopBar title="대시보드" subtitle={today} />

      <div className="flex-1 p-6 space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <KpiCard
            label="생산 달성률"
            value="87.3"
            unit="%"
            delta={2.1}
            deltaLabel="vs 어제"
            icon="🏭"
            color="blue"
          />
          <KpiCard
            label="OEE"
            value="82.5"
            unit="%"
            delta={-0.8}
            deltaLabel="vs 어제"
            icon="⚙"
            color="green"
          />
          <KpiCard
            label="품질 합격률"
            value="99.1"
            unit="%"
            delta={0.3}
            deltaLabel="vs 어제"
            icon="✓"
            color="green"
          />
          <KpiCard
            label="가동 설비"
            value="14"
            unit="/ 16"
            icon="🔧"
            color="cyan"
          />
          <KpiCard
            label="금일 생산량"
            value="4,280"
            unit="EA"
            delta={5.2}
            deltaLabel="vs 목표"
            icon="📦"
            color="orange"
          />
        </div>

        {/* Today's Work Orders */}
        <section>
          <h2 className="text-sm font-semibold text-muted-foreground mb-3">오늘의 생산지시</h2>
          <div className="rounded-lg border bg-card shadow-sm overflow-hidden">
            {woLoading ? (
              <div className="p-8 text-center text-sm text-muted-foreground">로딩 중...</div>
            ) : workOrders.length === 0 ? (
              // Fallback mock data while backend is not seeded
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/40">
                    <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">생산지시 코드</th>
                    <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">제품명</th>
                    <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">상태</th>
                    <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">진행률</th>
                    <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">계획/실적</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { code: 'WO-20260504-0001', product: '순살 닭가슴살 HMR 200g', status: 'IN_PROGRESS' as WorkOrderStatus, planned: 1200, actual: 820 },
                    { code: 'WO-20260504-0002', product: '현미밥 도시락 350g', status: 'PLANNED' as WorkOrderStatus, planned: 800, actual: 0 },
                    { code: 'WO-20260504-0003', product: '불고기 덮밥 450g', status: 'COMPLETED' as WorkOrderStatus, planned: 600, actual: 612 },
                  ].map((wo) => (
                    <tr key={wo.code} className="border-b last:border-0 hover:bg-muted/20 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs">{wo.code}</td>
                      <td className="px-4 py-3">{wo.product}</td>
                      <td className="px-4 py-3">
                        <WorkOrderStatusBadge status={wo.status} />
                      </td>
                      <td className="px-4 py-3 w-32">
                        <ProgressBar value={wo.actual} max={wo.planned} />
                      </td>
                      <td className="px-4 py-3 text-right tabular-nums text-xs">
                        {wo.actual.toLocaleString()} / {wo.planned.toLocaleString()} EA
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/40">
                    <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">생산지시 코드</th>
                    <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">상태</th>
                    <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">진행률</th>
                    <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">계획/실적</th>
                  </tr>
                </thead>
                <tbody>
                  {workOrders.map((wo) => (
                    <tr key={wo.id} className="border-b last:border-0 hover:bg-muted/20 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs">{wo.code}</td>
                      <td className="px-4 py-3">
                        <WorkOrderStatusBadge status={wo.status} />
                      </td>
                      <td className="px-4 py-3 w-32">
                        <ProgressBar value={Number(wo.actual_qty)} max={Number(wo.planned_qty)} />
                      </td>
                      <td className="px-4 py-3 text-right tabular-nums text-xs">
                        {Number(wo.actual_qty).toLocaleString()} / {Number(wo.planned_qty).toLocaleString()} {wo.unit}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>

        {/* Recent Quality Alerts */}
        <section>
          <h2 className="text-sm font-semibold text-muted-foreground mb-3">최근 품질 알림</h2>
          <div>
            {notifLoading ? (
              <div className="animate-pulse space-y-2">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="h-12 rounded bg-border" />
                ))}
              </div>
            ) : notifications.length === 0 ? (
              <p className="text-sm text-muted-foreground py-4 text-center">최근 알림이 없습니다</p>
            ) : (
              notifications.map((notif) => (
                <AlertItem
                  key={notif.id}
                  severity={severityMap[notif.severity] ?? 'info'}
                  title={notif.title}
                  body={notif.body}
                  time={new Date(notif.created_at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
                />
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
