'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'

interface NavItem {
  href: string
  label: string
  icon: string
}

const NAV_ITEMS: NavItem[] = [
  { href: '/dashboard',        label: '대시보드',       icon: '📊' },
  { href: '/production',       label: '생산관리',       icon: '🏭' },
  { href: '/production/lines', label: '생산라인',       icon: '🔧' },
  { href: '/products',         label: '제품/BOM',       icon: '📦' },
  { href: '/quality/ccp',      label: 'CCP 품질관리',   icon: '🌡' },
  { href: '/quality/xray',     label: 'X-Ray 검사',     icon: '🔍' },
  { href: '/haccp',            label: 'HACCP/식품안전', icon: '🛡' },
  { href: '/lots',             label: 'LOT 추적',       icon: '🔗' },
  { href: '/equipment',        label: '설비관리',       icon: '⚙' },
  { href: '/ai-hub',           label: 'AI Agent Hub',   icon: '🤖' },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-56 flex-shrink-0 bg-sidebar flex flex-col h-screen sticky top-0">
      {/* Logo */}
      <div className="h-14 flex items-center px-4 border-b border-white/10">
        <span className="text-white font-bold text-base tracking-tight">두손푸드 AI-MES</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + '/')
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-2.5 mx-2 rounded-md text-sm transition-colors',
                active
                  ? 'bg-primary/20 text-white font-medium'
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              )}
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-white/10">
        <p className="text-[11px] text-white/30 text-center">v0.1.0 · AI-MES</p>
      </div>
    </aside>
  )
}
