import { cn } from '@/lib/utils'

type Severity = 'critical' | 'warning' | 'info'

interface AlertItemProps {
  severity: Severity
  title: string
  body: string
  time?: string
  action?: React.ReactNode
  className?: string
}

const SEVERITY_STYLES: Record<Severity, { container: string; border: string; icon: string }> = {
  critical: {
    container: 'bg-critical-bg',
    border: 'border-l-critical',
    icon: '🚨',
  },
  warning: {
    container: 'bg-warning-bg',
    border: 'border-l-warning',
    icon: '⚠',
  },
  info: {
    container: 'bg-info-bg',
    border: 'border-l-info',
    icon: 'ℹ',
  },
}

export function AlertItem({ severity, title, body, time, action, className }: AlertItemProps) {
  const styles = SEVERITY_STYLES[severity]

  return (
    <div
      className={cn(
        'flex items-start gap-3 p-3 rounded-sm border-l-[3px] mb-2',
        styles.container,
        styles.border,
        className
      )}
    >
      <span className="text-base mt-0.5 flex-shrink-0">{styles.icon}</span>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold">{title}</p>
        <p className="text-xs text-muted-foreground mt-0.5">{body}</p>
        <div className="flex items-center gap-3 mt-1">
          {time && <span className="text-[11px] text-muted-foreground">{time}</span>}
          {action}
        </div>
      </div>
    </div>
  )
}
