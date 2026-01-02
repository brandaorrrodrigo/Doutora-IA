'use client';
import Link from 'next/link';
import Image from 'next/image';

export default function HomePage() {
  return (
    <>
      <style jsx global>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Georgia', 'Times New Roman', serif; background: #0a0a0a; color: #f5f5dc; line-height: 1.8; }

        header { text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #1a1410, #2d1f17); border-bottom: 2px solid #d4af37; }
        header .logo { margin-bottom: 20px; }
        header h1 { font-size: 2.8em; color: #d4af37; font-weight: 400; letter-spacing: 2px; margin: 10px 0; }
        header .subtitle { font-size: 1.3em; color: #f5f5dc; margin: 15px 0; }
        header .stats { font-size: 1em; color: #d4af37; margin-top: 20px; font-weight: 300; }

        .cta { display: inline-block; padding: 16px 40px; margin: 10px; background: #d4af37; color: #1a1410; text-decoration: none; border-radius: 6px; font-weight: 600; transition: all 0.3s; }
        .cta:hover { background: #b8860b; transform: translateY(-2px); }
        .cta-outline { background: transparent; border: 2px solid #d4af37; color: #d4af37; }
        .cta-outline:hover { background: rgba(212, 175, 55, 0.1); }

        .container { max-width: 1200px; margin: 0 auto; padding: 60px 40px; }

        .authority { background: linear-gradient(135deg, #1a1410, #2d1f17); padding: 50px 40px; border-radius: 8px; margin: 40px 0; border: 1px solid #d4af37; }
        .authority h2 { color: #d4af37; font-size: 2.2em; margin-bottom: 30px; text-align: center; font-weight: 400; }
        .authority-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; margin-top: 30px; }
        .authority-item { text-align: center; padding: 20px; background: rgba(212, 175, 55, 0.05); border-radius: 6px; }
        .authority-item .number { font-size: 2.5em; color: #d4af37; font-weight: 600; }
        .authority-item .label { font-size: 1em; color: #f5f5dc; margin-top: 10px; }

        .section { margin: 60px 0; }
        .section h2 { color: #d4af37; font-size: 2.2em; margin-bottom: 40px; text-align: center; font-weight: 400; border-bottom: 2px solid #d4af37; padding-bottom: 15px; }

        .feature-item { margin: 30px 0; padding: 25px; background: rgba(212, 175, 55, 0.03); border-left: 3px solid #d4af37; border-radius: 4px; }
        .feature-item h3 { color: #d4af37; font-size: 1.4em; margin-bottom: 15px; font-weight: 500; }
        .feature-item p { color: #f5f5dc; font-size: 1em; line-height: 1.7; }

        .differentials { background: linear-gradient(135deg, #2d1f17, #1a1410); padding: 50px 40px; border-radius: 8px; margin: 60px 0; }
        .differentials h2 { color: #d4af37; text-align: center; margin-bottom: 40px; font-size: 2.2em; }
        .differential-item { margin: 25px 0; padding: 20px; background: rgba(212, 175, 55, 0.05); border-radius: 6px; }
        .differential-item h3 { color: #d4af37; font-size: 1.3em; margin-bottom: 10px; }
        .differential-item p { color: #f5f5dc; }

        .transparency { background: rgba(212, 175, 55, 0.08); padding: 40px; border-radius: 8px; margin: 40px 0; text-align: center; border: 1px solid #d4af37; }
        .transparency h2 { color: #d4af37; margin-bottom: 20px; }
        .transparency p { color: #f5f5dc; font-size: 1.1em; line-height: 1.8; }

        .final-cta { text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #1a1410, #2d1f17); border-radius: 8px; margin: 60px 0; }
        .final-cta h2 { color: #d4af37; font-size: 2.5em; margin-bottom: 20px; }
        .final-cta p { color: #f5f5dc; font-size: 1.2em; margin-bottom: 30px; }

        footer { background: #1a1410; color: #f5f5dc; text-align: center; padding: 40px 20px; margin-top: 80px; border-top: 2px solid #d4af37; }
        footer p { margin: 10px 0; font-size: 0.95em; }
      `}</style>

      <header>
        <div className="logo">
          <Image src="/logodoutoraia.png" alt="Doutora IA" width={120} height={120} priority />
        </div>
        <h1>DOUTORA IA</h1>
        <p className="subtitle">A maior plataforma de inteligência jurídica já construída no Brasil</p>
        <p className="stats">1.326 engines jurídicas · 15 áreas do Direito · 539 PDFs de jurisprudência processados</p>
        <div style={{marginTop: '30px'}}>
          <Link href="/pricing" className="cta">VER PLANOS</Link>
          <Link href="/login" className="cta cta-outline">ENTRAR</Link>
        </div>
      </header>

      <div className="container">
        <section className="authority">
          <h2>Autoridade em Números</h2>
          <div className="authority-grid">
            <div className="authority-item">
              <div className="number">1.326</div>
              <div className="label">Engines Jurídicas Especializadas</div>
            </div>
            <div className="authority-item">
              <div className="number">15</div>
              <div className="label">Áreas do Direito Cobertas</div>
            </div>
            <div className="authority-item">
              <div className="number">539</div>
              <div className="label">PDFs de Jurisprudência Processados</div>
            </div>
            <div className="authority-item">
              <div className="number">100%</div>
              <div className="label">Gratuito para Cidadãos</div>
            </div>
          </div>
        </section>

        <section className="section">
          <h2>Para Advogados: Poder Profissional</h2>
          <div>
            <div className="feature-item">
              <h3>1. Automação Total de Petições</h3>
              <p>Gere petições iniciais, contestações, recursos e manifestações em segundos. Cada engine conhece profundamente sua área específica do Direito.</p>
            </div>
            <div className="feature-item">
              <h3>2. Calculadoras Jurídicas Especializadas</h3>
              <p>Cálculos trabalhistas, previdenciários, civis e tributários com precisão matemática. Atualizações automáticas de índices e tabelas.</p>
            </div>
            <div className="feature-item">
              <h3>3. Análise de Risco com IA</h3>
              <p>Avalie viabilidade de ações antes de entrar. A IA analisa jurisprudência, chances de êxito e riscos potenciais.</p>
            </div>
            <div className="feature-item">
              <h3>4. Dashboard de Performance</h3>
              <p>Métricas em tempo real: processos ativos, prazos críticos, taxa de sucesso por área, faturamento estimado e muito mais.</p>
            </div>
            <div className="feature-item">
              <h3>5. Alertas Inteligentes de Prazos</h3>
              <p>Nunca perca um prazo processual. Sistema integrado com tribunais monitora automaticamente suas ações.</p>
            </div>
            <div className="feature-item">
              <h3>6. Busca em 539 Fontes de Jurisprudência</h3>
              <p>Encontre precedentes relevantes instantaneamente. A IA contextualiza e sugere as decisões mais aplicáveis ao seu caso.</p>
            </div>
            <div className="feature-item">
              <h3>7. Marketplace Jurídico Integrado</h3>
              <p>Conecte-se com peritos, tradutores juramentados e outros profissionais. Sistema de reputação e pagamento integrado.</p>
            </div>
            <div className="feature-item">
              <h3>8. CRM Jurídico Completo</h3>
              <p>Gestão de leads, clientes e processos em um só lugar. Automação de follow-ups e propostas comerciais.</p>
            </div>
            <div className="feature-item">
              <h3>9. Perfil Profissional Público</h3>
              <p>Página otimizada para SEO com suas especializações, cases de sucesso e avaliações de clientes.</p>
            </div>
            <div className="feature-item">
              <h3>10. Relatórios Executivos Automáticos</h3>
              <p>Envie atualizações mensais aos clientes automaticamente. Transparência que gera confiança e retenção.</p>
            </div>
          </div>
        </section>

        <section className="section">
          <h2>Para Cidadãos: Justiça Acessível</h2>
          <div>
            <div className="feature-item">
              <h3>1. Triagem Jurídica Gratuita</h3>
              <p>Conte seu problema e a IA identifica: qual área do Direito, se você tem razão, qual ação cabível e estimativa de custos.</p>
            </div>
            <div className="feature-item">
              <h3>2. Gerador de Documentos Básicos</h3>
              <p>Notificações extrajudiciais, reclamações ao Procon, requerimentos administrativos - tudo gratuito e juridicamente válido.</p>
            </div>
            <div className="feature-item">
              <h3>3. Chat Jurídico 24/7</h3>
              <p>Tire dúvidas básicas a qualquer hora. A IA explica conceitos jurídicos em linguagem simples e direciona aos próximos passos.</p>
            </div>
            <div className="feature-item">
              <h3>4. Busca de Advogados Especializados</h3>
              <p>Sistema de matching que conecta você ao profissional ideal para o seu caso. Transparência de preços e avaliações reais.</p>
            </div>
            <div className="feature-item">
              <h3>5. Educação Jurídica Gratuita</h3>
              <p>Biblioteca com guias sobre direitos do consumidor, trabalhista, previdenciário e muito mais. Linguagem acessível a todos.</p>
            </div>
            <div className="feature-item">
              <h3>6. Calculadoras Públicas</h3>
              <p>Calcule valores de FGTS, INSS, indenizações trabalhistas e outros direitos. Ferramenta gratuita e sem necessidade de cadastro.</p>
            </div>
            <div className="feature-item">
              <h3>7. Verificador de Prescrição</h3>
              <p>Descubra se seu direito ainda pode ser cobrado judicialmente. A IA analisa prazos prescricionais de todas as áreas.</p>
            </div>
            <div className="feature-item">
              <h3>8. Modelos de Petições para Tribunais</h3>
              <p>Acesso gratuito a modelos validados para Juizados Especiais. Autonomia para casos simples que não exigem advogado.</p>
            </div>
            <div className="feature-item">
              <h3>9. Acompanhamento de Processos</h3>
              <p>Monitore processos judiciais gratuitamente. Receba alertas de movimentações e explique em português claro o que aconteceu.</p>
            </div>
            <div className="feature-item">
              <h3>10. Biblioteca de Jurisprudência Aberta</h3>
              <p>Consulte decisões judiciais que podem apoiar seu caso. Busca simplificada por assunto, não por jargão técnico.</p>
            </div>
          </div>
        </section>

        <section className="differentials">
          <h2>Por Que a Doutora IA é Diferente</h2>
          <div className="differential-item">
            <h3>Mais Completa</h3>
            <p>Não é só chatbot. São 1.326 engines especializadas, cada uma expert em um problema jurídico específico. Da triagem à execução.</p>
          </div>
          <div className="differential-item">
            <h3>IA de Verdade</h3>
            <p>Processamos 539 PDFs de jurisprudência e legislação. A IA não inventa - ela busca em fontes reais e cita as referências.</p>
          </div>
          <div className="differential-item">
            <h3>Democratiza o Direito</h3>
            <p>Cidadãos têm acesso gratuito a ferramentas que antes custavam milhares. Advogados ganham tecnologia de ponta a preço justo.</p>
          </div>
          <div className="differential-item">
            <h3>Privacidade Real</h3>
            <p>Seus dados não são vendidos. Não há anúncios. O modelo de negócio é transparente: assinaturas de advogados financiam o acesso gratuito de cidadãos.</p>
          </div>
          <div className="differential-item">
            <h3>Preço Justo</h3>
            <p>R$ 197/mês para advogados. Sem taxas ocultas, sem limites artificiais. Acesso ilimitado a todas as 1.326 engines.</p>
          </div>
        </section>

        <section className="transparency">
          <h2>Transparência Total</h2>
          <p>Estamos em fase de testes. Alguns recursos ainda estão sendo calibrados. Não há depoimentos falsos aqui - preferimos honestidade a marketing enganoso.</p>
          <p>Se encontrar bugs ou tiver sugestões, queremos ouvir. Esta plataforma está sendo construída COM advogados e cidadãos, não apenas PARA eles.</p>
        </section>

        <section className="final-cta">
          <h2>Experimente Gratuitamente</h2>
          <p>Cidadãos: acesso gratuito permanente</p>
          <p>Advogados: 14 dias de teste, sem cartão de crédito</p>
          <div style={{marginTop: '30px'}}>
            <Link href="/pricing" className="cta">COMEÇAR AGORA</Link>
            <Link href="/login" className="cta cta-outline">JÁ TENHO CONTA</Link>
          </div>
        </section>
      </div>

      <footer>
        <p><strong>Doutora IA</strong> - Tecnologia Jurídica Brasileira</p>
        <p>1.326 Engines · 15 Áreas do Direito · 539 PDFs Processados</p>
        <p>&copy; 2026 - Democratizando o acesso à Justiça</p>
      </footer>
    </>
  );
}
