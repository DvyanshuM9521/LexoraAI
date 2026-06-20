import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    return Promise.reject(new Error(message))
  }
)

// ── Contracts ──────────────────────────────────────────────────────────────
export const uploadContract = (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/contracts/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded * 100) / e.total))
      }
    },
  })
}

export const listContracts = () => api.get('/contracts/')
export const getContract = (id) => api.get(`/contracts/${id}`)
export const deleteContract = (id) => api.delete(`/contracts/${id}`)
export const getContractFileUrl = (id) => `/api/contracts/${id}/file`

// ── Analysis ───────────────────────────────────────────────────────────────
export const analyzeContract = (id) => api.post(`/analysis/${id}/analyze`)
export const getAnalysis = (id) => api.get(`/analysis/${id}`)

// ── Dashboard ──────────────────────────────────────────────────────────────
export const getDashboardStats = () => api.get('/dashboard/stats')
export const getContractsOverTime = () => api.get('/dashboard/contracts-over-time')
export const getRiskDistribution = () => api.get('/dashboard/risk-distribution')
export const getClauseCoverage = () => api.get('/dashboard/clause-coverage')
export const getRecentContracts = () => api.get('/dashboard/recent-contracts')

// ── Comparison ─────────────────────────────────────────────────────────────
export const compareContracts = (contractAId, contractBId) =>
  api.post('/comparison/', { contract_a_id: contractAId, contract_b_id: contractBId })

// ── Chat ───────────────────────────────────────────────────────────────────
export const sendChatMessage = (contractId, message) =>
  api.post(`/chat/${contractId}/message`, { message })
export const getChatHistory = (contractId) => api.get(`/chat/${contractId}/history`)
export const clearChatHistory = (contractId) => api.delete(`/chat/${contractId}/history`)

// ── Reports ────────────────────────────────────────────────────────────────
export const generateReport = (contractId) => api.post(`/reports/${contractId}/generate`)
export const getReportDownloadUrl = (contractId) => `/api/reports/${contractId}/download`

export default api
