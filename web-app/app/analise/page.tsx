'use client'

import { useState } from 'react'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import Link from 'next/link'

export default function AnalisePage() {
  const [descricao, setDescricao] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (descricao.trim().length < 50) {
      setError('Descreva seu caso com pelo menos 50 caracteres para uma análise adequada.')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('/api/auth/me')
      if (!response.ok) {
        setError('Faça login para acessar a análise completa.')
        setLoading(false)
        return
      }
      setResult({
        tipificacao: 'Análise em desenvolvimento. O módulo de IA será ativado em breve.',
        probabilidade: 'A funcionalidade de análise de risco está sendo implementada.',
      })
    } catch {
      setResult({
        tipificacao: 'Análise em desenvolvimento. O módulo de IA será ativado em breve.',
        probabilidade: 'A funcionalidade de análise de risco está sendo implementada.',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0a] via-[#1a1410] to-[#0a0a0a]">
      <header className="container mx-auto px-4 py-6">
        <Link href="/" className="flex items-center space-x-3">
          <Image src="/logo-redonda.png" alt="Doutora IA" width={48} height={48} />
          <span className="text-2xl font-bold text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Doutora IA</span>
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
                  className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold"
                  disabled={loading}
                >
                  {loading ? 'Analisando...' : 'Analisar Caso'}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {result && (
          <div className="space-y-6">
            <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
              <CardHeader>
                <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Análise do Seu Caso</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2 text-[#d4af37]">Tipificação</h3>
                  <p className="text-[#f5f5dc]/80">{result.tipificacao}</p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2 text-[#d4af37]">Probabilidade</h3>
                  <p className="text-[#f5f5dc]/80">{result.probabilidade}</p>
                </div>
                <div className="bg-[#d4af37]/10 p-6 rounded-lg border border-[#d4af37]/30">
                  <h3 className="text-xl font-bold mb-2 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Relatório Completo</h3>
                  <p className="mb-4 text-[#f5f5dc]/80">Por apenas R$ 7,00 você recebe o relatório completo em PDF</p>
                  <Button className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold">
                    Gerar Relatório Premium - R$ 7,00
                  </Button>
                </div>
                <Button
                  variant="outline"
                  className="w-full text-[#d4af37] border-[#d4af37] hover:bg-[#d4af37]/15"
                  onClick={() => { setResult(null); setDescricao('') }}
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
