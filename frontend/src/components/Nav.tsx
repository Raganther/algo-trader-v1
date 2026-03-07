'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { BarChart2, TrendingUp } from 'lucide-react'

const links = [
  { href: '/', label: 'Strategy Lab', icon: BarChart2 },
  { href: '/chart', label: 'Price Action', icon: TrendingUp },
]

export default function Nav() {
  const pathname = usePathname()

  return (
    <aside className="fixed top-0 left-0 h-screen w-52 bg-[#0d0d0d] border-r border-white/5 flex flex-col z-10">
      <div className="px-5 py-5 border-b border-white/5">
        <p className="text-xs font-bold text-gray-600 uppercase tracking-widest">Algo Trader</p>
        <p className="text-white font-semibold text-sm mt-0.5">Research Lab</p>
      </div>

      <nav className="flex-1 p-3 space-y-0.5">
        {links.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== '/' && pathname.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                active
                  ? 'bg-white/5 text-white font-medium'
                  : 'text-gray-500 hover:text-gray-200 hover:bg-white/[0.03]'
              }`}
            >
              <Icon size={16} className={active ? 'text-violet-400' : 'text-gray-600'} />
              {label}
            </Link>
          )
        })}
      </nav>

      <div className="px-5 py-4 border-t border-white/5">
        <p className="text-xs text-gray-700">Paper trading</p>
        <div className="flex items-center gap-1.5 mt-1">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
          <p className="text-xs text-gray-500">4 bots live</p>
        </div>
      </div>
    </aside>
  )
}
