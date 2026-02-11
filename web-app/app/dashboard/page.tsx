'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { toast } from 'sonner'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')

    if (!token) {
      router.push('/auth/login')
      return
    }

    if (userData) {
      setUser(JSON.parse(userData))
    }
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/')
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0a] via-[#1a1410] to-[#0a0a0a]">
      <header className="border-b border-[#d4af37]/20">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center space-x-3">
            <Image src="/logo-redonda.png" alt="Doutora IA" width={48} height={48} />
            <span className="text-xl font-bold text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Doutora IA</span>
          </Link>
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="/analise" className="text-[#f5f5dc]/70 hover:text-[#d4af37] transition-colors text-sm">Análise</Link>
            <Link href="/advogado/pesquisa" className="text-[#f5f5dc]/70 hover:text-[#d4af37] transition-colors text-sm">Pesquisa</Link>
            <Link href="/advogado/gerador" className="text-[#f5f5dc]/70 hover:text-[#d4af37] transition-colors text-sm">Gerador</Link>
            <Link href="/advogado/leads" className="text-[#f5f5dc]/70 hover:text-[#d4af37] transition-colors text-sm">Leads</Link>
          </nav>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-[#f5f5dc]/60 hidden sm:inline">{user.email}</span>
            <Button variant="outline" className="text-[#d4af37] border-[#d4af37] hover:bg-[#d4af37]/15" onClick={handleLogout}>Sair</Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Meu Dashboard</h1>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Nova Análise</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#f5f5dc]/70 mb-4">
                Analisar um novo caso jurídico com IA
              </p>
              <Link href="/analise">
                <Button className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold">Analisar Caso</Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Meus Casos</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#f5f5dc]/70 mb-4">
                Ver histórico de análises
              </p>
              <Link href="/analise">
                <Button className="w-full text-[#d4af37] border-[#d4af37] hover:bg-[#d4af37]/15" variant="outline">
                  Ver Casos
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Relatórios</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#f5f5dc]/70 mb-4">
                Relatórios premium gerados
              </p>
              <Button
                className="w-full text-[#d4af37] border-[#d4af37] hover:bg-[#d4af37]/15"
                variant="outline"
                onClick={() => toast.info('Módulo de relatórios em desenvolvimento')}
              >
                Ver Relatórios
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Pesquisa Jurídica</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#f5f5dc]/70 mb-4">
                Buscar legislação e jurisprudência
              </p>
              <Link href="/advogado/pesquisa">
                <Button className="w-full text-[#d4af37] border-[#d4af37] hover:bg-[#d4af37]/15" variant="outline">
                  Pesquisar
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Gerador de Peças</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#f5f5dc]/70 mb-4">
                Gerar peças jurídicas com IA
              </p>
              <Link href="/advogado/gerador">
                <Button className="w-full text-[#d4af37] border-[#d4af37] hover:bg-[#d4af37]/15" variant="outline">
                  Gerar Peça
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
            <CardHeader>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Feed de Leads</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#f5f5dc]/70 mb-4">
                Casos disponíveis para advogados
              </p>
              <Link href="/advogado/leads">
                <Button className="w-full text-[#d4af37] border-[#d4af37] hover:bg-[#d4af37]/15" variant="outline">
                  Ver Leads
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Nav mobile */}
        <div className="md:hidden mt-8 grid grid-cols-2 gap-3">
          <Link href="/analise">
            <Button variant="outline" className="w-full text-[#d4af37] border-[#d4af37]/40 hover:bg-[#d4af37]/15 text-sm">Análise</Button>
          </Link>
          <Link href="/advogado/pesquisa">
            <Button variant="outline" className="w-full text-[#d4af37] border-[#d4af37]/40 hover:bg-[#d4af37]/15 text-sm">Pesquisa</Button>
          </Link>
          <Link href="/advogado/gerador">
            <Button variant="outline" className="w-full text-[#d4af37] border-[#d4af37]/40 hover:bg-[#d4af37]/15 text-sm">Gerador</Button>
          </Link>
          <Link href="/advogado/leads">
            <Button variant="outline" className="w-full text-[#d4af37] border-[#d4af37]/40 hover:bg-[#d4af37]/15 text-sm">Leads</Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
