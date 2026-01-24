export interface User {
  id: number
  email: string
  role: 'user' | 'lawyer' | 'admin'
  created_at: string
}

export interface Lawyer {
  id: number
  name: string
  oab: string
  areas: string[]
  city: string
  success_score: number
  active: boolean
}

export interface Case {
  id: number
  user_id: number
  area: string
  descricao: string
  score_prob?: string
  cost_estimate?: string
  status: string
  created_at: string
}

export interface Report {
  id: number
  case_id: number
  pdf_path?: string
  paid: boolean
  content: AnalysisResponse
  created_at: string
}

export interface AnalysisResponse {
  tipificacao: string
  estrategias_riscos: string
  probabilidade: string
  custos_prazos: string
  checklist: string[]
  rascunho: string
  citacoes: Citation[]
  vigencia_base: string
}

export interface Citation {
  tipo: string
  id: string
  content: string
}

export interface SearchResult {
  id: string
  tipo: string
  area: string
  titulo: string
  texto: string
  score: number
  metadata: Record<string, any>
}

export interface Plan {
  id: number
  code: string
  name: string
  price_cents: number
  features: Record<string, any>
  active: boolean
}

export interface Lead {
  id: number
  case_id: number
  lawyer_id: number
  status: 'pending' | 'accepted' | 'expired' | 'rejected'
  expires_at: string
  created_at: string
}
