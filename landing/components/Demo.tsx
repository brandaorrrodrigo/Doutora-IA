import React from 'react';
import Container from './Container';

export default function Demo() {
  const features = [
    {
      title: 'Pesquisa com citações verificáveis',
      description: 'Digite qualquer questão jurídica e receba resposta fundamentada em leis e jurisprudências reais, com links clicáveis para as fontes oficiais.',
      image: '/screens/pesquisa.png',
      alt: 'Interface de pesquisa com citações verificáveis'
    },
    {
      title: 'Gerador de peças processuais',
      description: 'Crie petições iniciais, recursos, contestações e pareceres em minutos. A IA segue modelos profissionais e inclui todas as fundamentações.',
      image: '/screens/gerador.png',
      alt: 'Interface do gerador de peças processuais'
    },
    {
      title: 'Rodízio inteligente de leads',
      description: 'Configure suas áreas de atuação e receba leads qualificados por área e cidade. Sistema justo de distribuição sem favorecimento.',
      image: '/screens/rodizio.png',
      alt: 'Painel de rodízio de leads'
    },
    {
      title: 'Painel de gestão completo',
      description: 'Acompanhe suas consultas, peças geradas, leads recebidos e estatísticas de uso em tempo real. Tudo em um só lugar.',
      image: '/screens/painel.png',
      alt: 'Painel de gestão e estatísticas'
    }
  ];

  return (
    <section id="demo" className="py-20 bg-gradient-to-b from-transparent to-primary/5 scroll-mt-20">
      <Container>
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-5xl font-bold mb-4">
            Veja a <span className="text-primary">Doutora IA</span> em ação
          </h2>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Demonstração das principais funcionalidades da plataforma
          </p>
        </div>

        <div className="space-y-20">
          {features.map((feature, index) => (
            <div
              key={index}
              className={`grid lg:grid-cols-2 gap-12 items-center ${
                index % 2 === 1 ? 'lg:flex-row-reverse' : ''
              }`}
            >
              <div className={index % 2 === 1 ? 'lg:order-2' : ''}>
                <h3 className="text-2xl lg:text-3xl font-bold mb-4">
                  {feature.title}
                </h3>
                <p className="text-gray-400 text-lg">
                  {feature.description}
                </p>
              </div>

              <div className={index % 2 === 1 ? 'lg:order-1' : ''}>
                <div className="relative rounded-xl overflow-hidden border border-white/10 bg-gradient-to-br from-white/5 to-white/10 backdrop-blur">
                  <div className="aspect-video bg-gradient-to-br from-primary/20 to-blue-500/20 flex items-center justify-center">
                    <div className="text-center p-8">
                      <div className="text-6xl mb-4">📊</div>
                      <p className="text-sm text-gray-400">{feature.alt}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <div className="inline-block p-8 rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/20">
            <h3 className="text-2xl font-bold mb-4">Quer ver ao vivo?</h3>
            <p className="text-gray-400 mb-6 max-w-md">
              Agende uma demonstração personalizada com nossa equipe e descubra como a Doutora IA pode transformar sua prática jurídica.
            </p>
            <button
              onClick={() => {
                document.getElementById('lead-modal')?.classList.remove('hidden');
              }}
              className="px-6 py-3 bg-primary text-background rounded-lg font-semibold hover:bg-primary-dark transition"
            >
              Agendar demonstração
            </button>
          </div>
        </div>
      </Container>
    </section>
  );
}
