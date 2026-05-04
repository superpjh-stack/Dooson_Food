'use client'

import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { TopBar } from '@/components/layout/TopBar'
import { LotStatusBadge, LotTypeBadge } from '@/components/lot/LotStatusBadge'
import { lotService } from '@/services/lot.service'

export default function LotsPage() {
  const router = useRouter()
  const { data, isLoading } = useQuery({
    queryKey: ['lots'],
    queryFn: () => lotService.list(),
  })

  const lots = data?.items ?? []

  return (
    <div className="flex flex-col min-h-full">
      <TopBar title="LOT 관리" />
      <div className="flex-1 p-6">
        <div className="rounded-lg border bg-card shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/40">
                <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">LOT 코드</th>
                <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">유형</th>
                <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">상태</th>
                <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">수량</th>
                <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">단위</th>
                <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">생산일</th>
              </tr>
            </thead>
            <tbody>
              {isLoading
                ? Array.from({ length: 3 }).map((_, i) => (
                    <tr key={i} className="border-b">
                      {Array.from({ length: 6 }).map((_, j) => (
                        <td key={j} className="px-4 py-3">
                          <div className="animate-pulse bg-border h-4 rounded w-full" />
                        </td>
                      ))}
                    </tr>
                  ))
                : lots.length === 0
                ? (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-sm text-muted-foreground">
                        등록된 LOT가 없습니다
                      </td>
                    </tr>
                  )
                : lots.map((lot) => (
                    <tr
                      key={lot.id}
                      className="border-b last:border-0 hover:bg-muted/20 transition-colors cursor-pointer"
                      onClick={() => router.push(`/lots/${lot.id}/trace`)}
                    >
                      <td className="px-4 py-3 font-mono text-xs">{lot.code}</td>
                      <td className="px-4 py-3">
                        <LotTypeBadge type={lot.type} />
                      </td>
                      <td className="px-4 py-3">
                        <LotStatusBadge status={lot.status} />
                      </td>
                      <td className="px-4 py-3 text-right tabular-nums">{Number(lot.qty).toLocaleString()}</td>
                      <td className="px-4 py-3 text-muted-foreground">{lot.unit}</td>
                      <td className="px-4 py-3 text-muted-foreground text-xs">
                        {lot.produced_at
                          ? new Date(lot.produced_at).toLocaleDateString('ko-KR')
                          : '-'}
                      </td>
                    </tr>
                  ))}
            </tbody>
          </table>
        </div>
        {data && (
          <p className="mt-2 text-xs text-muted-foreground">
            총 {data.total.toLocaleString()}건
          </p>
        )}
      </div>
    </div>
  )
}
