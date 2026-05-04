import { cn } from '@/lib/utils'

type EquipmentStatus = 'running' | 'idle' | 'maintenance' | 'fault' | 'offline'

interface StatusDotProps {
  status: EquipmentStatus
  className?: string
}

const STATUS_STYLES: Record<EquipmentStatus, string> = {
  running: 'bg-success animate-pulse-dot',
  idle: 'bg-muted-foreground',
  maintenance: 'bg-warning',
  fault: 'bg-critical',
  offline: 'bg-muted-foreground/40',
}

const STATUS_LABEL: Record<EquipmentStatus, string> = {
  running: '정상 가동',
  idle: '대기',
  maintenance: '정비 중',
  fault: '고장',
  offline: '오프라인',
}

export function StatusDot({ status, className }: StatusDotProps) {
  return (
    <span className={cn('flex items-center gap-1.5 text-sm', className)}>
      <span className={cn('inline-block w-2 h-2 rounded-full flex-shrink-0', STATUS_STYLES[status])} />
      {STATUS_LABEL[status]}
    </span>
  )
}
