'use client';
import React from 'react';
import Container from './Container';
import { trackCTAClick } from '@/lib/analytics';

export default function CtaFinal() {
  return (
    <section className="py-20 bg-gradient-to-b from-primary/5 to-transparent">
      <Container>
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary/20 via-tech-blue/20 to-accent/20 border border-primary/30 p-12 lg:p-16">
          <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-tech-blue/10 blur-3xl" aria-hidden="true" />

          <div className="relative z-10 max-w-3xl mx-auto text-center">
            <h2 className="text-3xl lg:text-5xl font-bold mb-6">
              Pronto para transformar sua <span className="text-tech-blue">prática jurídica</span>?
            </h2>

            <p className="text-lg text-gray-300 mb-8">
              Junte-se a centenas de advogados que já economizam tempo e aumentam a qualidade do seu trabalho com a Doutora IA.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <button
                onClick={() => {
                  trackCTAClick('cta_final_pricing');
                  document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="px-8 py-4 bg-primary text-background rounded-lg font-bold text-lg hover:bg-primary-dark transition shadow-lg shadow-primary/20"
              >
                Ver planos e preços
              </button>

              <button
                onClick={() => {
                  trackCTAClick('cta_final_demo');
                  document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="px-8 py-4 border-2 border-tech-blue text-tech-blue rounded-lg font-bold text-lg hover:bg-tech-blue/10 transition"
              >
                Ver demonstração
              </button>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-tech-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>7 dias de garantia</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-tech-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Cancele quando quiser</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-tech-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>LGPD compliant</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500">
            Doutora IA é um produto da <strong>Legal Tech Brasil</strong> • CNPJ em processamento
          </p>
        </div>
      </Container>
    </section>
  );
}
