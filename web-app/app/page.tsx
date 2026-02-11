'use client'

import Link from 'next/link'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0a] via-[#1a1410] to-[#0a0a0a]">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Image src="/logo-redonda.png" alt="Doutora IA" width={48} height={48} />
            <span className="text-2xl font-bold text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Doutora IA</span>
          </div>
          <div className="flex items-center space-x-4">
            <Link href="/auth/login">
              <Button variant="ghost" className="text-[#f5f5dc] hover:bg-[#d4af37]/10 hover:text-[#d4af37] border border-[#d4af37]/30">
                Entrar
              </Button>
            </Link>
            <Link href="/auth/register">
              <Button className="bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold shadow-lg shadow-[#d4af37]/20">
                Começar Grátis
              </Button>
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="flex justify-center">
            <Image
              src="/logo-brilhante.png"
              alt="Doutora IA"
              width={280}
              height={280}
              className="animate-[glow-pulse_3s_ease-in-out_infinite]"
              priority
            />
          </div>

          <h1 className="text-5xl md:text-6xl font-bold text-[#f5f5dc] leading-tight" style={{ fontFamily: "'Cinzel', serif" }}>
            Inteligência Jurídica
            <br />
            <span className="text-[#d4af37]">em Minutos</span>
          </h1>

          <p className="text-xl text-[#f5f5dc]/80 max-w-2xl mx-auto">
            A maior plataforma de inteligência jurídica do Brasil. Relatórios com IA e RAG,
            baseados em legislação vigente, jurisprudência e doutrina.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/analise">
              <Button size="lg" className="bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] text-lg px-8 py-6 font-bold shadow-lg shadow-[#d4af37]/20" style={{ fontFamily: "'Cinzel', serif" }}>
                Analisar Meu Caso
              </Button>
            </Link>
            <Link href="/auth/register">
              <Button size="lg" variant="outline" className="text-[#d4af37] border-2 border-[#d4af37] hover:bg-[#d4af37]/15 text-lg px-8 py-6" style={{ fontFamily: "'Cinzel', serif" }}>
                Sou Advogado
              </Button>
            </Link>
          </div>

          <div className="flex items-center justify-center space-x-8 text-sm text-[#f5f5dc]/60">
            <div className="flex items-center space-x-2">
              <span className="text-[#d4af37]">✓</span>
              <span>25 áreas jurídicas</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-[#d4af37]">✓</span>
              <span>+2.500 obras jurídicas</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-[#d4af37]">✓</span>
              <span>100% baseado em fontes</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-br from-[#d4af37]/5 to-[#d4af37]/[0.02] border-2 border-[#d4af37]/40 backdrop-blur-sm hover:border-[#d4af37] hover:shadow-lg hover:shadow-[#d4af37]/20 transition-all duration-300 hover:-translate-y-1">
            <CardHeader>
              <div className="text-4xl mb-2">🔍</div>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Pesquisa Inteligente</CardTitle>
              <CardDescription className="text-[#f5f5dc]/70">
                Busca unificada em legislação, súmulas, temas STJ/STF e jurisprudência
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-gradient-to-br from-[#d4af37]/5 to-[#d4af37]/[0.02] border-2 border-[#d4af37]/40 backdrop-blur-sm hover:border-[#d4af37] hover:shadow-lg hover:shadow-[#d4af37]/20 transition-all duration-300 hover:-translate-y-1">
            <CardHeader>
              <div className="text-4xl mb-2">📊</div>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Relatórios Premium</CardTitle>
              <CardDescription className="text-[#f5f5dc]/70">
                Tipificação, probabilidade, custos, prazos, checklist e rascunho de petição
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-gradient-to-br from-[#d4af37]/5 to-[#d4af37]/[0.02] border-2 border-[#d4af37]/40 backdrop-blur-sm hover:border-[#d4af37] hover:shadow-lg hover:shadow-[#d4af37]/20 transition-all duration-300 hover:-translate-y-1">
            <CardHeader>
              <div className="text-4xl mb-2">⚡</div>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Sem Alucinação</CardTitle>
              <CardDescription className="text-[#f5f5dc]/70">
                Todas as citações vêm do RAG. Sistema anti-alucinação por design
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-gradient-to-br from-[#d4af37]/5 to-[#d4af37]/[0.02] border-2 border-[#d4af37]/40 backdrop-blur-sm hover:border-[#d4af37] hover:shadow-lg hover:shadow-[#d4af37]/20 transition-all duration-300 hover:-translate-y-1">
            <CardHeader>
              <div className="text-4xl mb-2">👨‍⚖️</div>
              <CardTitle className="text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Modo Advogado</CardTitle>
              <CardDescription className="text-[#f5f5dc]/70">
                Gerador de peças profissionais com carrinho de citações
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-3xl mx-auto space-y-6 bg-gradient-to-br from-[#d4af37]/10 to-[#d4af37]/[0.02] backdrop-blur-sm rounded-2xl p-12 border-2 border-[#d4af37]/40">
          <h2 className="text-4xl font-bold text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>
            Pronto para começar?
          </h2>
          <p className="text-xl text-[#f5f5dc]/80">
            Análise gratuita do seu caso. Relatório premium por apenas R$ 7,00.
          </p>
          <Link href="/analise">
            <Button size="lg" className="bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] text-lg px-8 py-6 font-bold shadow-lg shadow-[#d4af37]/20" style={{ fontFamily: "'Cinzel', serif" }}>
              Analisar Meu Caso Agora
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 border-t-2 border-[#d4af37]/30">
        <div className="flex flex-col md:flex-row justify-between items-center text-[#f5f5dc]/50 text-sm">
          <div className="flex items-center space-x-2 mb-4 md:mb-0">
            <Image src="/logo-redonda.png" alt="Doutora IA" width={24} height={24} />
            <span>© 2026 Doutora IA. Todos os direitos reservados.</span>
          </div>
          <div className="flex space-x-6">
            <Link href="/legal/privacidade" className="hover:text-[#d4af37]">
              Privacidade
            </Link>
            <Link href="/legal/termos" className="hover:text-[#d4af37]">
              Termos de Uso
            </Link>
            <a href="mailto:contato@doutora-ia.com.br" className="hover:text-[#d4af37]">
              Contato
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
