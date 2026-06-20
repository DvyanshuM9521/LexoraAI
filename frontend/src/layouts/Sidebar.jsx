import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, FileText, Zap, Scale, GitCompare,
  MessageSquare, FileDown, ChevronRight, Sparkles
} from 'lucide-react'
import clsx from 'clsx'

const NAV_ITEMS = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard', exact: true },
  { to: '/contracts', icon: FileText, label: 'Contracts' },
  { to: '/analysis', icon: Zap, label: 'Analysis' },
  { to: '/comparison', icon: GitCompare, label: 'Comparison' },
  { to: '/assistant', icon: MessageSquare, label: 'AI Assistant' },
  { to: '/reports', icon: FileDown, label: 'Reports' },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 h-screen bg-slate-900/95 backdrop-blur-xl border-r border-slate-800/80 flex flex-col fixed left-0 top-0 z-40">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/30">
            <Scale className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-100 tracking-wide">LEXORA AI</p>
            <p className="text-[10px] text-slate-500 font-medium tracking-wider uppercase">Contract Intelligence</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p className="section-label px-3 mb-3">Platform</p>
        {NAV_ITEMS.map(({ to, icon: Icon, label, exact }) => {
          const isActive = exact
            ? location.pathname === to
            : location.pathname.startsWith(to)

          return (
            <NavLink
              key={to}
              to={to}
              className={clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group',
                isActive
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
              )}
            >
              <Icon className={clsx('w-4 h-4 flex-shrink-0', isActive ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-400')} />
              <span>{label}</span>
              {isActive && <ChevronRight className="w-3 h-3 ml-auto text-indigo-400/60" />}
            </NavLink>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-slate-800/80">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-indigo-600/10 border border-indigo-500/20">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <div>
            <p className="text-xs font-semibold text-indigo-300">AI Engine Active</p>
            <p className="text-[10px] text-slate-500">Pattern Analysis v1.0</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
