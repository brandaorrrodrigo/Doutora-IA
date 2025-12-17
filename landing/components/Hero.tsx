'use client';
import React from 'react';
import Container from './Container';
import { trackCTAClick } from '@/lib/analytics';

export default function Hero() {
  return (
    <section className="relative py-20 lg:py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent pointer-events-none" aria-hidden="true" />

      <Container>
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-medium">Fontes oficiais</span>
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-medium">Citações com link</span>
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-medium">Sem alucinação</span>
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-medium">LGPD first</span>
            </div>

            <h1 className="text-4xl lg:text-6xl font-bold leading-tight">
              Doutora IA para Advogados — <span className="text-primary">pesquise, redija e receba leads qualificados</span>
            </h1>

            <p className="text-lg text-gray-300">
              Jurisprudência e leis com citações auditáveis, gerador de peças com fontes e rodízio de leads por área. LGPD first.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => {
                  trackCTAClick('hero_demo');
                  document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="px-6 py-3 bg-white text-background rounded-lg font-semibold hover:bg-gray-100 transition inline-flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                </svg>
                Ver demo de 3 minutos
              </button>

              <button
                onClick={() => {
                  trackCTAClick('hero_pricing');
                  document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="px-6 py-3 bg-primary text-background rounded-lg font-semibold hover:bg-primary-dark transition"
              >
                Começar no plano Pesquisa
              </button>

              <button
                onClick={() => {
                  trackCTAClick('hero_leads');
                  document.getElementById('lead-modal')?.classList.remove('hidden');
                }}
                className="px-6 py-3 border border-primary text-primary rounded-lg font-semibold hover:bg-primary/10 transition"
              >
                Entrar na fila de leads
              </button>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-blue-500/20 blur-3xl opacity-50" aria-hidden="true" />
            <div className="relative bg-gradient-to-br from-white/5 to-white/10 backdrop-blur p-8 rounded-2xl border border-white/10">
              <svg className="w-full h-auto text-primary" viewBox="0 0 200 200" fill="none" aria-hidden="true">
                <path
                  d="M100 40L120 80H80L100 40Z"
                  fill="currentColor"
                  opacity="0.2"
                />
                <rect x="70" y="80" width="60" height="80" fill="currentColor" opacity="0.3" />
                <circle cx="100" cy="100" r="50" stroke="currentColor" strokeWidth="2" fill="none" opacity="0.5" />
                <path
                  d="M60 160L100 120L140 160H60Z"
                  fill="currentColor"
                  opacity="0.4"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl mb-2">⚖️</div>
                  <p className="text-sm text-gray-400">Justiça com IA</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
