'use client';
import React, { useState } from 'react';
import Container from './Container';
import { trackROICalculated } from '@/lib/analytics';

export default function RoiCalculator() {
  const [pecasPorMes, setPecasPorMes] = useState(10);
  const [horasPorPeca, setHorasPorPeca] = useState(4);
  const [valorHora, setValorHora] = useState(200);

  const tempoSemIA = pecasPorMes * horasPorPeca;
  const tempoComIA = pecasPorMes * (horasPorPeca * 0.26); // 74% economia
  const tempoEconomizado = tempoSemIA - tempoComIA;
  const valorEconomizado = tempoEconomizado * valorHora;
  const custoPlano = 149; // Plano Pro
  const economiaLiquida = valorEconomizado - custoPlano;
  const roi = ((economiaLiquida / custoPlano) * 100);

  React.useEffect(() => {
    trackROICalculated(economiaLiquida);
  }, [economiaLiquida]);

  return (
    <section className="py-20 bg-gradient-to-b from-transparent to-primary/5">
      <Container>
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-5xl font-bold mb-4">
              Calcule sua <span className="text-tech-blue">economia</span>
            </h2>
            <p className="text-lg text-gray-400">
              Descubra quanto tempo e dinheiro você pode economizar com a Doutora IA
            </p>
          </div>

          <div className="bg-gradient-to-br from-white/5 to-white/10 border border-white/10 rounded-2xl p-8 backdrop-blur">
            <div className="grid md:grid-cols-2 gap-8 mb-8">
              <div>
                <label className="block text-sm font-semibold mb-2">
                  Quantas peças você redige por mês?
                </label>
                <input
                  type="range"
                  min="1"
                  max="50"
                  value={pecasPorMes}
                  onChange={(e) => setPecasPorMes(Number(e.target.value))}
                  className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="text-center mt-2">
                  <span className="text-3xl font-bold text-primary">{pecasPorMes}</span>
                  <span className="text-gray-400 ml-2">peças</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">
                  Quantas horas por peça (em média)?
                </label>
                <input
                  type="range"
                  min="1"
                  max="12"
                  value={horasPorPeca}
                  onChange={(e) => setHorasPorPeca(Number(e.target.value))}
                  className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="text-center mt-2">
                  <span className="text-3xl font-bold text-primary">{horasPorPeca}</span>
                  <span className="text-gray-400 ml-2">horas</span>
                </div>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-semibold mb-2">
                  Qual o valor da sua hora de trabalho?
                </label>
                <input
                  type="range"
                  min="50"
                  max="1000"
                  step="50"
                  value={valorHora}
                  onChange={(e) => setValorHora(Number(e.target.value))}
                  className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="text-center mt-2">
                  <span className="text-3xl font-bold text-primary">R${valorHora}</span>
                  <span className="text-gray-400 ml-2">por hora</span>
                </div>
              </div>
            </div>

            <div className="border-t border-white/10 pt-8">
              <div className="grid md:grid-cols-3 gap-6 mb-8">
                <div className="text-center p-6 bg-white/5 rounded-xl">
                  <div className="text-sm text-gray-400 mb-2">Tempo economizado</div>
                  <div className="text-3xl font-bold text-tech-blue">{tempoEconomizado.toFixed(0)}h</div>
                  <div className="text-xs text-gray-500 mt-1">por mês</div>
                </div>

                <div className="text-center p-6 bg-white/5 rounded-xl">
                  <div className="text-sm text-gray-400 mb-2">Valor economizado</div>
                  <div className="text-3xl font-bold text-tech-blue">R${valorEconomizado.toFixed(0)}</div>
                  <div className="text-xs text-gray-500 mt-1">por mês</div>
                </div>

                <div className="text-center p-6 bg-white/5 rounded-xl">
                  <div className="text-sm text-gray-400 mb-2">ROI (Retorno)</div>
                  <div className="text-3xl font-bold text-tech-blue">{roi.toFixed(0)}%</div>
                  <div className="text-xs text-gray-500 mt-1">sobre o investimento</div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-primary/20 to-tech-blue/20 border border-primary/30 rounded-xl p-6">
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="text-sm text-gray-300 mb-1">Economia líquida mensal</div>
                    <div className="text-4xl font-bold text-white">
                      R${economiaLiquida.toFixed(0)}
                    </div>
                    <div className="text-xs text-gray-400 mt-2">
                      Já descontando o plano Pro (R${custoPlano}/mês)
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' });
                    }}
                    className="px-6 py-3 bg-primary text-background rounded-lg font-semibold hover:bg-primary-dark transition whitespace-nowrap"
                  >
                    Ver planos
                  </button>
                </div>
              </div>
            </div>
          </div>

          <p className="text-center text-xs text-gray-500 mt-6">
            * Cálculo baseado em 74% de economia de tempo em relação à pesquisa e redação manual.
            Resultados podem variar conforme complexidade das peças.
          </p>
        </div>
      </Container>
    </section>
  );
}
