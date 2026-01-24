import axios from 'axios'
import type { AnalysisResponse, SearchResult, Report, Case, Lawyer, Lead } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// API Methods
export const apiClient = {
  // Health
  health: () => api.get('/health'),

  // Search
  search: (query: string, filtros?: Record<string, any>, limit = 10) =>
    api.post<SearchResult[]>('/search', { query, filtros, limit }),

  // Case Analysis
  analyzeCase: (descricao: string, detalhado = false) =>
    api.post<AnalysisResponse>('/analyze_case', { descricao, detalhado }),

  // Reports
  generateReport: (case_id?: number, payload?: Record<string, any>) =>
    api.post<Report>('/report', { case_id, payload }),

  // Compose
  composeDocument: (
    tipo_peca: string,
    metadados: Record<string, any>,
    carrinho_citacoes: any[]
  ) =>
    api.post('/compose', { tipo_peca, metadados, carrinho_citacoes }),

  // Auth
  register: (email: string, password: string, role = 'user') =>
    api.post('/auth/register', { email, password, role }),

  login: (email: string, password: string) =>
    api.post<{ access_token: string; user: any }>('/auth/login', { email, password }),

  me: () => api.get('/auth/me'),

  // Cases
  getCases: () => api.get<Case[]>('/cases'),

  getCase: (id: number) => api.get<Case>(`/cases/${id}`),

  // Lawyers
  getLawyers: () => api.get<Lawyer[]>('/lawyers'),

  registerLawyer: (data: Partial<Lawyer>) =>
    api.post<Lawyer>('/lawyers/register', data),

  getLawyerFeed: (lawyer_id: number) =>
    api.get<Case[]>(`/lawyers/feed?lawyer_id=${lawyer_id}`),

  // Leads
  assignLead: (case_id: number, lawyer_id: number) =>
    api.post<Lead>('/leads/assign', { case_id, lawyer_id }),
}
