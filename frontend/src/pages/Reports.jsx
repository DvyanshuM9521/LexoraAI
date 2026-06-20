import { useState, useEffect } from 'react'
import { FileDown, Loader2, CheckCircle2, AlertCircle, ExternalLink, FileText } from 'lucide-react'
import MainLayout from '../layouts/MainLayout'
import { listContracts, generateReport, getReportDownloadUrl } from '../services/api'
import { format, parseISO } from 'date-fns'
import clsx from 'clsx'

const RiskBadge = ({ level }) => {
  if (!level) return null
  const map = { High: 'risk-badge-high', Medium: 'risk-badge-medium', Low: 'risk-badge-low' }
  return <span className={map[level]}>{level}</span>
}

export default function Reports() {
  const [contracts, setContracts] = useState([])
  const [generating, setGenerating] = useState(null)
  const [generated, setGenerated] = useState({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listContracts()
      .then(r => setContracts(r.data.filter(c => c.status === 'analyzed')))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const handleGenerate = async (contractId) => {
    setGenerating(contractId)
    setError('')
    try {
      const res = await generateReport(contractId)
      setGenerated(prev => ({ ...prev, [contractId]: res.data }))
    } catch (e) {
      setError(e.message)
    } finally {
      setGenerating(null)
    }
  }

  return (
    <MainLayout title="Report Generator" subtitle="Generate downloadable PDF intelligence reports">
      <div className="space-y-6 animate-slide-up">
        <div className="glass-card p-5">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center flex-shrink-0">
              <FileDown className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Professional Contract Reports</h3>
              <p className="text-sm text-slate-400 mt-0.5">
                Generate comprehensive PDF reports including executive summary, risk analysis, clause coverage,
                and actionable recommendations. Reports are formatted for board presentations and legal review.
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
          </div>
        )}

        <div className="glass-card overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-800/60">
            <h2 className="text-sm font-semibold text-slate-200">
              Analyzed Contracts
              <span className="ml-2 text-xs text-slate-500">{contracts.length}</span>
            </h2>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
            </div>
          ) : contracts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <FileText className="w-10 h-10 text-slate-700" />
              <p className="text-slate-500 text-sm">No analyzed contracts found</p>
              <p className="text-slate-600 text-xs">Analyze contracts first to generate reports</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-800/40">
              {contracts.map((contract) => {
                const isGenerating = generating === contract.id
                const isGenerated = !!generated[contract.id]

                return (
                  <div key={contract.id} className="flex items-center gap-4 p-5 hover:bg-slate-800/20 transition-colors">
                    <div className="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center flex-shrink-0">
                      <FileText className="w-4 h-4 text-slate-400" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-200 truncate">{contract.original_name}</p>
                      <div className="flex items-center gap-3 mt-0.5">
                        <p className="text-xs text-slate-500">
                          {format(parseISO(contract.upload_date), 'MMM d, yyyy')}
                        </p>
                        <RiskBadge level={contract.risk_level} />
                        {contract.risk_score != null && (
                          <span className="text-xs font-mono text-slate-600">
                            Score: {contract.risk_score.toFixed(0)}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 flex-shrink-0">
                      {isGenerated ? (
                        <>
                          <a
                            href={getReportDownloadUrl(contract.id)}
                            download
                            className="btn-primary text-xs py-1.5"
                          >
                            <FileDown className="w-3.5 h-3.5" />
                            Download PDF
                          </a>
                          <button
                            onClick={() => handleGenerate(contract.id)}
                            className="btn-secondary text-xs py-1.5"
                          >
                            Regenerate
                          </button>
                        </>
                      ) : (
                        <button
                          onClick={() => handleGenerate(contract.id)}
                          disabled={isGenerating}
                          className={clsx('btn-primary text-xs py-1.5', isGenerating && 'opacity-70')}
                        >
                          {isGenerating ? (
                            <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Generating...</>
                          ) : (
                            <><FileDown className="w-3.5 h-3.5" /> Generate Report</>
                          )}
                        </button>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Report Contents Info */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Report Contents</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {[
              { icon: '📋', title: 'Executive Summary', desc: 'Contract purpose, parties, duration, and key obligations' },
              { icon: '⚠️', title: 'Risk Analysis', desc: 'Risk score, level, and detailed risk factor breakdown' },
              { icon: '🔍', title: 'Clause Analysis', desc: 'All 9 key clauses with extraction confidence scores' },
              { icon: '💡', title: 'Recommendations', desc: 'Prioritized action items with business impact details' },
            ].map((item, i) => (
              <div key={i} className="p-3 rounded-lg bg-slate-800/40 border border-slate-800/60">
                <p className="text-lg mb-1">{item.icon}</p>
                <p className="text-xs font-semibold text-slate-300">{item.title}</p>
                <p className="text-xs text-slate-500 mt-0.5">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
