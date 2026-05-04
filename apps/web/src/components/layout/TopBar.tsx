import { cn } from '@/lib/utils'

interface TopBarProps {
  title: string
  subtitle?: string
  actions?: React.ReactNode
  className?: string
}

export function TopBar({ title, subtitle, actions, className }: TopBarProps) {
  return (
    <header
      className={cn(
        'h-14 flex items-center justify-between px-6 border-b border-border bg-card sticky top-0 z-10',
        className
      )}
    >
      <div>
        <h1 className="text-base font-semibold leading-none">{title}</h1>
        {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </header>
  )
}
