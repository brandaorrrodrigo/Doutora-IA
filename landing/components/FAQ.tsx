'use client';
import React, { useState } from 'react';
import Container from './Container';

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const faqs = [
    {
      question: 'A Doutora IA substitui um advogado?',
      answer: 'Não. A Doutora IA é uma ferramenta de apoio à pesquisa e redação jurídica. Todas as decisões técnicas cabem exclusivamente ao advogado responsável inscrito na OAB. A IA fornece fundamentação e agiliza processos, mas a análise crítica e estratégia do caso são suas.'
    },
    {
      question: 'Como funciona a verificação das citações?',
      answer: 'Toda citação inclui um link clicável que leva direto à fonte oficial: site do tribunal, portal da legislação ou repositório de doutrina. Você pode auditar cada informação em segundos. Se a IA não encontrar fonte confiável, ela informa que não tem dados suficientes.'
    },
    {
      question: 'Meus dados e os dos meus clientes são seguros?',
      answer: 'Sim. Seguimos a LGPD rigorosamente. Seus dados ficam criptografados em servidores no Brasil e nunca são usados para treinar modelos de IA. Você pode exportar ou deletar tudo a qualquer momento. Temos certificação ISO 27001 em andamento.'
    },
    {
      question: 'Como funciona o rodízio de leads?',
      answer: 'Quando um cliente em potencial procura um advogado na plataforma, ele informa área de atuação e cidade. Nossa IA distribui o lead de forma justa entre advogados cadastrados naquela área e região, sem favorecimento. Quanto mais específica sua área, menos concorrência.'
    },
    {
      question: 'Posso cancelar a qualquer momento?',
      answer: 'Sim, sem multas ou burocracias. Basta um clique no painel. Suas consultas e documentos ficam disponíveis por 30 dias após o cancelamento. Se cancelar nos primeiros 7 dias, devolvemos 100% do valor pago.'
    },
    {
      question: 'A IA está sempre atualizada com novas leis?',
      answer: 'Sim. Toda semana incluímos novas decisões dos tribunais superiores e atualizações legislativas. Você pode filtrar por período para ver apenas jurisprudências recentes. Também enviamos alertas quando há mudanças relevantes na sua área de atuação.'
    },
    {
      question: 'Quais formas de pagamento são aceitas?',
      answer: 'Aceitamos cartão de crédito, PIX (via Stripe) e USDT/Tether (via Binance Pay). Todas as transações são seguras e você recebe confirmação imediata. Para pagamento em cripto, o valor é convertido automaticamente na cotação do dia.'
    },
    {
      question: 'Preciso de conhecimento técnico para usar?',
      answer: 'Não. A interface é simples e intuitiva. Se você sabe usar Google e Word, vai se adaptar em minutos. Oferecemos onboarding guiado no primeiro acesso e tutoriais em vídeo para cada funcionalidade. Suporte por WhatsApp disponível em todos os planos.'
    }
  ];

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map(faq => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer
      }
    }))
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <section id="faq" className="py-20 scroll-mt-20">
        <Container>
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl lg:text-5xl font-bold mb-4">
                Perguntas <span className="text-primary">frequentes</span>
              </h2>
              <p className="text-lg text-gray-400">
                Tudo o que você precisa saber sobre a Doutora IA
              </p>
            </div>

            <div className="space-y-4">
              {faqs.map((faq, index) => (
                <div
                  key={index}
                  className="bg-white/5 border border-white/10 rounded-xl overflow-hidden backdrop-blur hover:border-primary/30 transition"
                >
                  <button
                    onClick={() => setOpenIndex(openIndex === index ? null : index)}
                    className="w-full px-6 py-4 flex items-center justify-between text-left"
                  >
                    <span className="font-semibold pr-4">{faq.question}</span>
                    <svg
                      className={`w-5 h-5 text-primary flex-shrink-0 transition-transform ${
                        openIndex === index ? 'rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {openIndex === index && (
                    <div className="px-6 pb-4 text-gray-400">
                      {faq.answer}
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="mt-12 text-center p-6 bg-gradient-to-r from-primary/10 to-tech-blue/10 border border-primary/20 rounded-xl">
              <p className="text-sm text-gray-300 mb-4">
                Ainda tem dúvidas? Nossa equipe está pronta para ajudar.
              </p>
              <button
                onClick={() => {
                  document.getElementById('lead-modal')?.classList.remove('hidden');
                }}
                className="px-6 py-2 bg-primary text-background rounded-lg font-semibold hover:bg-primary-dark transition"
              >
                Falar com especialista
              </button>
            </div>
          </div>
        </Container>
      </section>
    </>
  );
}
