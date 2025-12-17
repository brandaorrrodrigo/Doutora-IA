import React from 'react';
import Container from './Container';

export default function Footer() {
  return (
    <footer className="bg-background border-t border-white/10 py-12" role="contentinfo">
      <Container>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div>
            <h3 className="font-bold text-lg mb-4">Doutora IA</h3>
            <p className="text-sm text-gray-400">
              Jurisprudência e leis com citações auditáveis para advogados.
            </p>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-4">Legal</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="/termos" className="hover:text-primary transition">Termos de Uso</a></li>
              <li><a href="/privacidade" className="hover:text-primary transition">Política de Privacidade</a></li>
              <li><a href="/lgpd" className="hover:text-primary transition">LGPD</a></li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-4">Contato</h3>
            <p className="text-sm text-gray-400">
              contato@doutoraia.com
            </p>
          </div>
        </div>

        <div className="border-t border-white/10 pt-8">
          <p className="text-xs text-gray-500 mb-4">
            <strong>Aviso Legal:</strong> O conteúdo fornecido pela Doutora IA é informativo e não substitui consulta jurídica profissional.
            Todas as decisões técnicas cabem ao advogado responsável inscrito na OAB.
          </p>
          <p className="text-xs text-gray-500 text-center">
            © {new Date().getFullYear()} Doutora IA. Todos os direitos reservados.
          </p>
        </div>
      </Container>
    </footer>
  );
}
