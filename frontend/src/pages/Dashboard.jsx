import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  FileText, AlertTriangle, TrendingUp, Shield,
  ArrowUpRight, Clock, ChevronRight, Activity
} from 'lucide-react'
import {
  AreaChart, Area, PieChart, Pie, Cell, RadarChart, Radar,
  PolarGrid, PolarAngleAxis, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import MainLayout from '../layouts/MainLayout'
import {
  getDashboardStats, getContractsOverTime,
  getRiskDistribution, getClauseCoverage, getRecentContracts
} from '../services/api'
import { format, parseISO } from 'date-fns'

const StatCard = ({ icon: Icon, label, value, color, sublabel }) => (
  <div className="glass-card p-5 flex items-start gap-4 hover:border-slate-600/60 transition-all duration-200">
    <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${color}`}>
      <Icon className="w-5 h-5 text-white" />
    </div>
    <div className="flex-1 min-w-0">
      <p className="text-2xl font-bold text-slate-100">{value}</p>
      <p className="text-sm text-slate-400">{label}</p>
      {sublabel && <p className="text-xs text-slate-600 mt-0.5">{sublabel}</p>}
    </div>
    <ArrowUpRight className="w-4 h-4 text-slate-600 flex-shrink-0" />
  </div>
)

const RiskBadge = ({ level }) => {
  const map = {
    High: 'risk-badge-high',
    Medium: 'risk-badge-medium',
    Low: 'risk-badge-low',
  }
  return <span className={map[level] || 'risk-badge-low'}>{level}</span>
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-card px-3 py-2 text-xs shadow-xl">
      <p className="text-slate-400 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="font-semibold" style={{ color: p.color }}>
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [timeData, setTimeData] = useState([])
  const [riskDist, setRiskDist] = useState([])
  const [clauseCov, setClauseCov] = useState([])
  const [recent, setRecent] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [s, t, r, c, rc] = await Promise.all([
          getDashboardStats(),
          getContractsOverTime(),
          getRiskDistribution(),
          getClauseCoverage(),
          getRecentContracts(),
        ])
        setStats(s.data)
        setTimeData(t.data.map(d => ({ ...d, date: d.date.slice(5) })))
        setRiskDist(r.data)
        setClauseCov(c.data.slice(0, 8))
        setRecent(rc.data)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  if (loading) {
    return (
      <MainLayout title="Dashboard" subtitle="Contract Intelligence Overview">
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-500 text-sm">Loading dashboard...</p>
          </div>
        </div>
      </MainLayout>
    )
  }

  const statCards = [
    { icon: FileText, label: 'Total Contracts', value: stats?.total_contracts ?? 0, color: 'bg-indigo-600', sublabel: `${stats?.analyzed ?? 0} analyzed` },
    { icon: AlertTriangle, label: 'High Risk', value: stats?.high_risk ?? 0, color: 'bg-red-600', sublabel: 'Require attention' },
    { icon: Activity, label: 'Medium Risk', value: stats?.medium_risk ?? 0, color: 'bg-amber-600', sublabel: 'Under review' },
    { icon: Shield, label: 'Low Risk', value: stats?.low_risk ?? 0, color: 'bg-emerald-600', sublabel: 'Compliant' },
  ]

  const hasData = stats?.total_contracts > 0

  return (
    <MainLayout title="Dashboard" subtitle="Contract Intelligence Overview">
      <div className="space-y-6 animate-slide-up">
        {/* Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {statCards.map((card, i) => (
            <StatCard key={i} {...card} />
          ))}
        </div>

        {!hasData && (
          <div className="glass-card p-10 flex flex-col items-center justify-center text-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center">
              <FileText className="w-8 h-8 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-200">No contracts yet</h3>
              <p className="text-slate-500 text-sm mt-1">Upload your first contract to start analyzing</p>
            </div>
            <Link to="/contracts" className="btn-primary">
              Upload Contract <ArrowUpRight className="w-4 h-4" />
            </Link>
          </div>
        )}

        {hasData && (
          <>
            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Contracts Over Time */}
              <div className="glass-card p-5 lg:col-span-2">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-200">Contracts Over Time</h3>
                    <p className="text-xs text-slate-500">Last 30 days</p>
                  </div>
                  <TrendingUp className="w-4 h-4 text-indigo-400" />
                </div>
                <ResponsiveContainer width="100%" height={180}>
                  <AreaChart data={timeData} margin={{ top: 5, right: 10, bottom: 0, left: -20 }}>
                    <defs>
                      <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} tickLine={false} axisLine={false} interval={4} />
                    <YAxis tick={{ fill: '#64748b', fontSize: 10 }} tickLine={false} axisLine={false} allowDecimals={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="count" name="Contracts" stroke="#6366f1" fill="url(#grad)" strokeWidth={2} dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Risk Distribution */}
              <div className="glass-card p-5">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-200">Risk Distribution</h3>
                    <p className="text-xs text-slate-500">Analyzed contracts</p>
                  </div>
                  <Shield className="w-4 h-4 text-indigo-400" />
                </div>
                {riskDist.every(d => d.value === 0) ? (
                  <div className="h-[180px] flex items-center justify-center text-slate-600 text-sm">No analyzed contracts</div>
                ) : (
                  <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                      <Pie data={riskDist} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value">
                        {riskDist.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(v, n) => [v, n]} contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }} />
                      <Legend iconSize={8} wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* Clause Coverage */}
            {clauseCov.length > 0 && (
              <div className="glass-card p-5">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-200">Clause Coverage</h3>
                    <p className="text-xs text-slate-500">Average across all analyzed contracts</p>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={clauseCov} margin={{ top: 0, right: 10, bottom: 0, left: -20 }} barSize={18}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                    <XAxis dataKey="clause" tick={{ fill: '#64748b', fontSize: 9 }} tickLine={false} axisLine={false} />
                    <YAxis tick={{ fill: '#64748b', fontSize: 10 }} tickLine={false} axisLine={false} domain={[0, 100]} unit="%" />
                    <Tooltip content={<CustomTooltip />} formatter={(v) => [`${v}%`]} />
                    <Bar dataKey="coverage" name="Coverage" fill="#6366f1" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Recent Contracts */}
            {recent.length > 0 && (
              <div className="glass-card p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-200">Recent Contracts</h3>
                  <Link to="/contracts" className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                    View all <ChevronRight className="w-3 h-3" />
                  </Link>
                </div>
                <div className="divide-y divide-slate-800/60">
                  {recent.map((c) => (
                    <div key={c.id} className="flex items-center gap-4 py-3 hover:bg-slate-800/30 -mx-2 px-2 rounded-lg transition-colors">
                      <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0">
                        <FileText className="w-4 h-4 text-slate-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-200 truncate">{c.name}</p>
                        <p className="text-xs text-slate-500 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {format(parseISO(c.upload_date), 'MMM d, yyyy')}
                        </p>
                      </div>
                      {c.risk_level && <RiskBadge level={c.risk_level} />}
                      {c.risk_score != null && (
                        <span className="text-xs font-mono text-slate-400">{c.risk_score.toFixed(0)}</span>
                      )}
                      <Link to={`/analysis?id=${c.id}`} className="text-slate-600 hover:text-indigo-400 transition-colors">
                        <ChevronRight className="w-4 h-4" />
                      </Link>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </MainLayout>
  )
}
