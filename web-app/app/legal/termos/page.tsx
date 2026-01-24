import Link from 'next/link'

export default function TermosPage() {
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
        <h1 className="text-4xl font-bold mb-8">Termos de Uso</h1>
        
        <div className="prose max-w-none space-y-6 text-gray-700">
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Aceite dos Termos</h2>
            <p>Ao usar nossos serviços, você concorda com estes termos.</p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Natureza Informativa</h2>
            <p>
              <strong>IMPORTANTE:</strong> Este serviço possui caráter informativo e não substitui 
              consulta com advogado qualificado. Não há garantia de êxito.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">3. Responsabilidades</h2>
            <p>O usuário é responsável pela veracidade das informações fornecidas.</p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">4. Pagamentos</h2>
            <p>Relatórios premium são cobrados conforme tabela de preços vigente.</p>
          </section>
        </div>
      </div>
    </div>
  )
}
