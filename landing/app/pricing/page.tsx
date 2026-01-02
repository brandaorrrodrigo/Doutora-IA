'use client';
import Link from 'next/link';

export default function PricingPage() {
  return (
    <>
      <style jsx global>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: serif; background: linear-gradient(135deg, #3e2723, #5d4037); min-height: 100vh; padding: 40px 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { text-align: center; color: #d4af37; font-size: 3em; margin-bottom: 40px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; }
        .card { background: white; border-radius: 20px; padding: 40px; text-align: center; border-top: 5px solid #d4af37; transition: transform 0.3s; }
        .card:hover { transform: translateY(-5px); }
        .name { font-size: 1.8em; color: #3e2723; margin-bottom: 10px; }
        .price { font-size: 3em; color: #d4af37; font-weight: bold; margin: 20px 0; }
        .btn { display: block; width: 100%; padding: 15px; background: #d4af37; color: #3e2723; border: none; border-radius: 10px; font-size: 1.2em; cursor: pointer; font-weight: bold; margin-top: 20px; transition: all 0.3s; text-decoration: none; }
        .btn:hover { background: #b8860b; }
        ul { list-style: none; text-align: left; margin: 20px 0; }
        ul li { padding: 10px 0; border-bottom: 1px solid #eee; }
        ul li:before { content: "✓ "; color: #d4af37; font-weight: bold; }
        .back { text-align: center; margin-top: 40px; }
        .back a { color: #f5f5dc; text-decoration: none; font-size: 1.1em; }
        .back a:hover { text-decoration: underline; }
      `}</style>

      <div className="container">
        <h1>Escolha Seu Plano</h1>
        <div className="grid">
          <div className="card">
            <div className="name">Basic</div>
            <div className="price">R$ 49</div>
            <p>por mês</p>
            <ul>
              <li>Dashboard completo</li>
              <li>Até 50 leads/mês</li>
              <li>Suporte email</li>
              <li>Relatórios básicos</li>
            </ul>
            <button className="btn" onClick={() => alert('Em breve! Entre em contato via email.')}>Assinar</button>
          </div>

          <div className="card">
            <div className="name">Pro</div>
            <div className="price">R$ 149</div>
            <p>por mês</p>
            <ul>
              <li>Tudo do Basic</li>
              <li>Leads ilimitados</li>
              <li>Suporte prioritário</li>
              <li>Relatórios avançados</li>
              <li>Integrações API</li>
            </ul>
            <button className="btn" onClick={() => alert('Em breve! Entre em contato via email.')}>Assinar</button>
          </div>

          <div className="card">
            <div className="name">Enterprise</div>
            <div className="price">R$ 499</div>
            <p>por mês</p>
            <ul>
              <li>Tudo do Pro</li>
              <li>API completa</li>
              <li>Suporte 24/7</li>
              <li>Customização total</li>
              <li>Treinamento equipe</li>
            </ul>
            <button className="btn" onClick={() => alert('Em breve! Entre em contato via email.')}>Assinar</button>
          </div>
        </div>

        <div className="back">
          <Link href="/">← Voltar para página inicial</Link>
        </div>
      </div>
    </>
  );
}
