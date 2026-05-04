import { cn } from '@/lib/utils'
import { LotStatusBadge, LotTypeBadge } from './LotStatusBadge'

type LotStatus = 'ACTIVE' | 'ON_HOLD' | 'CONSUMED' | 'SHIPPED' | 'RECALLED'
type LotType = 'RAW' | 'WIP' | 'FG'

interface LotNode {
  lotId: string
  lotCode: string
  productName: string
  type: LotType
  status: LotStatus
  qty: number
  unit: string
  depth: number
  children?: LotNode[]
}

interface LotTreeProps {
  root: LotNode
  className?: string
}

function LotNodeRow({ node }: { node: LotNode }) {
  const isHold = node.status === 'ON_HOLD' || node.status === 'RECALLED'
  return (
    <li>
      <div
        className={cn(
          'flex items-center gap-2 py-1.5 px-2 rounded text-sm',
          isHold && 'bg-critical-bg'
        )}
        style={{ paddingLeft: `${8 + node.depth * 20}px` }}
      >
        {node.depth > 0 && (
          <span className="text-muted-foreground/40 text-xs select-none">└</span>
        )}
        <LotTypeBadge type={node.type} />
        <span className="font-mono text-xs text-muted-foreground">{node.lotCode}</span>
        <span className="text-xs flex-1 truncate">{node.productName}</span>
        <span className="text-xs text-muted-foreground tabular-nums">
          {node.qty.toLocaleString()} {node.unit}
        </span>
        <LotStatusBadge status={node.status} />
      </div>
      {node.children && node.children.length > 0 && (
        <ul>
          {node.children.map((child) => (
            <LotNodeRow key={child.lotId} node={child} />
          ))}
        </ul>
      )}
    </li>
  )
}

export function LotTree({ root, className }: LotTreeProps) {
  return (
    <div className={cn('rounded-lg border bg-card p-3', className)}>
      <ul>
        <LotNodeRow node={root} />
      </ul>
    </div>
  )
}
