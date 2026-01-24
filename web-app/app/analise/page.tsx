'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import Link from 'next/link'

export default function AnalisePage() {
  const [descricao, setDescricao] = useState('')
  const [result, setResult] = useState<any>(null)

  const analyzeMutation = useMutation({
    mutationFn: (desc: string) => apiClient.analyzeCase(desc, false),
    onSuccess: (response) => setResult(response.data),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (descricao.trim().length < 50) return
    analyzeMutation.mutate(descricao)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0d2818] to-[#1b3d29]">
      <header className="container mx-auto px-4 py-6">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-4xl">⚖️</span>
          <span className="text-2xl font-bold text-white">Doutora IA</span>
        </Link>
      </header>

      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold text-white text-center mb-8">
          Análise Jurídica Inteligente
        </h1>

        {!result && (
          <Card>
            <CardHeader>
              <CardTitle>Descreva seu caso</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label>Descrição do Caso</Label>
                  <Textarea
                    value={descricao}
                    onChange={(e) => setDescricao(e.target.value)}
                    rows={8}
                    placeholder="Descreva seu problema juridico..."
                  />
                  <div className="text-sm text-gray-500 mt-1">
                    {descricao.length} caracteres (minimo 50)
                  </div>
                </div>
                <Button type="submit" className="w-full" disabled={analyzeMutation.isPending}>
                  {analyzeMutation.isPending ? 'Analisando...' : 'Analisar Caso'}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {result && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Análise do Seu Caso</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Tipificação</h3>
                  <p className="text-gray-700">{result.tipificacao}</p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Probabilidade</h3>
                  <p className="text-gray-700">{result.probabilidade}</p>
                </div>
                <div className="bg-green-50 p-6 rounded-lg">
                  <h3 className="text-xl font-bold mb-2">Relatório Completo</h3>
                  <p className="mb-4">Por apenas R$ 7,00 você recebe o relatório completo em PDF</p>
                  <Button className="w-full">Gerar Relatório Premium - R$ 7,00</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
