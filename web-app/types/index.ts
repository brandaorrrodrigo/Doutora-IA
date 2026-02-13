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

export interface Citation {
  id: string
  tipo: string
  titulo: string
  texto: string
  artigo_ou_tema?: string
  orgao?: string
  tribunal?: string
  data?: string
  fonte_url?: string
  hierarquia?: number
}

export interface AnalysisResponse {
  case_id?: number
  tipificacao: string
  area: string
  sub_area?: string
  estrategias: string
  riscos: string
  probabilidade: 'baixa' | 'media' | 'alta'
  probabilidade_detalhes: string
  custos: string
  prazos: string
  checklist: string[]
  rascunho_peticao: string
  citacoes: Citation[]
  base_atualizada_em: string
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

export interface CheckoutRequest {
  case_id: number
  provider: 'stripe' | 'mercadopago'
  payer_email?: string
}

export interface CheckoutResponse {
  payment_id: number
  checkout_url: string
  provider: string
}

export interface PaymentStatus {
  payment_id: number
  status: string
  provider: string
  report_url?: string
}
