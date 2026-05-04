'use client'

import { useQuery } from '@tanstack/react-query'
import { TopBar } from '@/components/layout/TopBar'
import { StatusDot } from '@/components/ui/status-dot'
import { ProgressBar } from '@/components/ui/progress-bar'
import { AlertItem } from '@/components/alerts/AlertItem'
import { apiClient } from '@/lib/api/client'
import type { Equipment, PaginatedResponse } from '@/lib/api/types'

type EquipmentStatusDot = 'running' | 'idle' | 'maintenance' | 'fault' | 'offline'

function toStatusDot(status: Equipment['status']): EquipmentStatusDot {
  const map: Record<Equipment['status'], EquipmentStatusDot> = {
    RUNNING: 'running',
    IDLE: 'idle',
    FAULT: 'fault',
    MAINTENANCE: 'maintenance',
  }
  return map[status] ?? 'offline'
}

function oeeColor(oee: number): 'success' | 'primary' | 'warning' {
  if (oee >= 85) return 'success'
  if (oee >= 60) return 'primary'
  return 'warning'
}

export default function EquipmentPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['equipment'],
    queryFn: async () => {
      const { data } = await apiClient.get<PaginatedResponse<Equipment>>('/api/v1/equipment')
      return data
    },
  })

  const equipmentList = data?.items ?? []
  const faultItems = equipmentList.filter((e) => e.status === 'FAULT')

  return (
    <div className="flex flex-col min-h-full">
      <TopBar title="설비관리" />
      <div className="flex-1 p-6 space-y-4">
        {faultItems.length > 0 && (
          <div>
            {faultItems.map((e) => (
              <AlertItem
                key={e.id}
                severity="warning"
                title={`설비 고장: ${e.name}`}
                body={`${e.code} — 즉각적인 점검이 필요합니다`}
              />
            ))}
          </div>
        )}

        {isLoading ? (
          <div className="grid grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-lg border bg-card p-4 space-y-3">
                <div className="animate-pulse bg-border h-4 rounded w-3/4" />
                <div className="animate-pulse bg-border h-3 rounded w-1/2" />
                <div className="animate-pulse bg-border h-2 rounded w-full" />
              </div>
            ))}
          </div>
        ) : equipmentList.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-12">
            등록된 설비가 없습니다
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {equipmentList.map((equip) => {
              const oee = equip.oee ?? 0
              return (
                <div key={equip.id} className="rounded-lg border bg-card p-4 space-y-3 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-semibold text-sm">{equip.name}</p>
                      <p className="text-xs text-muted-foreground font-mono">{equip.code}</p>
                    </div>
                    <StatusDot status={toStatusDot(equip.status)} className="text-xs" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                      <span>OEE</span>
                      <span className="font-semibold tabular-nums">{oee}%</span>
                    </div>
                    <ProgressBar value={oee} max={100} color={oeeColor(oee)} />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    마지막 유지보수:{' '}
                    {equip.last_maintained_at
                      ? new Date(equip.last_maintained_at).toLocaleDateString('ko-KR')
                      : '-'}
                  </p>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
