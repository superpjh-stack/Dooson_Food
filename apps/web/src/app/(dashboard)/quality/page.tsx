'use client'

import { TopBar } from '@/components/layout/TopBar'
import { CcpStatusCard } from '@/components/quality/CcpStatusCard'
import { FValueChart } from '@/components/charts/FValueChart'
import { useCcpRecords } from '@/hooks/use-ccp-records'

const MOCK_CCP_CARDS = [
  {
    id: 'mock-1',
    ccpCode: 'CCP-1',
    ccpName: '살균 온도',
    measuredValue: 121.8,
    unit: '°C',
    limitMin: 121,
    limitMax: 135,
    result: 'PASS' as const,
    measuredAt: '2026-05-04 14:00',
    aiConfidence: 0.97,
    aiModel: 'TempNet v2',
  },
  {
    id: 'mock-2',
    ccpCode: 'CCP-2',
    ccpName: 'F값',
    measuredValue: 12.4,
    unit: 'min',
    limitMin: 10,
    limitMax: undefined,
    result: 'PASS' as const,
    measuredAt: '2026-05-04 14:10',
    aiConfidence: 0.91,
    aiModel: 'FValueNet v1',
  },
  {
    id: 'mock-3',
    ccpCode: 'CCP-3',
    ccpName: '살균 온도 (2호기)',
    measuredValue: 119.2,
    unit: '°C',
    limitMin: 121,
    limitMax: 135,
    result: 'FAIL' as const,
    measuredAt: '2026-05-04 14:22',
    aiConfidence: 0.88,
    aiModel: 'TempNet v2',
  },
  {
    id: 'mock-4',
    ccpCode: 'CCP-4',
    ccpName: '금속 검출 (X-Ray)',
    measuredValue: 0,
    unit: 'mm',
    limitMin: undefined,
    limitMax: 0.5,
    result: 'PASS' as const,
    measuredAt: '2026-05-04 13:55',
    aiConfidence: 0.99,
    aiModel: 'XRayNet v3',
  },
]

const FVALUE_SAMPLE_DATA = [
  { time: '08:00', actual: 115.2, predicted: 114.8 },
  { time: '08:10', actual: 118.5, predicted: 118.0 },
  { time: '08:20', actual: 120.9, predicted: 120.5 },
  { time: '08:30', actual: 121.8, predicted: 121.6 },
  { time: '08:40', actual: 122.1, predicted: 122.0 },
  { time: '08:50', actual: 121.9, predicted: 121.8 },
  { time: '09:00', actual: 122.3, predicted: 122.1 },
  { time: '09:10', actual: 121.7, predicted: 121.5 },
  { time: '09:20', actual: 121.4, predicted: 121.3 },
  { time: '09:30', actual: 120.8, predicted: 120.6 },
  { time: '09:40', actual: 119.5, predicted: 119.8 },
  { time: '09:50', actual: 117.2, predicted: 118.0 },
]

function SkeletonCard() {
  return (
    <div className="rounded-lg border bg-card p-4 animate-pulse space-y-3">
      <div className="h-3 bg-muted rounded w-1/4" />
      <div className="h-4 bg-muted rounded w-1/2" />
      <div className="h-8 bg-muted rounded w-1/3" />
    </div>
  )
}

export default function QualityPage() {
  const { data: ccpRecords, isLoading } = useCcpRecords()

  // Determine if we should render live data or mock data
  const useLiveData = !isLoading && ccpRecords && ccpRecords.length > 0

  return (
    <div className="flex flex-col min-h-full">
      <TopBar title="품질관리 — CCP / F값 / X-Ray" />

      <div className="flex-1 p-6 space-y-6">
        {/* CCP Status Grid */}
        <section>
          <h2 className="text-sm font-semibold text-muted-foreground mb-3">CCP 점검 현황</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
            ) : useLiveData ? (
              ccpRecords.map((record) => (
                <CcpStatusCard
                  key={record.id}
                  ccpCode={record.ccp_id}
                  ccpName="CCP 측정"
                  measuredValue={Number(record.measured_value)}
                  unit=""
                  result={record.is_deviation ? 'FAIL' : 'PASS'}
                  measuredAt={new Date(record.measured_at).toLocaleString('ko-KR')}
                />
              ))
            ) : (
              MOCK_CCP_CARDS.map((card) => (
                <CcpStatusCard
                  key={card.id}
                  ccpCode={card.ccpCode}
                  ccpName={card.ccpName}
                  measuredValue={card.measuredValue}
                  unit={card.unit}
                  limitMin={card.limitMin}
                  limitMax={card.limitMax}
                  result={card.result}
                  measuredAt={card.measuredAt}
                  aiConfidence={card.aiConfidence}
                  aiModel={card.aiModel}
                />
              ))
            )}
          </div>
        </section>

        {/* F-Value Chart */}
        <section>
          <div className="rounded-lg border bg-card p-4 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-sm font-semibold">F값 온도 프로파일</h2>
                <p className="text-xs text-muted-foreground">살균기 STR-001 — 오늘 08:00 ~ 09:50</p>
              </div>
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <span className="inline-block w-3 h-0.5 bg-primary" /> 실측
                </span>
                <span className="flex items-center gap-1">
                  <span className="inline-block w-3 h-0.5 bg-accent border-dashed" /> AI 예측
                </span>
              </div>
            </div>
            <FValueChart data={FVALUE_SAMPLE_DATA} threshold={121} targetFValue={10} height={220} />
          </div>
        </section>
      </div>
    </div>
  )
}
