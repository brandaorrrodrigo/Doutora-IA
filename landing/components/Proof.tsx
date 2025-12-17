import React from 'react';
import Container from './Container';

export default function Proof() {
  const stats = [
    {
      value: '+2.000',
      label: 'consultas simuladas',
      description: 'em jurisprudência e leis brasileiras'
    },
    {
      value: '89%',
      label: 'mais rápido em pesquisa',
      description: 'vs. busca manual em tribunais'
    },
    {
      value: '74%',
      label: 'de economia por peça',
      description: 'comparado a serviços tradicionais'
    }
  ];

  return (
    <section className="py-16 bg-gradient-to-b from-transparent to-primary/5">
      <Container>
        <div className="grid md:grid-cols-3 gap-8">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="text-center p-6 rounded-xl bg-white/5 border border-white/10 backdrop-blur hover:bg-white/10 transition"
            >
              <div className="text-4xl lg:text-5xl font-bold text-primary mb-2">
                {stat.value}
              </div>
              <div className="text-lg font-semibold mb-1">
                {stat.label}
              </div>
              <div className="text-sm text-gray-400">
                {stat.description}
              </div>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
