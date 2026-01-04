'use client';
import Link from 'next/link';
import Image from 'next/image';

export default function HomePage() {
  return (
    <>
      <style jsx global>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Georgia', 'Times New Roman', serif; background: #0a0a0a; color: #f5f5dc; line-height: 1.8; }

        @keyframes glow-pulse {
          0%, 100% {
            filter: drop-shadow(0 0 20px rgba(212, 175, 55, 0.8))
                    drop-shadow(0 0 40px rgba(212, 175, 55, 0.6))
                    drop-shadow(0 0 60px rgba(212, 175, 55, 0.4))
                    drop-shadow(0 0 80px rgba(212, 175, 55, 0.3));
            transform: scale(1);
          }
          50% {
            filter: drop-shadow(0 0 30px rgba(212, 175, 55, 1))
                    drop-shadow(0 0 60px rgba(212, 175, 55, 0.9))
                    drop-shadow(0 0 90px rgba(212, 175, 55, 0.7))
                    drop-shadow(0 0 120px rgba(212, 175, 55, 0.5))
                    drop-shadow(0 0 150px rgba(212, 175, 55, 0.3));
            transform: scale(1.02);
          }
        }

        header {
          border-top: 2px solid #d4af37;
          border-bottom: 2px solid #d4af37;
          background: linear-gradient(135deg, #1a1410, #2d1f17);
          padding: 60px 20px;
          text-align: center;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 60px;
        }

        header h1 {
          font-size: 3em;
          color: #d4af37;
          font-weight: 400;
          letter-spacing: 3px;
          margin: 0;
          text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }

        header .logo {
          animation: glow-pulse 3s ease-in-out infinite;
          max-width: 400px;
          width: 100%;
          height: auto;
        }

        header .content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 20px;
          max-width: 900px;
        }

        header .subtitle {
          font-size: 1.3em;
          color: #f5f5dc;
          margin: 0;
        }

        header .stats {
          font-size: 0.95em;
          color: #d4af37;
          font-weight: 300;
          margin: 0;
        }

        header .intro {
          font-size: 1.05em;
          color: #f5f5dc;
          margin: 0;
          line-height: 1.7;
          opacity: 0.95;
        }

        header .cta-group {
          display: flex;
          gap: 20px;
          margin-top: 10px;
          flex-wrap: wrap;
          justify-content: center;
        }

        .cta {
          display: inline-block;
          padding: 16px 40px;
          background: #d4af37;
          color: #1a1410;
          text-decoration: none;
          border-radius: 6px;
          font-weight: 600;
          transition: all 0.3s;
          cursor: pointer;
          border: none;
          font-family: inherit;
          font-size: 1em;
        }

        .cta:hover {
          background: #b8860b;
          transform: translateY(-2px);
        }

        .cta-outline {
          background: transparent;
          border: 2px solid #d4af37;
          color: #d4af37;
        }

        .cta-outline:hover {
          background: rgba(212, 175, 55, 0.1);
        }

        footer {
          background: #1a1410;
          color: #f5f5dc;
          text-align: center;
          padding: 40px 20px;
          border-top: 2px solid #d4af37;
          margin-top: 80px;
        }

        footer p {
          margin: 10px 0;
          font-size: 0.95em;
        }
      `}</style>

      <header>
        <h1>DOUTORA IA</h1>
        <Image
          src="/logo-brilhante.png"
          alt="Doutora IA"
          width={400}
          height={400}
          priority
          className="logo"
          style={{ objectFit: 'contain' }}
        />
        <div className="content">
          <p className="subtitle">A maior plataforma de inteligência jurídica já construída no Brasil</p>
          <p className="stats">1.326 engines jurídicas especializadas · 15 áreas do Direito cobertas · 539 PDFs de jurisprudência processados</p>
          <p className="intro">A Doutora IA une automação processual, análise de risco com inteligência artificial, jurisprudência real e gestão completa de escritórios. Uma plataforma jurídica de nova geração, com IA operando localmente no Brasil.</p>
          <div className="cta-group">
            <Link href="/pricing" className="cta">VER PLANOS</Link>
            <button className="cta cta-outline">ENTRAR</button>
          </div>
        </div>
      </header>

      <footer>
        <p><strong>DOUTORA IA</strong> - Tecnologia Jurídica Brasileira</p>
        <p>1.326 Engines especializadas · 15 Áreas do Direito cobertas · 539 PDFs de jurisprudência processados</p>
        <p>&copy; 2026 - Democratizando o acesso à Justiça</p>
      </footer>
    </>
  );
}
