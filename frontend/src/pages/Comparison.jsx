import { useState, useEffect } from 'react'
import { GitCompare, ArrowRight, Loader2, AlertCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import MainLayout from '../layouts/MainLayout'
import { listContracts, compareContracts } from '../services/api'
import clsx from 'clsx'

const IMPACT_STYLES = {
  high: 'text-red-400 bg-red-500/10 border-red-500/25',
  medium: 'text-amber-400 bg-amber-500/10 border-amber-500/25',
  low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/25',
  none: 'text-slate-500 bg-slate-800/40 border-slate-700/40',
}

const CHANGE_TYPE_LABELS = {
  modified: { label: 'Modified', color: 'text-amber-400' },
  added: { label: 'Added', color: 'text-emerald-400' },
  removed: { label: 'Removed', color: 'text-red-400' },
  unchanged: { label: 'Unchanged', color: 'text-slate-600' },
}

const ImpactIndicator = ({ delta }) => {
  if (delta > 0) return <TrendingUp className="w-4 h-4 text-red-400" />
  if (delta < 0) return <TrendingDown className="w-4 h-4 text-emerald-400" />
  return <Minus className="w-4 h-4 text-slate-500" />
}

export default function Comparison() {
  const [contracts, setContracts] = useState([])
  const [contractA, setContractA] = useState('')
  const [contractB, setContractB] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    listContracts().then(r => {
      const analyzed = r.data.filter(c => c.status === 'analyzed')
      setContracts(analyzed)
    }).catch(() => {})
  }, [])

  const handleCompare = async () => {
    if (!contractA || !contractB) return
    if (contractA === contractB) {
      setError('Please select two different contracts to compare.')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await compareContracts(Number(contractA), Number(contractB))
      setResult(res.data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const changedClauses = result?.changes?.filter(c => c.change_type !== 'unchanged') || []
  const unchangedClauses = result?.changes?.filter(c => c.change_type === 'unchanged') || []

  return (
    <MainLayout title="Contract Comparison" subtitle="Side-by-side clause analysis and change detection">
      <div className="space-y-6 animate-slide-up">
        {/* Selector */}
        <div className="glass-card p-5">
          <div className="grid grid-cols-1 md:grid-cols-[1fr,auto,1fr,auto] gap-4 items-end">
            <div>
              <label className="section-label mb-2 block">Contract A</label>
              <select value={contractA} onChange={e => setContractA(e.target.value)} className="input-field">
                <option value="">Select contract...</option>
                {contracts.map(c => (
                  <option key={c.id} value={c.id}>{c.original_name}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center justify-center pb-0.5">
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center">
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </div>
            </div>

            <div>
              <label className="section-label mb-2 block">Contract B</label>
              <select value={contractB} onChange={e => setContractB(e.target.value)} className="input-field">
                <option value="">Select contract...</option>
                {contracts.map(c => (
                  <option key={c.id} value={c.id}>{c.original_name}</option>
                ))}
              </select>
            </div>

            <button
              onClick={handleCompare}
              disabled={!contractA || !contractB || loading}
              className="btn-primary h-[38px]"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <GitCompare className="w-4 h-4" />}
              {loading ? 'Comparing...' : 'Compare'}
            </button>
          </div>

          {contracts.length === 0 && (
            <p className="text-xs text-amber-400/70 mt-3 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5" />
              You need at least 2 analyzed contracts to use comparison. Go to Analysis to analyze contracts first.
            </p>
          )}
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
              <p className="text-slate-500 text-sm">Comparing contracts...</p>
            </div>
          </div>
        )}

        {result && (
          <div className="space-y-4">
            {/* Overview */}
            <div className="glass-card p-5">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-slate-200 mb-1">Comparison Summary</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">{result.summary}</p>
                </div>
                <div className="flex flex-col items-end gap-1 flex-shrink-0">
                  <div className="flex items-center gap-2">
                    <ImpactIndicator delta={result.risk_delta} />
                    <span className={clsx('text-sm font-bold font-mono',
                      result.risk_delta > 0 ? 'text-red-400' : result.risk_delta < 0 ? 'text-emerald-400' : 'text-slate-400'
                    )}>
                      {result.risk_delta > 0 ? '+' : ''}{result.risk_delta.toFixed(1)} pts
                    </span>
                  </div>
                  <span className={clsx('text-xs font-semibold px-2.5 py-1 rounded-full border',
                    result.risk_delta > 15 ? 'text-red-400 border-red-500/30 bg-red-500/10' :
                    result.risk_delta > 0 ? 'text-amber-400 border-amber-500/30 bg-amber-500/10' :
                    result.risk_delta < 0 ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10' :
                    'text-slate-400 border-slate-600 bg-slate-800/40'
                  )}>
                    {result.overall_impact}
                  </span>
                </div>
              </div>
            </div>

            {/* Contract Headers */}
            <div className="grid grid-cols-2 gap-3">
              <div className="glass-card p-3">
                <p className="section-label mb-1">Contract A</p>
                <p className="text-sm font-medium text-slate-200 truncate">{result.contract_a?.original_name}</p>
              </div>
              <div className="glass-card p-3 border-indigo-500/30">
                <p className="section-label mb-1">Contract B</p>
                <p className="text-sm font-medium text-slate-200 truncate">{result.contract_b?.original_name}</p>
              </div>
            </div>

            {/* Changed Clauses */}
            {changedClauses.length > 0 && (
              <div className="glass-card overflow-hidden">
                <div className="px-5 py-3 border-b border-slate-800/60 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-400" />
                  <h3 className="text-sm font-semibold text-slate-200">Changed Clauses</h3>
                  <span className="text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-full">
                    {changedClauses.length}
                  </span>
                </div>
                <div className="divide-y divide-slate-800/40">
                  {changedClauses.map((change, i) => (
                    <div key={i} className="p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <h4 className="text-sm font-semibold text-slate-200">{change.title}</h4>
                        <span className={clsx('text-xs font-medium', CHANGE_TYPE_LABELS[change.change_type]?.color)}>
                          {CHANGE_TYPE_LABELS[change.change_type]?.label}
                        </span>
                        <span className={clsx('text-[10px] font-bold uppercase px-2 py-0.5 rounded border ml-auto', IMPACT_STYLES[change.impact_level])}>
                          {change.impact_level === 'none' ? 'No Impact' : `${change.impact_level} Impact`}
                        </span>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                        <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/60">
                          <p className="section-label mb-1.5">Contract A</p>
                          <p className="text-xs text-slate-400 leading-relaxed line-clamp-4">
                            {change.contract_a === 'Not found' ? (
                              <span className="text-slate-600 italic">Not found</span>
                            ) : change.contract_a}
                          </p>
                        </div>
                        <div className="p-3 rounded-lg bg-indigo-900/10 border border-indigo-500/20">
                          <p className="section-label mb-1.5">Contract B</p>
                          <p className="text-xs text-slate-400 leading-relaxed line-clamp-4">
                            {change.contract_b === 'Not found' ? (
                              <span className="text-slate-600 italic">Not found</span>
                            ) : change.contract_b}
                          </p>
                        </div>
                      </div>

                      <div className={clsx('p-3 rounded-lg border text-xs leading-relaxed', IMPACT_STYLES[change.impact_level])}>
                        {change.impact}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Unchanged Clauses Summary */}
            {unchangedClauses.length > 0 && (
              <div className="glass-card p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Minus className="w-4 h-4 text-slate-500" />
                  <h3 className="text-sm font-semibold text-slate-500">Unchanged Clauses ({unchangedClauses.length})</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {unchangedClauses.map((c, i) => (
                    <span key={i} className="text-xs text-slate-600 bg-slate-800/60 border border-slate-800 px-2.5 py-1 rounded-lg">
                      {c.title}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </MainLayout>
  )
}
