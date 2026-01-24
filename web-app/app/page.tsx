import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0d2818] via-[#1b3d29] to-[#0d2818]">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-4xl">⚖️</span>
            <span className="text-2xl font-bold text-white">Doutora IA</span>
          </div>
          <div className="flex items-center space-x-4">
            <Link href="/auth/login">
              <Button variant="ghost" className="text-white hover:bg-white/10">
                Entrar
              </Button>
            </Link>
            <Link href="/auth/register">
              <Button className="bg-white text-[#1b3d29] hover:bg-white/90">
                Começar Grátis
              </Button>
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="text-7xl animate-bounce">⚖️</div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-white leading-tight">
            Análise Jurídica Inteligente
            <br />
            <span className="text-green-300">em Minutos</span>
          </h1>
          
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Relatórios detalhados com IA e RAG. Baseados em legislação vigente,
            jurisprudência e doutrina. Sem alucinações.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/analise">
              <Button size="lg" className="bg-white text-[#1b3d29] hover:bg-white/90 text-lg px-8 py-6">
                Analisar Meu Caso
              </Button>
            </Link>
            <Link href="/advogado">
              <Button size="lg" variant="outline" className="text-white border-white hover:bg-white/10 text-lg px-8 py-6">
                Sou Advogado
              </Button>
            </Link>
          </div>

          <div className="flex items-center justify-center space-x-8 text-sm text-gray-400">
            <div className="flex items-center space-x-2">
              <span className="text-green-400">✓</span>
              <span>Sem cadastro para análise</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-green-400">✓</span>
              <span>Relatório Premium R$ 7</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-green-400">✓</span>
              <span>100% baseado em fontes</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
            <CardHeader>
              <div className="text-4xl mb-2">🔍</div>
              <CardTitle className="text-white">Pesquisa Inteligente</CardTitle>
              <CardDescription className="text-gray-300">
                Busca unificada em legislação, súmulas, temas STJ/STF e jurisprudência
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
            <CardHeader>
              <div className="text-4xl mb-2">📊</div>
              <CardTitle className="text-white">Relatórios Premium</CardTitle>
              <CardDescription className="text-gray-300">
                Tipificação, probabilidade, custos, prazos, checklist e rascunho de petição
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
            <CardHeader>
              <div className="text-4xl mb-2">⚡</div>
              <CardTitle className="text-white">Sem Alucinação</CardTitle>
              <CardDescription className="text-gray-300">
                Todas as citações vêm do RAG. Sistema anti-alucinação por design
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
            <CardHeader>
              <div className="text-4xl mb-2">👨‍⚖️</div>
              <CardTitle className="text-white">Modo Advogado</CardTitle>
              <CardDescription className="text-gray-300">
                Gerador de peças profissionais com carrinho de citações
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-3xl mx-auto space-y-6 bg-white/10 backdrop-blur-sm rounded-2xl p-12 border border-white/20">
          <h2 className="text-4xl font-bold text-white">
            Pronto para começar?
          </h2>
          <p className="text-xl text-gray-300">
            Análise gratuita do seu caso. Relatório premium por apenas R$ 7,00.
          </p>
          <Link href="/analise">
            <Button size="lg" className="bg-white text-[#1b3d29] hover:bg-white/90 text-lg px-8 py-6">
              Analisar Meu Caso Agora
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 border-t border-white/10">
        <div className="flex flex-col md:flex-row justify-between items-center text-gray-400 text-sm">
          <div className="mb-4 md:mb-0">
            © 2024 Doutora IA. Todos os direitos reservados.
          </div>
          <div className="flex space-x-6">
            <Link href="/legal/privacidade" className="hover:text-white">
              Privacidade
            </Link>
            <Link href="/legal/termos" className="hover:text-white">
              Termos de Uso
            </Link>
            <a href="mailto:contato@doutora-ia.com.br" className="hover:text-white">
              Contato
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
