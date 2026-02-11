import Image from 'next/image'
import Link from 'next/link'

export default function TermosPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0a] via-[#1a1410] to-[#0a0a0a]">
      <header className="border-b border-[#d4af37]/20">
        <div className="container mx-auto px-4 py-4">
          <Link href="/" className="flex items-center space-x-3">
            <Image src="/logo-redonda.png" alt="Doutora IA" width={48} height={48} />
            <span className="text-xl font-bold text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Doutora IA</span>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold mb-8 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Termos de Uso</h1>

        <div className="space-y-8">
          <section className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>1. Aceite dos Termos</h2>
            <p className="text-[#f5f5dc]/80">Ao usar nossos serviços, você concorda com estes termos. Se não concordar, por favor não utilize a plataforma.</p>
          </section>

          <section className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>2. Natureza Informativa</h2>
            <p className="text-[#f5f5dc]/80">
              <strong className="text-[#d4af37]">IMPORTANTE:</strong> Este serviço possui caráter informativo e não substitui
              consulta com advogado qualificado. Não há garantia de êxito em nenhuma ação judicial.
            </p>
          </section>

          <section className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>3. Responsabilidades</h2>
            <p className="text-[#f5f5dc]/80">O usuário é responsável pela veracidade das informações fornecidas. A Doutora IA não se responsabiliza por decisões tomadas com base nas análises.</p>
          </section>

          <section className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>4. Pagamentos</h2>
            <p className="text-[#f5f5dc]/80">Relatórios premium são cobrados conforme tabela de preços vigente. Pagamentos são processados de forma segura.</p>
          </section>
        </div>

        <div className="mt-8 text-center">
          <Link href="/" className="text-[#d4af37] hover:underline">Voltar para a página inicial</Link>
        </div>
      </div>
    </div>
  )
}
