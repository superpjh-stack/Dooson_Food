'use client'

import { useQuery } from '@tanstack/react-query'
import { TopBar } from '@/components/layout/TopBar'
import { apiClient } from '@/lib/api/client'

interface HaccpCheckPlan {
  id: string
  ccp_id: string
  check_frequency: string
  responsible_person: string
  is_active: boolean
}

interface HaccpCheckRecord {
  id: string
  plan_id: string
  lot_id: string | null
  checked_at: string
  result: 'PASS' | 'FAIL' | 'CONDITIONAL_PASS'
  checked_by: string
  notes: string | null
}

const RESULT_STYLES: Record<string, string> = {
  PASS: 'bg-success-bg text-success border-success/30',
  FAIL: 'bg-critical-bg text-critical border-critical/30',
  CONDITIONAL_PASS: 'bg-warning-bg text-warning border-warning/30',
}

const RESULT_LABEL: Record<string, string> = {
  PASS: '합격',
  FAIL: '불합격',
  CONDITIONAL_PASS: '조건부 합격',
}

function ResultBadge({ result }: { result: string }) {
  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium border ${RESULT_STYLES[result] ?? ''}`}>
      {RESULT_LABEL[result] ?? result}
    </span>
  )
}

export default function HaccpPage() {
  const { data: plans, isLoading: plansLoading } = useQuery({
    queryKey: ['haccp-plans'],
    queryFn: async () => {
      const { data } = await apiClient.get<HaccpCheckPlan[]>('/api/v1/haccp/check-plans')
      return data
    },
  })

  const { data: records, isLoading: recordsLoading } = useQuery({
    queryKey: ['haccp-records'],
    queryFn: async () => {
      const { data } = await apiClient.get<HaccpCheckRecord[]>('/api/v1/haccp/check-records', {
        params: { limit: 20 },
      })
      return data
    },
  })

  return (
    <div className="flex flex-col min-h-full">
      <TopBar title="HACCP / 식품안전" />
      <div className="flex-1 p-6 space-y-8">
        <section>
          <h2 className="text-sm font-semibold text-muted-foreground mb-3">점검 계획</h2>
          <div className="rounded-lg border bg-card shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/40">
                  <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">CCP ID</th>
                  <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">점검주기</th>
                  <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">담당자</th>
                  <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">활성여부</th>
                </tr>
              </thead>
              <tbody>
                {plansLoading ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-sm text-muted-foreground">로딩 중...</td>
                  </tr>
                ) : !plans || plans.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-sm text-muted-foreground">등록된 점검 계획이 없습니다</td>
                  </tr>
                ) : plans.map((plan) => (
                  <tr key={plan.id} className="border-b last:border-0 hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs">{plan.ccp_id.slice(0, 8)}...</td>
                    <td className="px-4 py-3 text-muted-foreground">{plan.check_frequency}</td>
                    <td className="px-4 py-3">{plan.responsible_person}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium border ${plan.is_active ? 'bg-success-bg text-success border-success/30' : 'bg-muted text-muted-foreground border-border'}`}>
                        {plan.is_active ? '활성' : '비활성'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section>
          <h2 className="text-sm font-semibold text-muted-foreground mb-3">최근 점검 기록</h2>
          <div className="rounded-lg border bg-card shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/40">
                  <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">점검일시</th>
                  <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">결과</th>
                  <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">검사자</th>
                  <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">LOT</th>
                  <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">비고</th>
                </tr>
              </thead>
              <tbody>
                {recordsLoading ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-sm text-muted-foreground">로딩 중...</td>
                  </tr>
                ) : !records || records.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-sm text-muted-foreground">점검 기록이 없습니다</td>
                  </tr>
                ) : records.map((rec) => (
                  <tr
                    key={rec.id}
                    className={`border-b last:border-0 hover:bg-muted/20 transition-colors ${rec.result === 'FAIL' ? 'bg-critical-bg' : ''}`}
                  >
                    <td className="px-4 py-3 text-xs">
                      {new Date(rec.checked_at).toLocaleString('ko-KR')}
                    </td>
                    <td className="px-4 py-3">
                      <ResultBadge result={rec.result} />
                    </td>
                    <td className="px-4 py-3">{rec.checked_by}</td>
                    <td className="px-4 py-3 font-mono text-xs">{rec.lot_id ? rec.lot_id.slice(0, 8) + '...' : '-'}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{rec.notes ?? '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  )
}
