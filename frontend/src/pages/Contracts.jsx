import { useState, useEffect, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Link } from 'react-router-dom'
import {
  Upload, FileText, Trash2, Eye, Zap, Clock,
  AlertTriangle, CheckCircle2, Loader2, FilePlus
} from 'lucide-react'
import MainLayout from '../layouts/MainLayout'
import { uploadContract, listContracts, deleteContract, getContractFileUrl } from '../services/api'
import { format, parseISO } from 'date-fns'
import clsx from 'clsx'

const RiskBadge = ({ level }) => {
  if (!level) return <span className="text-xs text-slate-600">Pending</span>
  const map = { High: 'risk-badge-high', Medium: 'risk-badge-medium', Low: 'risk-badge-low' }
  return <span className={map[level]}>{level}</span>
}

const StatusBadge = ({ status }) => {
  if (status === 'analyzed') return (
    <span className="inline-flex items-center gap-1 text-xs text-emerald-400">
      <CheckCircle2 className="w-3 h-3" /> Analyzed
    </span>
  )
  return (
    <span className="inline-flex items-center gap-1 text-xs text-slate-500">
      <Clock className="w-3 h-3" /> Uploaded
    </span>
  )
}

export default function Contracts() {
  const [contracts, setContracts] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState('')
  const [deleting, setDeleting] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchContracts = useCallback(async () => {
    try {
      const res = await listContracts()
      setContracts(res.data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchContracts() }, [fetchContracts])

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return
    setError('')
    setUploading(true)
    setUploadProgress(0)
    try {
      await uploadContract(file, setUploadProgress)
      await fetchContracts()
    } catch (e) {
      setError(e.message)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }, [fetchContracts])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: uploading,
  })

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this contract and all its analysis data?')) return
    setDeleting(id)
    try {
      await deleteContract(id)
      setContracts(prev => prev.filter(c => c.id !== id))
    } catch (e) {
      setError(e.message)
    } finally {
      setDeleting(null)
    }
  }

  const formatSize = (bytes) => {
    if (!bytes) return '—'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <MainLayout title="Contract Repository" subtitle="Upload and manage your contracts">
      <div className="space-y-6 animate-slide-up">
        {/* Upload Zone */}
        <div
          {...getRootProps()}
          className={clsx(
            'border-2 border-dashed rounded-xl p-10 text-center transition-all duration-200 cursor-pointer',
            isDragActive
              ? 'border-indigo-500 bg-indigo-600/10'
              : 'border-slate-700 hover:border-indigo-500/60 bg-slate-900/40 hover:bg-indigo-600/5',
            uploading && 'pointer-events-none opacity-60'
          )}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center gap-3">
            {uploading ? (
              <>
                <Loader2 className="w-10 h-10 text-indigo-400 animate-spin" />
                <p className="text-slate-300 font-medium">Uploading... {uploadProgress}%</p>
                <div className="w-48 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-indigo-500 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </>
            ) : isDragActive ? (
              <>
                <FilePlus className="w-10 h-10 text-indigo-400" />
                <p className="text-indigo-300 font-medium">Drop the PDF here</p>
              </>
            ) : (
              <>
                <div className="w-14 h-14 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center">
                  <Upload className="w-6 h-6 text-slate-400" />
                </div>
                <div>
                  <p className="text-slate-300 font-medium">Drop a PDF contract here, or click to browse</p>
                  <p className="text-slate-500 text-sm mt-1">Supports PDF • Max 50MB</p>
                </div>
                <button className="btn-primary mt-1">
                  <Upload className="w-4 h-4" /> Upload Contract
                </button>
              </>
            )}
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Contract Table */}
        <div className="glass-card overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-800/60 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-200">
              Contracts <span className="ml-2 text-xs text-slate-500">{contracts.length}</span>
            </h2>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
            </div>
          ) : contracts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <FileText className="w-10 h-10 text-slate-700" />
              <p className="text-slate-500 text-sm">No contracts uploaded yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800/60">
                    {['Contract Name', 'Uploaded', 'Pages', 'Words', 'Status', 'Risk', 'Actions'].map(h => (
                      <th key={h} className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40">
                  {contracts.map((contract) => (
                    <tr key={contract.id} className="hover:bg-slate-800/30 transition-colors group">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0">
                            <FileText className="w-3.5 h-3.5 text-slate-400" />
                          </div>
                          <span className="font-medium text-slate-200 truncate max-w-[200px]">
                            {contract.original_name}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-xs">
                        {format(parseISO(contract.upload_date), 'MMM d, yyyy')}
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-xs">{contract.page_count || '—'}</td>
                      <td className="py-3 px-4 text-slate-400 text-xs">
                        {contract.word_count ? contract.word_count.toLocaleString() : '—'}
                      </td>
                      <td className="py-3 px-4">
                        <StatusBadge status={contract.status} />
                      </td>
                      <td className="py-3 px-4">
                        <RiskBadge level={contract.risk_level} />
                        {contract.risk_score != null && (
                          <span className="ml-1.5 text-xs text-slate-600 font-mono">
                            ({contract.risk_score.toFixed(0)})
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Link
                            to={`/analysis?id=${contract.id}`}
                            className="p-1.5 rounded-md text-slate-500 hover:text-indigo-400 hover:bg-indigo-500/10 transition-colors"
                            title="Analyze"
                          >
                            <Zap className="w-3.5 h-3.5" />
                          </Link>
                          <a
                            href={getContractFileUrl(contract.id)}
                            target="_blank"
                            rel="noreferrer"
                            className="p-1.5 rounded-md text-slate-500 hover:text-sky-400 hover:bg-sky-500/10 transition-colors"
                            title="View PDF"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </a>
                          <button
                            onClick={() => handleDelete(contract.id)}
                            disabled={deleting === contract.id}
                            className="p-1.5 rounded-md text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-40"
                            title="Delete"
                          >
                            {deleting === contract.id
                              ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              : <Trash2 className="w-3.5 h-3.5" />
                            }
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  )
}
