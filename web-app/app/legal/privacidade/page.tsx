import Link from 'next/link'

export default function PrivacidadePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-3xl">⚖️</span>
            <span className="text-xl font-bold">Doutora IA</span>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold mb-8">Política de Privacidade</h1>
        
        <div className="prose max-w-none space-y-6 text-gray-700">
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Coleta de Dados</h2>
            <p>Coletamos apenas os dados necessários para fornecer nossos serviços.</p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Uso dos Dados</h2>
            <p>Seus dados são usados exclusivamente para análise jurídica e geração de relatórios.</p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">3. LGPD</h2>
            <p>Estamos em conformidade com a Lei Geral de Proteção de Dados (LGPD).</p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">4. Direitos do Titular</h2>
            <p>Você tem direito a acessar, corrigir e excluir seus dados a qualquer momento.</p>
          </section>
        </div>
      </div>
    </div>
  )
}
