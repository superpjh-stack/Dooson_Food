'use client'

import { cn, getConfidenceLevel } from '@/lib/utils'

interface AiConfidenceBarProps {
  confidence: number        // 0~1
  modelName?: string        // 'LSTM-v2', 'XGBoost-CCP-v1'
  source?: string           // RAG 출처 문서명
  predictedAt?: string
  className?: string
}

/**
 * CONVENTIONS 필수 규칙:
 * - confidence < 0.6 → 렌더링하지 않음
 * - 반드시 modelName 또는 source 함께 표시
 */
export function AiConfidenceBar({
  confidence,
  modelName,
  source,
  predictedAt,
  className,
}: AiConfidenceBarProps) {
  const level = getConfidenceLevel(confidence)

  // 신뢰도 0.6 미만 → 표시하지 않음 (CONVENTIONS 규칙)
  if (level === 'hidden') return null

  const pct = Math.round(confidence * 100)
  const barColor =
    level === 'high' ? 'bg-accent' : 'bg-warning'
  const textColor =
    level === 'high' ? 'text-accent confidence-high' : 'text-warning confidence-medium'

  return (
    <div className={cn('flex items-center gap-2 text-xs text-muted-foreground', className)}>
      <span>AI</span>
      <div className="flex-1 h-1 bg-border rounded-full overflow-hidden min-w-[40px]">
        <div className={cn('h-full rounded-full', barColor)} style={{ width: `${pct}%` }} />
      </div>
      <span className={cn('font-semibold tabular-nums', textColor)}>{pct}%</span>
      {(modelName || source) && (
        <span className="text-muted-foreground/70 truncate max-w-[140px]">
          · {source ?? modelName}
        </span>
      )}
    </div>
  )
}
