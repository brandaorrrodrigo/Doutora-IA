'use client'

import { useState } from 'react'
import Image from 'next/image'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import Link from 'next/link'
import { toast } from 'sonner'

export default function PesquisaPage() {
  const [query, setQuery] = useState('')

  const handleSearch = () => {
    if (!query.trim()) {
      toast.error('Digite um termo para pesquisar')
      return
    }
    toast.info('Módulo de pesquisa jurídica em desenvolvimento')
  }

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
        <h1 className="text-3xl font-bold mb-8 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Pesquisa Jurídica</h1>

        <Card className="mb-6 bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
          <CardContent className="pt-6">
            <div className="flex gap-2">
              <Input
                placeholder="Buscar legislação, súmulas, jurisprudência..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="bg-[#0a0a0a]/50 border-[#d4af37]/30 text-[#f5f5dc] placeholder:text-[#f5f5dc]/40"
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button
                className="bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold"
                onClick={handleSearch}
              >
                Pesquisar
              </Button>
            </div>
          </CardContent>
        </Card>

        <p className="text-[#f5f5dc]/50 text-center">
          Digite sua consulta para buscar em 6 coleções jurídicas
        </p>
      </div>
    </div>
  )
}
