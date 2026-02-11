'use client'

import Image from 'next/image'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { toast } from 'sonner'

export default function LeadsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0a] via-[#1a1410] to-[#0a0a0a]">
      <header className="border-b border-[#d4af37]/20">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center space-x-3">
            <Image src="/logo-redonda.png" alt="Doutora IA" width={48} height={48} />
            <span className="text-xl font-bold text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Doutora IA</span>
          </Link>
          <Link href="/dashboard">
            <Button variant="outline" className="text-[#d4af37] border-[#d4af37] hover:bg-[#d4af37]/15">Dashboard</Button>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Feed de Leads</h1>

        <div className="space-y-4">
          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Caso: Pensão Alimentícia</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#f5f5dc]/70 mb-4">
                Área: Família | Probabilidade: Média | Valor estimado: R$ 5.000
              </p>
              <Button
                className="bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold"
                onClick={() => toast.info('Módulo de leads em desenvolvimento')}
              >
                Aceitar Lead
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Caso: Golpe PIX</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#f5f5dc]/70 mb-4">
                Área: Criminal/Cível | Probabilidade: Alta | Valor estimado: R$ 3.200
              </p>
              <Button
                className="bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold"
                onClick={() => toast.info('Módulo de leads em desenvolvimento')}
              >
                Aceitar Lead
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Caso: Plano de Saúde</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#f5f5dc]/70 mb-4">
                Área: Consumidor | Probabilidade: Alta | Valor estimado: R$ 15.000
              </p>
              <Button
                className="bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold"
                onClick={() => toast.info('Módulo de leads em desenvolvimento')}
              >
                Aceitar Lead
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
