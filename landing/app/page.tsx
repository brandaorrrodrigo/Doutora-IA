'use client';
import Link from 'next/link';

export default function HomePage() {
  return (
    <>
      <style jsx global>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: serif; background: #faf0e6; }
        header { background: #3e2723; padding: 20px; text-align: center; color: #d4af37; font-size: 2rem; font-weight: bold; }
        .hero { background: linear-gradient(135deg, #3e2723, #5d4037); color: #f5f5dc; padding: 100px 20px; text-align: center; }
        .hero h1 { font-size: 3rem; color: #d4af37; margin-bottom: 20px; }
        .hero p { font-size: 1.3rem; margin-bottom: 30px; }
        .btn { display: inline-block; padding: 15px 40px; margin: 10px; background: #d4af37; color: #3e2723; text-decoration: none; border-radius: 30px; font-weight: bold; transition: all 0.3s; }
        .btn:hover { background: #b8860b; }
        .btn-outline { background: transparent; border: 2px solid #f5f5dc; color: #f5f5dc; }
        .btn-outline:hover { background: rgba(245, 245, 220, 0.1); }
        .features { max-width: 1000px; margin: 60px auto; padding: 20px; }
        .feature { background: white; padding: 30px; margin: 20px 0; border-radius: 10px; border-left: 4px solid #d4af37; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .feature h3 { color: #3e2723; margin-bottom: 15px; font-size: 1.5rem; }
        .feature p { color: #555; line-height: 1.6; }
        footer { background: #3e2723; color: #f5f5dc; text-align: center; padding: 30px; margin-top: 60px; }
        footer p { margin: 5px 0; }
      `}</style>

      <header>DOUTORA IA</header>

      <div className="hero">
        <h1>Gestão Jurídica Inteligente</h1>
        <p>Plataforma completa para advogados gerenciarem leads e clientes</p>
        <Link href="/pricing" className="btn">VER PLANOS</Link>
        <Link href="/login" className="btn btn-outline">ENTRAR</Link>
      </div>

      <div className="features">
        <div className="feature">
          <h3>📊 Dashboard Completo</h3>
          <p>Visualize métricas e KPIs do seu escritório em tempo real. Acompanhe conversões, receita e performance da equipe em um só lugar.</p>
        </div>

        <div className="feature">
          <h3>👥 Gestão de Leads</h3>
          <p>Organize e acompanhe seus potenciais clientes. Sistema inteligente de qualificação e distribuição automática de leads.</p>
        </div>

        <div className="feature">
          <h3>⚖️ Painel do Advogado</h3>
          <p>Ferramentas essenciais para o dia a dia do advogado. Acesso rápido a processos, prazos e documentos importantes.</p>
        </div>

        <div className="feature">
          <h3>📈 Relatórios Avançados</h3>
          <p>Análises detalhadas de performance, origem de leads e ROI. Tome decisões baseadas em dados reais.</p>
        </div>

        <div className="feature">
          <h3>🔔 Notificações Inteligentes</h3>
          <p>Nunca perca um prazo ou oportunidade. Alertas automáticos para prazos processuais e follow-up de clientes.</p>
        </div>

        <div className="feature">
          <h3>🔐 Segurança Total</h3>
          <p>Seus dados protegidos com criptografia de ponta. Conformidade com LGPD e melhores práticas de segurança.</p>
        </div>
      </div>

      <footer>
        <p><strong>Doutora IA</strong> - Tecnologia Jurídica</p>
        <p>&copy; 2026 - Todos os direitos reservados</p>
      </footer>
    </>
  );
}
