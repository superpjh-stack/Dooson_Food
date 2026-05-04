import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { AiConfidenceBar } from '@/components/ai/AiConfidenceBar'

type CcpResult = 'PASS' | 'FAIL' | 'WARNING' | 'PENDING'

interface CcpStatusCardProps {
  ccpName: string
  ccpCode: string
  measuredValue: number
  unit: string
  limitMin?: number
  limitMax?: number
  result: CcpResult
  measuredAt?: string
  aiConfidence?: number
  aiModel?: string
  className?: string
}

const RESULT_CONFIG: Record<CcpResult, { variant: 'success' | 'critical' | 'warning' | 'muted'; label: string }> = {
  PASS:    { variant: 'success',  label: '적합' },
  FAIL:    { variant: 'critical', label: '부적합' },
  WARNING: { variant: 'warning',  label: '경고' },
  PENDING: { variant: 'muted',    label: '대기' },
}

export function CcpStatusCard({
  ccpName,
  ccpCode,
  measuredValue,
  unit,
  limitMin,
  limitMax,
  result,
  measuredAt,
  aiConfidence,
  aiModel,
  className,
}: CcpStatusCardProps) {
  const config = RESULT_CONFIG[result]
  const isFail = result === 'FAIL'

  return (
    <div
      className={cn(
        'rounded-lg border bg-card p-4 shadow-sm',
        isFail && 'border-critical/50 bg-critical-bg',
        className
      )}
    >
      <div className="flex items-start justify-between mb-2">
        <div>
          <p className="text-xs text-muted-foreground">{ccpCode}</p>
          <p className="text-sm font-semibold">{ccpName}</p>
        </div>
        <Badge variant={config.variant}>{config.label}</Badge>
      </div>

      <div className="flex items-baseline gap-1 my-2">
        <span className={cn('text-2xl font-bold tabular-nums', isFail && 'text-critical')}>
          {measuredValue.toFixed(1)}
        </span>
        <span className="text-sm text-muted-foreground">{unit}</span>
      </div>

      {(limitMin !== undefined || limitMax !== undefined) && (
        <p className="text-[11px] text-muted-foreground mb-2">
          허용 범위: {limitMin ?? '–'} ~ {limitMax ?? '–'} {unit}
        </p>
      )}

      {aiConfidence !== undefined && (
        <AiConfidenceBar confidence={aiConfidence} modelName={aiModel} />
      )}

      {measuredAt && (
        <p className="text-[11px] text-muted-foreground/70 mt-1">{measuredAt}</p>
      )}
    </div>
  )
}
