import { Bell, Search, HelpCircle } from 'lucide-react'

export default function TopNav({ title, subtitle }) {
  return (
    <header className="h-16 bg-slate-900/60 backdrop-blur-xl border-b border-slate-800/60 flex items-center px-6 gap-4 sticky top-0 z-30">
      <div className="flex-1 min-w-0">
        <h1 className="text-lg font-semibold text-slate-100 truncate">{title}</h1>
        {subtitle && <p className="text-xs text-slate-500 truncate">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-2 flex-shrink-0">
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search contracts..."
            className="pl-9 pr-4 py-1.5 bg-slate-800/80 border border-slate-700 rounded-lg text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-indigo-500/50 w-52"
          />
        </div>

        <button className="relative p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-indigo-500 rounded-full" />
        </button>

        <button className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors">
          <HelpCircle className="w-4 h-4" />
        </button>

        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white shadow-lg shadow-indigo-500/20">
          L
        </div>
      </div>
    </header>
  )
}
