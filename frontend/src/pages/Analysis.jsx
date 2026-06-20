import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import {
  Zap, FileText, AlertTriangle, CheckCircle2, XCircle,
  Loader2, ChevronDown, ChevronUp, Shield, Target,
  Lightbulb, BookOpen, AlertCircle, ArrowLeft
} from 'lucide-react'
import MainLayout from '../layouts/MainLayout'
import { listContracts, analyzeContract, getAnalysis } from '../services/api'
import clsx from 'clsx'

const SEVERITY_COLORS = {
  Critical: 'text-red-400 bg-red-500/10 border-red-500/25',
  High: 'text-red-400 bg-red-500/10 border-red-500/25',
  Medium: 'text-amber-400 bg-amber-500/10 border-amber-500/25',
  Low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/25',
  None: 'text-slate-500 bg-slate-800/50 border-slate-700/50',
}

const RiskGauge = ({ score, level }) => {
  const color = level === 'High' ? '#ef4444' : level === 'Medium' ? '#f59e0b' : '#10b981'
  const angle = (score / 100) * 180 - 90
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-36 h-20 overflow-hidden">
        <svg viewBox="0 0 120 60" className="w-full h-full">
          {/* Track */}
          <path d="M 10 60 A 50 50 0 0 1 110 60" fill="none" stroke="#1e293b" strokeWidth="10" strokeLinecap="round" />
          {/* Progress */}
          <path
            d="M 10 60 A 50 50 0 0 1 110 60"
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${(score / 100) * 157} 157`}
          />
          {/* Needle */}
          <g transform={`translate(60, 60) rotate(${angle})`}>
            <line x1="0" y1="0" x2="0" y2="-42" stroke="#f1f5f9" strokeWidth="2" strokeLinecap="round" />
            <circle cx="0" cy="0" r="3" fill="#f1f5f9" />
          </g>
        </svg>
      </div>
      <div className="text-center">
        <p className="text-3xl font-bold font-mono" style={{ color }}>{score.toFixed(0)}</p>
        <p className="text-xs text-slate-500 uppercase tracking-wider">/ 100</p>
      </div>
    </div>
  )
}

const ClauseCard = ({ clause }) => {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className={clsx(
      'glass-card p-4 transition-all duration-200',
      clause.found ? 'border-slate-700/50' : 'border-slate-800/50 opacity-75'
    )}>
      <div className="flex items-start gap-3">
        <div className={clsx(
          'w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5',
          clause.found ? 'bg-emerald-500/10' : 'bg-red-500/10'
        )}>
          {clause.found
            ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            : <XCircle className="w-3.5 h-3.5 text-red-400" />
          }
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h4 className="text-sm font-semibold text-slate-200">{clause.title}</h4>
            <div className="flex items-center gap-2 flex-shrink-0">
              {clause.found && (
                <span className="text-[10px] font-mono text-slate-600 bg-slate-800 px-1.5 py-0.5 rounded">
                  {(clause.confidence * 100).toFixed(0)}%
                </span>
              )}
              {clause.found && clause.content.length > 100 && (
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="text-slate-600 hover:text-slate-400"
                >
                  {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </button>
              )}
            </div>
          </div>
          {clause.found && (
            <p className={clsx('text-xs text-slate-400 mt-1.5 leading-relaxed', !expanded && 'line-clamp-2')}>
              {clause.content}
            </p>
          )}
          {!clause.found && (
            <p className="text-xs text-red-400/70 mt-1">Not identified in contract</p>
          )}
        </div>
      </div>
    </div>
  )
}

const RiskFactorRow = ({ factor }) => (
  <div className={clsx(
    'flex items-start gap-3 p-3 rounded-lg border',
    factor.present ? SEVERITY_COLORS[factor.severity] || SEVERITY_COLORS.Medium : 'border-slate-800/40 bg-slate-900/20'
  )}>
    <div className={clsx('mt-0.5 flex-shrink-0', factor.present ? 'opacity-100' : 'opacity-30')}>
      {factor.present
        ? <AlertTriangle className="w-4 h-4" />
        : <CheckCircle2 className="w-4 h-4 text-emerald-400" />
      }
    </div>
    <div className="flex-1 min-w-0">
      <div className="flex items-center gap-2">
        <span className={clsx('text-sm font-semibold', !factor.present && 'text-slate-500')}>{factor.factor}</span>
        {factor.present && (
          <span className={clsx('text-[10px] font-bold uppercase px-1.5 py-0.5 rounded border', SEVERITY_COLORS[factor.severity] || SEVERITY_COLORS.Medium)}>
            {factor.severity}
          </span>
        )}
      </div>
      <p className={clsx('text-xs mt-0.5 leading-relaxed', factor.present ? 'opacity-90' : 'text-slate-600')}>
        {factor.explanation}
      </p>
    </div>
  </div>
)

const RecommendationCard = ({ rec }) => {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="glass-card p-4 hover:border-slate-600/60 transition-all duration-200">
      <div className="flex items-start gap-3">
        <div className={clsx('w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 border',
          SEVERITY_COLORS[rec.severity] || SEVERITY_COLORS.Medium
        )}>
          <Lightbulb className="w-3.5 h-3.5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className="text-sm font-semibold text-slate-200">{rec.issue}</h4>
            <div className="flex items-center gap-2 flex-shrink-0">
              <span className={clsx('text-[10px] font-bold uppercase px-1.5 py-0.5 rounded border', SEVERITY_COLORS[rec.severity] || SEVERITY_COLORS.Medium)}>
                {rec.severity}
              </span>
              <button onClick={() => setExpanded(!expanded)} className="text-slate-600 hover:text-slate-400">
                {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">{rec.category}</p>
          {expanded && (
            <div className="mt-3 space-y-2">
              <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/40">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-1">Business Impact</p>
                <p className="text-xs text-slate-300 leading-relaxed">{rec.business_impact}</p>
              </div>
              <div className="p-3 rounded-lg bg-indigo-500/5 border border-indigo-500/20">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-indigo-400 mb-1">Suggested Action</p>
                <p className="text-xs text-slate-300 leading-relaxed">{rec.suggested_action}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const TABS = ['Summary', 'Clauses', 'Risk', 'Recommendations']

export default function Analysis() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [contracts, setContracts] = useState([])
  const [selectedId, setSelectedId] = useState(searchParams.get('id') ? Number(searchParams.get('id')) : null)
  const [analysis, setAnalysis] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('Summary')

  useEffect(() => {
    listContracts().then(r => setContracts(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    const id = searchParams.get('id')
    if (id) {
      setSelectedId(Number(id))
      loadAnalysis(Number(id))
    }
  }, [searchParams])

  const loadAnalysis = async (id) => {
    setLoading(true)
    setError('')
    try {
      const res = await getAnalysis(id)
      setAnalysis(res.data)
    } catch {
      setAnalysis(null)
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!selectedId) return
    setAnalyzing(true)
    setError('')
    try {
      const res = await analyzeContract(selectedId)
      setAnalysis(res.data)
      setActiveTab('Summary')
    } catch (e) {
      setError(e.message)
    } finally {
      setAnalyzing(false)
    }
  }

  const handleSelect = (id) => {
    setSelectedId(id)
    setSearchParams({ id })
    setAnalysis(null)
    setError('')
  }

  const selectedContract = contracts.find(c => c.id === selectedId)

  return (
    <MainLayout title="Contract Analysis" subtitle="Clause Intelligence & Risk Assessment">
      <div className="space-y-5 animate-slide-up">
        {/* Contract Selector */}
        <div className="glass-card p-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <div className="flex-1">
              <label className="section-label mb-2 block">Select Contract</label>
              <select
                value={selectedId || ''}
                onChange={e => handleSelect(Number(e.target.value))}
                className="input-field max-w-sm"
              >
                <option value="">Choose a contract...</option>
                {contracts.map(c => (
                  <option key={c.id} value={c.id}>{c.original_name}</option>
                ))}
              </select>
            </div>
            {selectedId && (
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="btn-primary flex-shrink-0"
              >
                {analyzing
                  ? <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</>
                  : <><Zap className="w-4 h-4" /> {analysis ? 'Re-Analyze' : 'Analyze'}</>
                }
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
          </div>
        )}

        {!selectedId && (
          <div className="glass-card p-12 flex flex-col items-center gap-4 text-center">
            <div className="w-16 h-16 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center">
              <FileText className="w-8 h-8 text-slate-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-300">Select a contract to analyze</h3>
              <p className="text-slate-500 text-sm mt-1">
                Or{' '}
                <Link to="/contracts" className="text-indigo-400 hover:underline">upload a new contract</Link>
                {' '}first
              </p>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
          </div>
        )}

        {selectedId && !analysis && !loading && !analyzing && (
          <div className="glass-card p-10 flex flex-col items-center gap-4 text-center">
            <Zap className="w-10 h-10 text-indigo-400" />
            <div>
              <h3 className="text-lg font-semibold text-slate-200">Contract not yet analyzed</h3>
              <p className="text-slate-500 text-sm mt-1">Click "Analyze" to extract clauses, assess risks, and generate recommendations</p>
            </div>
          </div>
        )}

        {analysis && (
          <div className="space-y-4">
            {/* Tabs */}
            <div className="flex gap-1 p-1 bg-slate-900/60 border border-slate-800/60 rounded-xl w-fit">
              {TABS.map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={clsx(
                    'px-4 py-1.5 text-sm font-medium rounded-lg transition-all duration-150',
                    activeTab === tab
                      ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/40'
                      : 'text-slate-500 hover:text-slate-300'
                  )}
                >
                  {tab}
                  {tab === 'Recommendations' && analysis.recommendations?.length > 0 && (
                    <span className="ml-1.5 text-[10px] bg-red-500/20 text-red-400 px-1.5 py-0.5 rounded-full">
                      {analysis.recommendations.length}
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            {activeTab === 'Summary' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Risk Score */}
                <div className="glass-card p-5 flex flex-col items-center gap-4">
                  <div className="text-center">
                    <p className="section-label">Risk Score</p>
                  </div>
                  <RiskGauge score={analysis.risk?.score ?? 0} level={analysis.risk?.level ?? 'Low'} />
                  <div className={clsx('px-4 py-1.5 rounded-full text-sm font-bold border',
                    analysis.risk?.level === 'High' ? 'text-red-400 border-red-500/30 bg-red-500/10' :
                    analysis.risk?.level === 'Medium' ? 'text-amber-400 border-amber-500/30 bg-amber-500/10' :
                    'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'
                  )}>
                    {analysis.risk?.level} Risk
                  </div>
                  <p className="text-xs text-slate-500 text-center leading-relaxed">{analysis.risk?.summary}</p>
                </div>

                {/* Summary Details */}
                <div className="lg:col-span-2 space-y-3">
                  <div className="glass-card p-4">
                    <p className="section-label mb-2">Contract Purpose</p>
                    <p className="text-sm text-slate-300 leading-relaxed">{analysis.summary?.purpose}</p>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="glass-card p-4">
                      <p className="section-label mb-2">Parties</p>
                      {analysis.summary?.parties?.map((p, i) => (
                        <p key={i} className="text-sm text-slate-300">{p}</p>
                      ))}
                    </div>
                    <div className="glass-card p-4">
                      <p className="section-label mb-2">Duration</p>
                      <p className="text-sm text-slate-300">{analysis.summary?.duration}</p>
                    </div>
                  </div>
                  <div className="glass-card p-4">
                    <p className="section-label mb-2">Key Obligations</p>
                    <ul className="space-y-1.5">
                      {analysis.summary?.key_obligations?.map((o, i) => (
                        <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 flex-shrink-0" />
                          {o}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'Clauses' && (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                {analysis.clauses?.map((clause, i) => (
                  <ClauseCard key={i} clause={clause} />
                ))}
              </div>
            )}

            {activeTab === 'Risk' && (
              <div className="space-y-3">
                <div className="glass-card p-4">
                  <div className="flex items-center gap-3 mb-1">
                    <Shield className="w-4 h-4 text-indigo-400" />
                    <h3 className="text-sm font-semibold text-slate-200">Risk Assessment Summary</h3>
                  </div>
                  <p className="text-sm text-slate-400 leading-relaxed">{analysis.risk?.summary}</p>
                </div>
                <div className="space-y-2">
                  {analysis.risk?.factors?.map((factor, i) => (
                    <RiskFactorRow key={i} factor={factor} />
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'Recommendations' && (
              <div className="space-y-3">
                {analysis.recommendations?.length === 0 ? (
                  <div className="glass-card p-10 flex flex-col items-center gap-3 text-center">
                    <CheckCircle2 className="w-10 h-10 text-emerald-400" />
                    <p className="text-slate-300 font-medium">No critical recommendations</p>
                    <p className="text-slate-500 text-sm">This contract has a manageable risk profile</p>
                  </div>
                ) : (
                  analysis.recommendations?.map((rec, i) => (
                    <RecommendationCard key={i} rec={rec} />
                  ))
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </MainLayout>
  )
}
