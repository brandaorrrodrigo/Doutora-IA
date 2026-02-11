'use client'

import Image from 'next/image'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { toast } from 'sonner'

export default function GeradorPage() {
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

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Gerador de Peças Jurídicas</h1>

        <div className="grid md:grid-cols-3 gap-4">
          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Inicial - Alimentos</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#f5f5dc]/70 mb-4 text-sm">Petição inicial para ação de alimentos</p>
              <Button
                className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold"
                onClick={() => toast.info('Gerador de peças em desenvolvimento')}
              >
                Gerar Peça
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Inicial - PIX</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#f5f5dc]/70 mb-4 text-sm">Petição para golpe via PIX</p>
              <Button
                className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold"
                onClick={() => toast.info('Gerador de peças em desenvolvimento')}
              >
                Gerar Peça
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Inicial - Plano de Saúde</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#f5f5dc]/70 mb-4 text-sm">Petição contra plano de saúde</p>
              <Button
                className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold"
                onClick={() => toast.info('Gerador de peças em desenvolvimento')}
              >
                Gerar Peça
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
