import { cn } from '@/lib/utils'

interface ProgressBarProps {
  value: number
  max?: number
  className?: string
  showLabel?: boolean
  color?: 'primary' | 'success' | 'warning' | 'critical'
}

const COLOR_STYLES = {
  primary: 'bg-primary',
  success: 'bg-success',
  warning: 'bg-warning',
  critical: 'bg-critical',
}

export function ProgressBar({ value, max = 100, className, showLabel = false, color = 'primary' }: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  const displayColor = pct >= 80 ? 'success' : pct >= 40 ? (color === 'primary' ? 'primary' : color) : 'warning'

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="flex-1 h-2 bg-border rounded-full overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-500', COLOR_STYLES[displayColor])}
          style={{ width: `${pct}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-xs font-semibold text-foreground w-10 text-right">
          {pct.toFixed(0)}%
        </span>
      )}
    </div>
  )
}
