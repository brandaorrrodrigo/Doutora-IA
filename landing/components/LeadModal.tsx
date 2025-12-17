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
    trackLeadSubmit({ areas, cidades, oab });

    // Mock API call - replace with actual endpoint
    try {
      const response = await fetch('/api/lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, email, telefone, oab, areas, cidades })
      });

      if (response.ok) {
        setSubmitted(true);
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
      }
    } catch (error) {
      console.error('Erro ao enviar lead:', error);
    }
  };

  return (
    <div
      id="lead-modal"
      className="hidden fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          e.currentTarget.classList.add('hidden');
        }
      }}
    >
      <div className="bg-background border border-white/10 rounded-2xl p-8 max-w-lg w-full my-8">
        {!submitted ? (
          <>
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-2xl font-bold mb-2">Entrar na fila</h3>
                <p className="text-sm text-gray-400">
                  Preencha seus dados para receber acesso prioritário
                </p>
              </div>
              <button
                onClick={() => {
                  document.getElementById('lead-modal')?.classList.add('hidden');
                }}
                className="text-gray-400 hover:text-white"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

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
                <label className="block text-sm font-semibold mb-2">Email</label>
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
                <label className="block text-sm font-semibold mb-2">OAB (Número e UF)</label>
                <input
                  type="text"
                  required
                  value={oab}
                  onChange={(e) => setOab(e.target.value)}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-primary focus:outline-none"
                  placeholder="Ex: 123456/SP"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Áreas de atuação (selecione até 3)</label>
                <div className="grid grid-cols-2 gap-2">
                  {areasOptions.map((area) => (
                    <label key={area} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={areas.includes(area)}
                        onChange={(e) => {
                          if (e.target.checked && areas.length < 3) {
                            setAreas([...areas, area]);
                          } else if (!e.target.checked) {
                            setAreas(areas.filter(a => a !== area));
                          }
                        }}
                        className="w-4 h-4 accent-primary"
                      />
                      <span className="text-sm">{area}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Cidades de atuação</label>
                <input
                  type="text"
                  value={cidades.join(', ')}
                  onChange={(e) => setCidades(e.target.value.split(',').map(c => c.trim()))}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-primary focus:outline-none"
                  placeholder="Ex: São Paulo, Campinas, Santos"
                />
                <p className="text-xs text-gray-500 mt-1">Separe por vírgula</p>
              </div>

              <div className="pt-4 border-t border-white/10">
                <label className="flex items-start gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    required
                    checked={lgpdConsent}
                    onChange={(e) => setLgpdConsent(e.target.checked)}
                    className="w-5 h-5 mt-0.5 accent-primary flex-shrink-0"
                  />
                  <span className="text-xs text-gray-400">
                    Concordo com a <a href="/privacidade" className="text-primary hover:underline">Política de Privacidade</a> e autorizo o tratamento dos meus dados conforme a LGPD. Estou ciente de que posso solicitar a exclusão a qualquer momento.
                  </span>
                </label>
              </div>

              <button
                type="submit"
                className="w-full py-3 bg-primary text-background rounded-lg font-bold hover:bg-primary-dark transition"
              >
                Entrar na fila
              </button>

              <p className="text-xs text-gray-500 text-center">
                Você receberá um email de confirmação em até 24 horas.
              </p>
            </form>
          </>
        ) : (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-tech-blue rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold mb-2">Cadastro realizado!</h3>
            <p className="text-gray-400">
              Você entrou na fila. Em breve você receberá um email com mais informações.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
