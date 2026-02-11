import Image from 'next/image'
import Link from 'next/link'

export default function PrivacidadePage() {
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
        <h1 className="text-4xl font-bold mb-8 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Política de Privacidade</h1>

        <div className="space-y-8">
          <section className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>1. Coleta de Dados</h2>
            <p className="text-[#f5f5dc]/80">Coletamos apenas os dados necessários para fornecer nossos serviços, incluindo nome, email e informações do caso jurídico que você nos apresentar.</p>
          </section>

          <section className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>2. Uso dos Dados</h2>
            <p className="text-[#f5f5dc]/80">Seus dados são usados exclusivamente para análise jurídica e geração de relatórios. Não compartilhamos informações pessoais com terceiros.</p>
          </section>

          <section className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>3. LGPD</h2>
            <p className="text-[#f5f5dc]/80">Estamos em conformidade com a Lei Geral de Proteção de Dados (LGPD - Lei 13.709/2018). Seus dados são armazenados de forma segura e criptografada.</p>
          </section>

          <section className="bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>4. Direitos do Titular</h2>
            <p className="text-[#f5f5dc]/80">Você tem direito a acessar, corrigir e excluir seus dados a qualquer momento. Para exercer esses direitos, entre em contato conosco.</p>
          </section>
        </div>

        <div className="mt-8 text-center">
          <Link href="/" className="text-[#d4af37] hover:underline">Voltar para a página inicial</Link>
        </div>
      </div>
    </div>
  )
}
