'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import Link from 'next/link'
import { toast } from 'sonner'
import { apiClient } from '@/services/api'
import type { AnalysisResponse } from '@/types'

const probabilidadeLabel: Record<string, { text: string; color: string }> = {
  baixa: { text: 'Baixa', color: 'text-red-400' },
  media: { text: 'Média', color: 'text-yellow-400' },
  alta: { text: 'Alta', color: 'text-green-400' },
}

export default function AnalisePage() {
  const [descricao, setDescricao] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResponse | null>(null)
  const [error, setError] = useState('')
  const [showPayment, setShowPayment] = useState(false)
  const [paymentLoading, setPaymentLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (descricao.trim().length < 50) {
      setError('Descreva seu caso com pelo menos 50 caracteres para uma análise adequada.')
      return
    }

    setLoading(true)
    try {
      const response = await apiClient.analyzeCase(descricao.trim())
      setResult(response.data)
      toast.success('Análise concluída!')
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Erro ao analisar o caso. Tente novamente.'
      setError(msg)
      toast.error('Erro na análise')
    } finally {
      setLoading(false)
    }
  }

  const handleCheckout = async (provider: 'stripe' | 'mercadopago') => {
    if (!result?.case_id) {
      toast.error('ID do caso não disponível')
      return
    }
    setPaymentLoading(true)
    try {
      const response = await apiClient.createCheckout({
        case_id: result.case_id,
        provider
      })
      // Save payment_id for success page
      localStorage.setItem('pending_payment_id', String(response.data.payment_id))
      window.location.href = response.data.checkout_url
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Erro ao criar checkout'
      toast.error(msg)
      setPaymentLoading(false)
    }
  }

  const prob = result ? probabilidadeLabel[result.probabilidade] || { text: result.probabilidade, color: 'text-[#f5f5dc]' } : null

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0a] via-[#1a1410] to-[#0a0a0a]">
      <header className="container mx-auto px-4 py-6 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-3">
          <Image src="/logo-redonda.png" alt="Doutora IA" width={48} height={48} />
          <span className="text-2xl font-bold text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Doutora IA</span>
        </Link>
        <Link href="/dashboard">
          <Button variant="outline" className="text-[#d4af37] border-[#d4af37] hover:bg-[#d4af37]/15">
            Dashboard
          </Button>
        </Link>
      </header>

      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold text-[#d4af37] text-center mb-8" style={{ fontFamily: "'Cinzel', serif" }}>
          Análise Jurídica Inteligente
        </h1>

        {!result && (
          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Descreva seu caso</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label className="text-[#f5f5dc]">Descrição do Caso</Label>
                  <Textarea
                    value={descricao}
                    onChange={(e) => setDescricao(e.target.value)}
                    rows={8}
                    placeholder="Descreva seu problema jurídico com o máximo de detalhes possível..."
                    className="bg-[#0a0a0a]/50 border-[#d4af37]/30 text-[#f5f5dc] placeholder:text-[#f5f5dc]/40"
                  />
                  <div className="text-sm text-[#f5f5dc]/50 mt-1">
                    {descricao.length} caracteres (mínimo 50)
                  </div>
                </div>
                {error && (
                  <div className="bg-red-900/30 text-red-300 p-3 rounded-md text-sm border border-red-500/30">
                    {error}
                  </div>
                )}
                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold text-lg py-6"
                  disabled={loading}
                >
                  {loading ? (
                    <span className="flex items-center gap-3">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Analisando com IA... Aguarde
                    </span>
                  ) : 'Analisar Caso'}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {result && (
          <div className="space-y-6">
            {/* Tipificação */}
            <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
              <CardHeader>
                <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>
                  Tipificação
                  {result.area && <span className="text-sm font-normal text-[#f5f5dc]/60 ml-3">({result.area}{result.sub_area ? ` - ${result.sub_area}` : ''})</span>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-[#f5f5dc]/90 leading-relaxed prose prose-invert prose-sm max-w-none prose-headings:text-[#d4af37] prose-strong:text-[#f5f5dc] prose-li:text-[#f5f5dc]/90"><ReactMarkdown>{result.tipificacao}</ReactMarkdown></div>
              </CardContent>
            </Card>

            {/* Estratégias e Riscos */}
            {(result.estrategias || result.riscos) && (
              <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
                <CardHeader>
                  <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Estratégias e Riscos</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {result.estrategias && (
                    <div>
                      <h4 className="font-semibold text-[#d4af37]/80 mb-2">Estratégias</h4>
                      <div className="text-[#f5f5dc]/90 leading-relaxed prose prose-invert prose-sm max-w-none prose-headings:text-[#d4af37] prose-strong:text-[#f5f5dc] prose-li:text-[#f5f5dc]/90"><ReactMarkdown>{result.estrategias}</ReactMarkdown></div>
                    </div>
                  )}
                  {result.riscos && (
                    <div>
                      <h4 className="font-semibold text-[#d4af37]/80 mb-2">Riscos</h4>
                      <div className="text-[#f5f5dc]/90 leading-relaxed prose prose-invert prose-sm max-w-none prose-headings:text-[#d4af37] prose-strong:text-[#f5f5dc] prose-li:text-[#f5f5dc]/90"><ReactMarkdown>{result.riscos}</ReactMarkdown></div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Probabilidade */}
            <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
              <CardHeader>
                <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Probabilidade de Êxito</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4 mb-3">
                  <span className={`text-3xl font-bold ${prob?.color}`}>{prob?.text}</span>
                  <div className="flex-1 h-3 bg-[#0a0a0a]/50 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        result.probabilidade === 'alta' ? 'bg-green-500 w-[85%]' :
                        result.probabilidade === 'media' ? 'bg-yellow-500 w-[55%]' :
                        'bg-red-500 w-[25%]'
                      }`}
                    />
                  </div>
                </div>
                {result.probabilidade_detalhes && (
                  <div className="text-[#f5f5dc]/70 text-sm prose prose-invert prose-sm max-w-none prose-p:text-[#f5f5dc]/70"><ReactMarkdown>{result.probabilidade_detalhes}</ReactMarkdown></div>
                )}
              </CardContent>
            </Card>

            {/* Custos e Prazos */}
            {(result.custos || result.prazos) && (
              <div className="grid md:grid-cols-2 gap-6">
                {result.custos && (
                  <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
                    <CardHeader>
                      <CardTitle className="text-[#d4af37] text-lg" style={{ fontFamily: "'Cinzel', serif" }}>Custos Estimados</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-[#f5f5dc]/90 prose prose-invert prose-sm max-w-none prose-headings:text-[#d4af37] prose-strong:text-[#f5f5dc] prose-li:text-[#f5f5dc]/90"><ReactMarkdown>{result.custos}</ReactMarkdown></div>
                    </CardContent>
                  </Card>
                )}
                {result.prazos && (
                  <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
                    <CardHeader>
                      <CardTitle className="text-[#d4af37] text-lg" style={{ fontFamily: "'Cinzel', serif" }}>Prazos Estimados</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-[#f5f5dc]/90 prose prose-invert prose-sm max-w-none prose-headings:text-[#d4af37] prose-strong:text-[#f5f5dc] prose-li:text-[#f5f5dc]/90"><ReactMarkdown>{result.prazos}</ReactMarkdown></div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}

            {/* Checklist */}
            {result.checklist && result.checklist.length > 0 && (
              <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
                <CardHeader>
                  <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Checklist de Documentos</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {result.checklist.map((item, i) => (
                      <li key={i} className="flex items-start gap-3 text-[#f5f5dc]/90">
                        <span className="text-[#d4af37] mt-0.5">&#9744;</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Citações */}
            {result.citacoes && result.citacoes.length > 0 && (
              <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
                <CardHeader>
                  <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>
                    Fundamentação Legal ({result.citacoes.length})
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {result.citacoes.map((cit, i) => (
                    <div key={cit.id || i} className="bg-[#0a0a0a]/40 p-4 rounded-lg border border-[#d4af37]/20">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs uppercase bg-[#d4af37]/20 text-[#d4af37] px-2 py-0.5 rounded font-semibold">
                          {cit.tipo}
                        </span>
                        <span className="text-[#f5f5dc] font-semibold text-sm">{cit.titulo}</span>
                      </div>
                      <p className="text-[#f5f5dc]/70 text-sm leading-relaxed">{cit.texto}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            {/* Rascunho de Petição */}
            {result.rascunho_peticao && (
              <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
                <CardHeader>
                  <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Rascunho de Petição</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-[#f5f5dc]/90 leading-relaxed bg-[#0a0a0a]/40 p-4 rounded-lg border border-[#d4af37]/20 prose prose-invert prose-sm max-w-none prose-headings:text-[#d4af37] prose-strong:text-[#f5f5dc] prose-li:text-[#f5f5dc]/90"><ReactMarkdown>{result.rascunho_peticao}</ReactMarkdown></div>
                </CardContent>
              </Card>
            )}

            {/* Relatório Premium + Nova Análise */}
            <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
              <CardContent className="pt-6 space-y-4">
                <div className="bg-[#d4af37]/10 p-6 rounded-lg border border-[#d4af37]/30 text-center">
                  <h3 className="text-xl font-bold mb-2 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Relatório Completo em PDF</h3>
                  <p className="mb-4 text-[#f5f5dc]/80">Análise detalhada com jurisprudência, estratégias e petição inicial</p>

                  {!showPayment ? (
                    <Button
                      className="w-full max-w-md bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold"
                      onClick={() => result?.case_id ? setShowPayment(true) : toast.error('Realize a análise primeiro')}
                      disabled={paymentLoading}
                    >
                      Gerar Relatório Premium - R$ 7,00
                    </Button>
                  ) : (
                    <div className="space-y-3 max-w-md mx-auto">
                      <p className="text-[#f5f5dc]/70 text-sm mb-3">Escolha a forma de pagamento:</p>
                      <Button
                        className="w-full bg-gradient-to-r from-[#635bff] to-[#7a73ff] text-white hover:from-[#7a73ff] hover:to-[#635bff] font-bold"
                        onClick={() => handleCheckout('stripe')}
                        disabled={paymentLoading}
                      >
                        {paymentLoading ? 'Redirecionando...' : 'Pagar com Cartão (Stripe)'}
                      </Button>
                      <Button
                        className="w-full bg-gradient-to-r from-[#00b4d8] to-[#0096c7] text-white hover:from-[#0096c7] hover:to-[#00b4d8] font-bold"
                        onClick={() => handleCheckout('mercadopago')}
                        disabled={paymentLoading}
                      >
                        {paymentLoading ? 'Redirecionando...' : 'Pagar com PIX (Mercado Pago)'}
                      </Button>
                      <button
                        className="text-[#f5f5dc]/50 text-sm hover:text-[#f5f5dc]/80 underline"
                        onClick={() => setShowPayment(false)}
                      >
                        Voltar
                      </button>
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2 text-[#f5f5dc]/50 text-xs justify-center">
                  <span>Base de dados atualizada em {result.base_atualizada_em}</span>
                  {result.case_id && <span>| Caso #{result.case_id}</span>}
                </div>

                <Button
                  variant="outline"
                  className="w-full text-[#d4af37] border-[#d4af37] hover:bg-[#d4af37]/15"
                  onClick={() => { setResult(null); setDescricao(''); setError(''); setShowPayment(false) }}
                >
                  Nova Análise
                </Button>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
