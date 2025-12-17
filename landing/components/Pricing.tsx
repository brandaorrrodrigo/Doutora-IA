'use client';
import React, { useState } from 'react';
import Container from './Container';
import { trackPlanSelect } from '@/lib/analytics';

export default function Pricing() {
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const plans = [
    {
      name: 'Pesquisa',
      price: 49,
      description: 'Para quem quer pesquisar com fontes confiáveis',
      features: [
        'Pesquisa ilimitada em jurisprudência',
        'Citações com link para fonte oficial',
        'Busca em leis federais e estaduais',
        'Histórico de 90 dias',
        'Suporte por email'
      ],
      cta: 'Começar agora',
      highlight: false
    },
    {
      name: 'Leads',
      price: 79,
      description: 'Pesquisa + rodízio de leads qualificados',
      features: [
        'Tudo do plano Pesquisa',
        'Rodízio de leads por área',
        'Até 3 áreas de atuação',
        'Até 5 cidades',
        'Perfil público na plataforma',
        'Suporte prioritário'
      ],
      cta: 'Receber leads',
      highlight: false
    },
    {
      name: 'Redação',
      price: 99,
      description: 'Pesquisa + gerador de peças processuais',
      features: [
        'Tudo do plano Pesquisa',
        'Gerador de petições iniciais',
        'Gerador de recursos',
        'Gerador de contestações',
        'Modelos personalizáveis',
        'Exportação em DOCX/PDF'
      ],
      cta: 'Gerar peças',
      highlight: false
    },
    {
      name: 'Pro',
      price: 149,
      description: 'Pesquisa + Leads + Redação completo',
      features: [
        'Tudo dos planos anteriores',
        'Até 5 áreas de atuação',
        'Até 10 cidades',
        'API de integração',
        'Relatórios mensais',
        'Suporte WhatsApp'
      ],
      cta: 'Plano completo',
      highlight: true
    },
    {
      name: 'Full',
      price: 199,
      description: 'Tudo liberado + prioridade máxima',
      features: [
        'Todos os recursos ilimitados',
        'Áreas de atuação ilimitadas',
        'Cidades ilimitadas',
        'Prioridade em leads',
        'Selo "Verificado pela Doutora IA"',
        'Onboarding dedicado',
        'Suporte 24/7'
      ],
      cta: 'Plano premium',
      highlight: false
    }
  ];

  return (
    <section id="pricing" className="py-20 bg-gradient-to-b from-primary/5 to-transparent scroll-mt-20">
      <Container>
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-5xl font-bold mb-4">
            Planos que cabem no seu <span className="text-primary">bolso</span>
          </h2>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Escolha o plano ideal para o seu escritório. Cancele quando quiser, sem multas.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-6 mb-12">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`relative p-6 rounded-2xl border backdrop-blur transition ${
                plan.highlight
                  ? 'bg-gradient-to-br from-primary/20 to-tech-blue/20 border-primary scale-105'
                  : 'bg-white/5 border-white/10 hover:border-primary/30'
              }`}
            >
              {plan.highlight && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-primary text-background rounded-full text-xs font-bold">
                  MAIS POPULAR
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                <div className="mb-3">
                  <span className="text-4xl font-bold">R${plan.price}</span>
                  <span className="text-gray-400">/mês</span>
                </div>
                <p className="text-sm text-gray-400">{plan.description}</p>
              </div>

              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <svg className="w-5 h-5 text-tech-blue flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => {
                  trackPlanSelect(plan.name);
                  setSelectedPlan(plan.name);
                  document.getElementById(`payment-modal-${plan.name}`)?.classList.remove('hidden');
                }}
                className={`w-full py-3 rounded-lg font-semibold transition ${
                  plan.highlight
                    ? 'bg-primary text-background hover:bg-primary-dark'
                    : 'bg-white/10 hover:bg-white/20'
                }`}
              >
                {plan.cta}
              </button>

              {/* Modal de pagamento individual por plano */}
              <div
                id={`payment-modal-${plan.name}`}
                className="hidden fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                onClick={(e) => {
                  if (e.target === e.currentTarget) {
                    e.currentTarget.classList.add('hidden');
                  }
                }}
              >
                <div className="bg-background border border-white/10 rounded-2xl p-8 max-w-md w-full">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <h3 className="text-2xl font-bold mb-2">Plano {plan.name}</h3>
                      <p className="text-3xl font-bold text-primary">R${plan.price}/mês</p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.currentTarget.closest('#payment-modal-' + plan.name)?.classList.add('hidden');
                      }}
                      className="text-gray-400 hover:text-white"
                    >
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>

                  <div className="space-y-4">
                    <p className="text-gray-400 text-sm mb-6">
                      Escolha sua forma de pagamento preferida:
                    </p>

                    <button className="w-full p-4 border border-white/10 rounded-lg hover:border-primary/50 transition flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                        <svg className="w-6 h-6" fill="white" viewBox="0 0 24 24">
                          <path d="M4 4h16a2 2 0 012 2v12a2 2 0 01-2 2H4a2 2 0 01-2-2V6a2 2 0 012-2zm0 2v12h16V6H4zm2 2h12v2H6V8zm0 4h8v2H6v-2z"/>
                        </svg>
                      </div>
                      <div className="text-left flex-1">
                        <div className="font-semibold">Cartão de Crédito ou PIX</div>
                        <div className="text-xs text-gray-400">via Stripe</div>
                      </div>
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </button>

                    <button className="w-full p-4 border border-white/10 rounded-lg hover:border-tech-blue/50 transition flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-tech-blue to-tech-blue-dark rounded-lg flex items-center justify-center text-xl font-bold">
                        B
                      </div>
                      <div className="text-left flex-1">
                        <div className="font-semibold">USDT (Tether)</div>
                        <div className="text-xs text-gray-400">via Binance Pay</div>
                      </div>
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  </div>

                  <p className="text-xs text-gray-500 mt-6">
                    Ao continuar, você concorda com nossos Termos de Uso e Política de Privacidade. Assinatura renovada mensalmente. Cancele quando quiser.
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center">
          <p className="text-sm text-gray-400">
            Todas as assinaturas incluem 7 dias de garantia. Não gostou? Devolvemos 100% do valor.
          </p>
        </div>
      </Container>
    </section>
  );
}
