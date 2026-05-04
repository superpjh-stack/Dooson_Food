import { cn } from '@/lib/utils'

type KpiColor = 'green' | 'blue' | 'orange' | 'red' | 'cyan'

interface KpiCardProps {
  label: string
  value: number | string
  unit?: string
  delta?: number
  deltaLabel?: string
  icon?: string
  color?: KpiColor
  className?: string
}

const BAR_COLORS: Record<KpiColor, string> = {
  green:  'bg-secondary',
  blue:   'bg-primary',
  orange: 'bg-warning',
  red:    'bg-critical',
  cyan:   'bg-accent',
}

export function KpiCard({
  label,
  value,
  unit,
  delta,
  deltaLabel,
  icon,
  color = 'blue',
  className,
}: KpiCardProps) {
  const isUp = delta !== undefined && delta > 0
  const isDown = delta !== undefined && delta < 0

  return (
    <div
      className={cn(
        'relative rounded-lg border border-border bg-card px-5 pt-5 pb-4 shadow-sm overflow-hidden',
        className
      )}
    >
      {/* 상단 컬러 바 */}
      <div className={cn('absolute top-0 left-0 right-0 h-[3px]', BAR_COLORS[color])} />

      {/* 아이콘 */}
      {icon && (
        <span className="absolute right-4 top-4 text-3xl opacity-10 select-none">{icon}</span>
      )}

      <p className="text-xs font-medium text-muted-foreground mb-1">{label}</p>
      <div className="flex items-baseline gap-1">
        <span className="text-3xl font-bold tabular-nums leading-none">{value}</span>
        {unit && <span className="text-sm text-muted-foreground">{unit}</span>}
      </div>

      {delta !== undefined && (
        <p
          className={cn(
            'mt-1.5 text-xs font-medium',
            isUp && 'text-success',
            isDown && 'text-critical',
            !isUp && !isDown && 'text-muted-foreground'
          )}
        >
          {isUp ? '▲' : isDown ? '▼' : '—'}{' '}
          {Math.abs(delta).toFixed(1)}%{deltaLabel ? ` ${deltaLabel}` : ''}
        </p>
      )}
    </div>
  )
}
