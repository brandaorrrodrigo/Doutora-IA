import React from 'react';
import Container from './Container';

export default function HowItWorks() {
  const steps = [
    {
      number: '01',
      title: 'Pesquise com citações',
      description: 'Digite sua dúvida jurídica e receba respostas fundamentadas com links diretos para leis e jurisprudências. Todas as citações são auditáveis e rastreáveis.',
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      )
    },
    {
      number: '02',
      title: 'Monte a peça em minutos',
      description: 'Gere petições iniciais, recursos e pareceres com base em modelos testados. A IA redige seguindo o seu estilo e inclui todas as fontes necessárias.',
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      )
    },
    {
      number: '03',
      title: 'Receba leads no rodízio',
      description: 'Cadastre suas áreas de atuação e cidades. Quando um cliente em potencial procurar um advogado, você entra no rodízio e recebe leads qualificados diretamente.',
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      )
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-b from-primary/5 to-transparent">
      <Container>
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-5xl font-bold mb-4">
            Como funciona a <span className="text-primary">Doutora IA</span>
          </h2>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Três passos simples para transformar sua prática jurídica
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div
              key={index}
              className="relative p-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur hover:bg-white/10 hover:border-primary/30 transition group"
            >
              <div className="absolute -top-4 -left-4 w-16 h-16 bg-primary rounded-full flex items-center justify-center text-background font-bold text-xl">
                {step.number}
              </div>

              <div className="text-primary mb-4 mt-4">
                {step.icon}
              </div>

              <h3 className="text-xl font-bold mb-3">
                {step.title}
              </h3>

              <p className="text-gray-400">
                {step.description}
              </p>

              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-1/2 -right-4 w-8 h-0.5 bg-primary/30" aria-hidden="true" />
              )}
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
