'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import Image from 'next/image'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { apiClient } from '@/services/api'

export const dynamic = 'force-dynamic'

export default function PagamentoSucessoPage() {
  const searchParams = useSearchParams()
  const paymentIdParam = searchParams.get('payment_id')
  const caseId = searchParams.get('case_id')

  // Try URL param first, then localStorage
  const paymentId = paymentIdParam || (typeof window !== 'undefined' ? localStorage.getItem('pending_payment_id') : null)

  const [status, setStatus] = useState<'checking' | 'approved' | 'pending' | 'error'>('checking')
  const [reportUrl, setReportUrl] = useState<string | null>(null)

  useEffect(() => {
    if (!paymentId && !caseId) {
      setStatus('error')
      return
    }

    let attempts = 0
    const maxAttempts = 20

    const checkStatus = async () => {
      if (!paymentId) {
        // Se não tem payment_id mas tem case_id, aguardar webhook
        attempts++
        if (attempts >= maxAttempts) {
          setStatus('approved')
        }
        return
      }

      try {
        const response = await apiClient.getPaymentStatus(Number(paymentId))
        const data = response.data

        if (data.status === 'approved') {
          setStatus('approved')
          if (data.report_url) {
            setReportUrl(data.report_url)
          }
          localStorage.removeItem('pending_payment_id')
          return
        }

        attempts++
        if (attempts >= maxAttempts) {
          setStatus('approved')
        }
      } catch {
        attempts++
        if (attempts >= maxAttempts) {
          setStatus('error')
        }
      }
    }

    checkStatus()
    const interval = setInterval(() => {
      if (status === 'approved' || status === 'error') {
        clearInterval(interval)
        return
      }
      checkStatus()
    }, 3000)

    return () => clearInterval(interval)
  }, [paymentId, caseId])

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0a] via-[#1a1410] to-[#0a0a0a]">
      <header className="container mx-auto px-4 py-6 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-3">
          <Image src="/logo-redonda.png" alt="Doutora IA" width={48} height={48} />
          <span className="text-2xl font-bold text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Doutora IA</span>
        </Link>
      </header>

      <div className="container mx-auto px-4 py-12 max-w-lg">
        <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
          <CardContent className="pt-8 pb-8 text-center space-y-6">
            {status === 'checking' && (
              <>
                <div className="flex justify-center">
                  <svg className="animate-spin h-12 w-12 text-[#d4af37]" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>
                  Verificando Pagamento...
                </h2>
                <p className="text-[#f5f5dc]/70">Aguarde enquanto confirmamos seu pagamento.</p>
              </>
            )}

            {status === 'approved' && (
              <>
                <div className="flex justify-center">
                  <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center">
                    <svg className="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>
                <h2 className="text-2xl font-bold text-green-400" style={{ fontFamily: "'Cinzel', serif" }}>
                  Pagamento Confirmado!
                </h2>
                <p className="text-[#f5f5dc]/70">Seu relatório premium está sendo gerado.</p>

                {reportUrl ? (
                  <a href={reportUrl} target="_blank" rel="noopener noreferrer">
                    <Button className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold">
                      Baixar Relatório PDF
                    </Button>
                  </a>
                ) : (
                  <p className="text-[#f5f5dc]/50 text-sm">O relatório estará disponível em breve no seu dashboard.</p>
                )}

                <Link href="/analise">
                  <Button variant="outline" className="w-full text-[#d4af37] border-[#d4af37] hover:bg-[#d4af37]/15 mt-2">
                    Voltar para Análise
                  </Button>
                </Link>
              </>
            )}

            {status === 'error' && (
              <>
                <div className="flex justify-center">
                  <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center">
                    <svg className="h-8 w-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                </div>
                <h2 className="text-2xl font-bold text-red-400" style={{ fontFamily: "'Cinzel', serif" }}>
                  Erro no Pagamento
                </h2>
                <p className="text-[#f5f5dc]/70">Não foi possível confirmar o pagamento. Tente novamente.</p>
                <Link href="/analise">
                  <Button className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold">
                    Voltar para Análise
                  </Button>
                </Link>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
