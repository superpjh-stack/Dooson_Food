import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

type LotStatus = 'ACTIVE' | 'ON_HOLD' | 'CONSUMED' | 'SHIPPED' | 'RECALLED'
type LotType = 'RAW' | 'WIP' | 'FG'

interface LotStatusBadgeProps {
  status: LotStatus
  className?: string
}

interface LotTypeBadgeProps {
  type: LotType
  className?: string
}

const STATUS_CONFIG: Record<LotStatus, { variant: 'success' | 'critical' | 'warning' | 'muted' | 'info'; label: string }> = {
  ACTIVE:   { variant: 'success',  label: '활성' },
  ON_HOLD:  { variant: 'critical', label: '보류' },
  CONSUMED: { variant: 'muted',    label: '소비됨' },
  SHIPPED:  { variant: 'info',     label: '출하' },
  RECALLED: { variant: 'critical', label: '회수' },
}

const TYPE_STYLES: Record<LotType, string> = {
  RAW: 'bg-info-bg text-info border-info/30',
  WIP: 'bg-warning-bg text-warning border-warning/30',
  FG:  'bg-success-bg text-success border-success/30',
}

const TYPE_LABEL: Record<LotType, string> = {
  RAW: '원자재',
  WIP: '반제품',
  FG:  '완제품',
}

export function LotStatusBadge({ status, className }: LotStatusBadgeProps) {
  const config = STATUS_CONFIG[status]
  return (
    <Badge variant={config.variant} className={className}>
      {status === 'ON_HOLD' && '⚠ '}
      {status === 'RECALLED' && '🚨 '}
      {config.label}
    </Badge>
  )
}

export function LotTypeBadge({ type, className }: LotTypeBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded px-1.5 py-0.5 text-[10px] font-bold border',
        TYPE_STYLES[type],
        className
      )}
    >
      {TYPE_LABEL[type]}
    </span>
  )
}
