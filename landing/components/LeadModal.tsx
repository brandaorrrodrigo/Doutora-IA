'use client';
import React, { useState } from 'react';
import { trackLeadSubmit } from '@/lib/analytics';

export default function LeadModal() {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [telefone, setTelefone] = useState('');
  const [oab, setOab] = useState('');
  const [areas, setAreas] = useState<string[]>([]);
  const [cidades, setCidades] = useState<string[]>([]);
  const [lgpdConsent, setLgpdConsent] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const areasOptions = [
    'Cível', 'Criminal', 'Trabalhista', 'Previdenciário', 'Família',
    'Tributário', 'Empresarial', 'Ambiental', 'Consumidor', 'Imobiliário'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!lgpdConsent) {
      alert('Por favor, aceite os termos de privacidade para continuar.');
      return;
    }

    // Track lead submission
    trackLeadSubmit({ nome, email, telefone, oab, areas, cidades });

    // Simulate success (no backend API needed for now)
    setSubmitted(true);
    
    // Auto-close after 3 seconds
    setTimeout(() => {
      document.getElementById('lead-modal')?.classList.add('hidden');
      setSubmitted(false);
      // Reset form
      setNome('');
      setEmail('');
      setTelefone('');
      setOab('');
      setAreas([]);
      setCidades([]);
      setLgpdConsent(false);
    }, 3000);
  };

  const handleAreaToggle = (area: string) => {
    setAreas(prev =>
      prev.includes(area)
        ? prev.filter(a => a !== area)
        : [...prev, area]
    );
  };

  return (
    <div
      id="lead-modal"
      className="hidden fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          document.getElementById('lead-modal')?.classList.add('hidden');
        }
      }}
    >
      <div className="bg-background border border-white/10 rounded-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {!submitted ? (
          <>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold">Cadastre-se na Waitlist</h3>
              <button
                onClick={() => document.getElementById('lead-modal')?.classList.add('hidden')}
                className="text-gray-400 hover:text-white transition"
              >
                ✕
              </button>
            </div>

            <p className="text-gray-400 mb-6">
              Seja um dos primeiros a experimentar a Doutora IA. Preencha seus dados e receba acesso prioritário.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Nome completo</label>
                <input
                  type="text"
                  required
                  value={nome}
                  onChange={(e) => setNome(e.target.value)}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-primary focus:outline-none"
                  placeholder="Seu nome"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">E-mail profissional</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-primary focus:outline-none"
                  placeholder="seu@email.com"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Telefone/WhatsApp</label>
                <input
                  type="tel"
                  required
                  value={telefone}
                  onChange={(e) => setTelefone(e.target.value)}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-primary focus:outline-none"
                  placeholder="(00) 00000-0000"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">OAB (opcional)</label>
                <input
                  type="text"
                  value={oab}
                  onChange={(e) => setOab(e.target.value)}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-primary focus:outline-none"
                  placeholder="OAB/UF 000000"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Áreas de atuação</label>
                <div className="grid grid-cols-2 gap-2">
                  {areasOptions.map(area => (
                    <label key={area} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={areas.includes(area)}
                        onChange={() => handleAreaToggle(area)}
                        className="rounded border-gray-600"
                      />
                      <span className="text-sm">{area}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Cidades de interesse</label>
                <input
                  type="text"
                  value={cidades.join(', ')}
                  onChange={(e) => setCidades(e.target.value.split(',').map(c => c.trim()))}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-primary focus:outline-none"
                  placeholder="São Paulo, Rio de Janeiro..."
                />
              </div>

              <div className="flex items-start space-x-2">
                <input
                  type="checkbox"
                  required
                  checked={lgpdConsent}
                  onChange={(e) => setLgpdConsent(e.target.checked)}
                  className="mt-1 rounded border-gray-600"
                />
                <label className="text-xs text-gray-400">
                  Concordo com o processamento dos meus dados conforme a{' '}
                  <a href="/privacy" className="text-primary hover:underline">Política de Privacidade</a> (LGPD).
                  Meus dados serão usados apenas para comunicação sobre a Doutora IA.
                </label>
              </div>

              <button
                type="submit"
                className="w-full py-3 bg-primary text-background rounded-lg font-semibold hover:bg-primary-dark transition"
              >
                Entrar na Waitlist
              </button>
            </form>
          </>
        ) : (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">✅</div>
            <h3 className="text-2xl font-bold mb-2">Cadastro realizado!</h3>
            <p className="text-gray-400">
              Você receberá um e-mail em breve com instruções de acesso.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
