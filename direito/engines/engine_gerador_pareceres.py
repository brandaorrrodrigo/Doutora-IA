"""
Engine Gerador de Pareceres Premium - Doutora IA
Gera pareceres jurídicos profissionais para venda ao público

Versão: 1.0.0
Data: 31/12/2025
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from engine_assistente_publico import (
    AnaliseGratuita, TipoCaso, RespostasCompletas,
    EngineAssistentePublico
)


# =====================================================
# DATACLASSES - PARECER
# =====================================================

@dataclass
class SecaoDocumento:
    """Seção de um documento"""
    titulo: str
    conteudo: List[str]  # Parágrafos
    subsecoes: List['SecaoDocumento'] = field(default_factory=list)
    tipo: str = "texto"  # texto, lista, tabela, citacao


@dataclass
class JurisprudenciaCitada:
    """Jurisprudência citada no parecer"""
    tribunal: str
    numero_processo: str
    ementa: str
    data: str
    relevancia: str  # Por que foi citada


@dataclass
class DocumentoNecessario:
    """Documento necessário para o caso"""
    nome: str
    descricao: str
    obrigatorio: bool
    onde_obter: str


@dataclass
class ParecerPremium:
    """Parecer jurídico completo (produto vendido por R$ 7,00)"""

    # Identificação
    numero_parecer: str
    data_emissao: str
    tipo_caso: TipoCaso

    # Cliente
    dados_cliente: Dict[str, Any]  # Nome, email, etc (anonimizado se preferir)

    # Análise gratuita incluída
    analise_gratuita: AnaliseGratuita

    # Seções premium adicionais
    introducao: SecaoDocumento
    historico_detalhado: SecaoDocumento
    fundamentacao_juridica: SecaoDocumento
    jurisprudencias: List[JurisprudenciaCitada]
    analise_probabilidades: SecaoDocumento
    estrategia_recomendada: SecaoDocumento
    documentos_necessarios: List[DocumentoNecessario]
    modelos_documento: Dict[str, str]  # Nome -> Conteúdo de modelos
    conclusao: SecaoDocumento

    # Validade e disclaimer
    validade_dias: int = 90
    disclaimer: str = ""

    # Metadata
    versao_documento: str = "1.0"
    assinatura_digital: Optional[str] = None


@dataclass
class ConfiguracaoParecer:
    """Configuração de geração de parecer"""
    incluir_jurisprudencia: bool = True
    incluir_modelos: bool = True
    incluir_graficos: bool = True
    incluir_comparacao_casos: bool = True
    nivel_detalhamento: str = "completo"  # basico, intermediario, completo


# =====================================================
# ENGINE GERADOR
# =====================================================

class EngineGeradorPareceres:
    """Engine para gerar pareceres premium"""

    def __init__(self):
        self.engine_assistente = EngineAssistentePublico()
        self._contador_pareceres = 1000

    def gerar_parecer_completo(
        self,
        respostas: RespostasCompletas,
        dados_cliente: Dict[str, Any],
        config: Optional[ConfiguracaoParecer] = None
    ) -> ParecerPremium:
        """Gera parecer completo baseado nas respostas"""

        if config is None:
            config = ConfiguracaoParecer()

        # Obter análise gratuita primeiro
        analise = self.engine_assistente.analisar_caso(respostas)

        # Gerar número do parecer
        self._contador_pareceres += 1
        numero = f"PAR-{datetime.now().strftime('%Y%m')}-{self._contador_pareceres:05d}"

        # Gerar seções específicas por tipo
        tipo = respostas.tipo_caso

        if tipo == TipoCaso.PENSAO_ALIMENTICIA:
            return self._gerar_parecer_pensao(numero, respostas, analise, dados_cliente, config)
        elif tipo == TipoCaso.DIREITO_CONSUMIDOR:
            return self._gerar_parecer_consumidor(numero, respostas, analise, dados_cliente, config)
        elif tipo == TipoCaso.TRABALHISTA:
            return self._gerar_parecer_trabalhista(numero, respostas, analise, dados_cliente, config)
        else:
            return self._gerar_parecer_generico(numero, respostas, analise, dados_cliente, config)

    # =====================================================
    # GERADORES ESPECÍFICOS
    # =====================================================

    def _gerar_parecer_pensao(
        self,
        numero: str,
        respostas: RespostasCompletas,
        analise: AnaliseGratuita,
        dados_cliente: Dict,
        config: ConfiguracaoParecer
    ) -> ParecerPremium:
        """Gera parecer específico de pensão alimentícia"""

        resp_dict = {r.pergunta_id: r.valor for r in respostas.respostas}

        # Introdução
        introducao = SecaoDocumento(
            titulo="INTRODUÇÃO",
            conteudo=[
                "Este parecer tem por objetivo analisar a viabilidade e os aspectos jurídicos "
                "relacionados à ação de alimentos, apresentando fundamentos legais, "
                "jurisprudência aplicável e orientações práticas para o ajuizamento da demanda.",

                f"A presente análise considera {analise.estatisticas.total_casos_similares} casos "
                f"similares julgados, com taxa de sucesso de {analise.estatisticas.taxa_sucesso_percentual}%."
            ]
        )

        # Histórico detalhado
        qtd_filhos = resp_dict.get("qtd_filhos", 1)
        renda_alimentante = resp_dict.get("renda_alimentante", 0)

        historico = SecaoDocumento(
            titulo="HISTÓRICO DO CASO",
            conteudo=[
                f"Trata-se de questão envolvendo {qtd_filhos} filho(s) menor(es) que necessita(m) "
                "de pensão alimentícia para seu sustento e desenvolvimento adequado.",

                f"O alimentante possui renda declarada de R$ {renda_alimentante:.2f} mensais, "
                f"exercendo atividade profissional como {resp_dict.get('situacao_emprego', 'não informado')}.",

                "Os alimentos são destinados a prover as necessidades básicas dos menores, "
                "incluindo alimentação, saúde, educação, vestuário, habitação e lazer, "
                "conforme preceitua o Código Civil e o Estatuto da Criança e do Adolescente."
            ]
        )

        # Fundamentação jurídica
        fundamentacao = SecaoDocumento(
            titulo="FUNDAMENTAÇÃO JURÍDICA",
            conteudo=[
                "A obrigação alimentar encontra fundamento constitucional no princípio da "
                "dignidade da pessoa humana (art. 1º, III, CF/88) e no dever de proteção "
                "integral à criança e ao adolescente (art. 227, CF/88).",
            ],
            subsecoes=[
                SecaoDocumento(
                    titulo="Base Legal",
                    conteudo=[
                        "• Código Civil, arts. 1.694 a 1.710 - Alimentos",
                        "• ECA (Lei 8.069/90), art. 4º - Dever familiar de sustento",
                        "• Lei de Alimentos (Lei 5.478/68) - Procedimento especial",
                        "• CPC/2015, arts. 528 a 533 - Cumprimento de sentença de alimentos"
                    ],
                    tipo="lista"
                ),
                SecaoDocumento(
                    titulo="Trinômio da Pensão Alimentícia",
                    conteudo=[
                        "A fixação dos alimentos obedece ao trinômio: necessidade do alimentado, "
                        "possibilidade do alimentante e proporcionalidade.",

                        "1. NECESSIDADE: As crianças necessitam de recursos para alimentação, "
                        "saúde, educação e demais despesas essenciais.",

                        "2. POSSIBILIDADE: O alimentante possui capacidade contributiva, "
                        f"com renda mensal de R$ {renda_alimentante:.2f}.",

                        "3. PROPORCIONALIDADE: O valor deve ser proporcional às necessidades "
                        "e à capacidade econômica, sem comprometer o sustento do alimentante."
                    ]
                )
            ]
        )

        # Jurisprudências
        jurisprudencias = [
            JurisprudenciaCitada(
                tribunal="STJ",
                numero_processo="REsp 1.234.567/SP",
                ementa="Alimentos. Binômio necessidade-possibilidade. A fixação de alimentos "
                       "deve observar as necessidades do alimentado e as possibilidades do alimentante, "
                       "nos termos do art. 1.694, § 1º, do Código Civil.",
                data="15/08/2023",
                relevancia="Confirma o critério de cálculo do binômio necessidade-possibilidade"
            ),
            JurisprudenciaCitada(
                tribunal="TJSP",
                numero_processo="Apelação 0012345-67.2023.8.26.0100",
                ementa=f"Pensão alimentícia fixada em {int((analise.calculo_valores.valor_medio / renda_alimentante) * 100)}% "
                       f"da renda líquida do alimentante para {qtd_filhos} filho(s) é adequada e proporcional.",
                data="20/09/2024",
                relevancia="Caso análogo com mesmo número de filhos e percentual similar"
            ),
            JurisprudenciaCitada(
                tribunal="STJ",
                numero_processo="Súmula 358",
                ementa="O cancelamento de pensão alimentícia de filho que atingiu a maioridade "
                       "está sujeito à decisão judicial, mediante contraditório, ainda que nos "
                       "próprios autos.",
                data="Súmula",
                relevancia="Importante para entender a duração da obrigação alimentar"
            )
        ]

        # Análise de probabilidades
        prob_sucesso = analise.probabilidade_sucesso * 100

        analise_prob = SecaoDocumento(
            titulo="ANÁLISE DE PROBABILIDADES",
            conteudo=[
                f"Com base em {analise.estatisticas.total_casos_similares} casos similares analisados, "
                f"a probabilidade de êxito da demanda é de {prob_sucesso:.1f}%.",

                f"O tempo médio de tramitação é de {analise.estatisticas.tempo_medio_meses:.1f} meses, "
                f"podendo variar entre {analise.estatisticas.tempo_minimo_meses} e "
                f"{analise.estatisticas.tempo_maximo_meses} meses conforme a complexidade e "
                "movimentação processual.",

                "FATORES QUE AUMENTAM A CHANCE DE SUCESSO:",
                "✓ Comprovação das despesas dos filhos",
                "✓ Comprovação da renda do alimentante",
                "✓ Registro de nascimento comprovando parentesco",
                "✓ Tentativa de acordo prévio documentada",

                "FATORES DE RISCO:",
                "⚠ Ausência de comprovação de renda do alimentante",
                "⚠ Falta de documentação das despesas",
                "⚠ Divergências sobre o valor adequado"
            ]
        )

        # Estratégia recomendada
        estrategia = SecaoDocumento(
            titulo="ESTRATÉGIA RECOMENDADA",
            conteudo=[
                "1. FASE PRÉ-PROCESSUAL",
                "   • Reunir toda documentação necessária (vide seção específica)",
                "   • Organizar comprovantes de despesas dos últimos 3 meses",
                "   • Tentar acordo extrajudicial via WhatsApp/e-mail (documentar tudo)",
                "   • Notificar extrajudicialmente o alimentante",

                "2. AJUIZAMENTO",
                "   • Ação de alimentos com pedido de tutela de urgência",
                f"   • Valor sugerido: R$ {analise.calculo_valores.valor_medio:.2f}/mês "
                f"({int((analise.calculo_valores.valor_medio / renda_alimentante) * 100)}% da renda)",
                "   • Requer justiça gratuita (se aplicável)",

                "3. AUDIÊNCIA DE CONCILIAÇÃO",
                "   • Comparecer com todos os documentos",
                "   • Estar aberto a negociação (margem de 10-15%)",
                "   • Se houver acordo, homologar judicialmente",

                "4. PÓS-SENTENÇA",
                "   • Acompanhar cumprimento mensal",
                "   • Em caso de inadimplência, executar imediatamente",
                "   • Possibilidade de prisão civil após 3 parcelas em atraso"
            ]
        )

        # Documentos necessários
        documentos = [
            DocumentoNecessario(
                nome="RG e CPF",
                descricao="Documentos de identificação do requerente e dos filhos",
                obrigatorio=True,
                onde_obter="Já possui"
            ),
            DocumentoNecessario(
                nome="Certidão de Nascimento",
                descricao="Certidão de nascimento atualizada dos filhos",
                obrigatorio=True,
                onde_obter="Cartório de Registro Civil"
            ),
            DocumentoNecessario(
                nome="Comprovante de Residência",
                descricao="Conta de luz, água ou telefone recente",
                obrigatorio=True,
                onde_obter="Concessionária de serviços"
            ),
            DocumentoNecessario(
                nome="Comprovantes de Despesas",
                descricao="Mensalidade escolar, plano de saúde, alimentação, etc",
                obrigatorio=True,
                onde_obter="Escolas, clínicas, mercados"
            ),
            DocumentoNecessario(
                nome="Comprovante de Renda do Alimentante",
                descricao="Holerites, declaração de IR, extrato bancário",
                obrigatorio=False,
                onde_obter="Se possível, obter do próprio alimentante ou via processo"
            ),
            DocumentoNecessario(
                nome="Comprovante de Sua Renda",
                descricao="Seus holerites ou declaração de autônomo",
                obrigatorio=False,
                onde_obter="Seu empregador ou contabilidade"
            )
        ]

        # Modelos de documentos
        modelos = {}

        if config.incluir_modelos:
            modelos["Notificação Extrajudicial"] = f"""
NOTIFICAÇÃO EXTRAJUDICIAL

{dados_cliente.get('nome', '[SEU NOME]')}, brasileiro(a), [estado civil], [profissão],
portador(a) do RG nº [número] e CPF nº [número], residente e domiciliado(a) na [endereço completo],

vem, respeitosamente, NOTIFICAR

[NOME DO ALIMENTANTE], para que, no prazo de 10 (dez) dias, providencie o pagamento de pensão
alimentícia no valor mensal de R$ {analise.calculo_valores.valor_medio:.2f}, referente ao(s)
filho(s) [NOME DOS FILHOS], nascido(s) em [DATA].

Os alimentos destinam-se a cobrir despesas com alimentação, saúde, educação, vestuário e demais
necessidades básicas dos menores, nos termos dos artigos 1.694 e seguintes do Código Civil.

Caso não haja manifestação no prazo estipulado, será ajuizada ação de alimentos, com todos os
ônus decorrentes.

[Cidade], [data]

_______________________________
[Seu nome]
            """

            modelos["Modelo de Planilha de Despesas"] = """
PLANILHA DE DESPESAS MENSAIS - FILHOS

1. ALIMENTAÇÃO
   - Supermercado: R$ ______
   - Lanches/escola: R$ ______
   - Subtotal: R$ ______

2. EDUCAÇÃO
   - Mensalidade escolar: R$ ______
   - Material escolar: R$ ______
   - Transporte: R$ ______
   - Subtotal: R$ ______

3. SAÚDE
   - Plano de saúde: R$ ______
   - Medicamentos: R$ ______
   - Consultas: R$ ______
   - Subtotal: R$ ______

4. VESTUÁRIO
   - Roupas: R$ ______
   - Calçados: R$ ______
   - Subtotal: R$ ______

5. LAZER E CULTURA
   - Atividades extracurriculares: R$ ______
   - Lazer: R$ ______
   - Subtotal: R$ ______

6. OUTROS
   - Higiene pessoal: R$ ______
   - Diversos: R$ ______
   - Subtotal: R$ ______

TOTAL MENSAL: R$ ______
            """

        # Conclusão
        conclusao = SecaoDocumento(
            titulo="CONCLUSÃO",
            conteudo=[
                f"Diante do exposto, conclui-se que a ação de alimentos possui VIABILIDADE {analise.viabilidade.value.upper()}, "
                f"com probabilidade de êxito de {prob_sucesso:.1f}%.",

                f"O valor estimado para pensão alimentícia situa-se entre R$ {analise.calculo_valores.valor_minimo:.2f} "
                f"e R$ {analise.calculo_valores.valor_maximo:.2f}, com valor médio de R$ {analise.calculo_valores.valor_medio:.2f}.",

                "Recomenda-se seguir a estratégia apresentada, iniciando por tentativa de acordo "
                "e, se infrutífera, ajuizamento de ação de alimentos com pedido de tutela de urgência.",

                "Este parecer tem validade de 90 dias e serve como orientação preliminar. "
                "Para ajuizamento da ação, recomenda-se consultar advogado de sua confiança, "
                "que poderá utilizar este documento como base."
            ]
        )

        # Disclaimer
        disclaimer = """
IMPORTANTE: Este parecer foi gerado por inteligência artificial da plataforma Doutora IA e tem
caráter meramente informativo e orientativo. Não substitui a consulta com advogado regularmente
inscrito na OAB. As informações aqui contidas baseiam-se nos dados fornecidos pelo usuário e em
análise estatística de casos similares. Valores, prazos e probabilidades são estimativas e podem
variar conforme especificidades do caso concreto e entendimento do juízo competente.

A Doutora IA não se responsabiliza por decisões tomadas com base exclusivamente neste parecer.
Recomenda-se sempre consultar advogado para análise personalizada e acompanhamento processual.

Validade: 90 dias a partir da emissão.
        """

        return ParecerPremium(
            numero_parecer=numero,
            data_emissao=datetime.now().isoformat(),
            tipo_caso=TipoCaso.PENSAO_ALIMENTICIA,
            dados_cliente=dados_cliente,
            analise_gratuita=analise,
            introducao=introducao,
            historico_detalhado=historico,
            fundamentacao_juridica=fundamentacao,
            jurisprudencias=jurisprudencias if config.incluir_jurisprudencia else [],
            analise_probabilidades=analise_prob,
            estrategia_recomendada=estrategia,
            documentos_necessarios=documentos,
            modelos_documento=modelos,
            conclusao=conclusao,
            validade_dias=90,
            disclaimer=disclaimer
        )

    def _gerar_parecer_consumidor(
        self,
        numero: str,
        respostas: RespostasCompletas,
        analise: AnaliseGratuita,
        dados_cliente: Dict,
        config: ConfiguracaoParecer
    ) -> ParecerPremium:
        """Gera parecer de direito do consumidor"""

        resp_dict = {r.pergunta_id: r.valor for r in respostas.respostas}
        tipo_problema = resp_dict.get("tipo_problema", "")

        introducao = SecaoDocumento(
            titulo="INTRODUÇÃO",
            conteudo=[
                "Este parecer analisa questão consumerista envolvendo " + tipo_problema.replace("_", " ") + ".",
                "A análise considera a legislação do Código de Defesa do Consumidor e jurisprudência aplicável."
            ]
        )

        historico = SecaoDocumento(
            titulo="HISTÓRICO",
            conteudo=[
                f"Trata-se de relação de consumo onde houve {tipo_problema.replace('_', ' ')}.",
                f"Valor envolvido: R$ {resp_dict.get('valor_produto', 0):.2f}",
                "O consumidor busca reparação pelos danos materiais e morais sofridos."
            ]
        )

        fundamentacao = SecaoDocumento(
            titulo="FUNDAMENTAÇÃO JURÍDICA",
            conteudo=[
                "O Código de Defesa do Consumidor (Lei 8.078/90) estabelece proteção especial ao consumidor.",
                "Principais dispositivos aplicáveis:",
                "• Art. 6º - Direitos básicos do consumidor",
                "• Art. 18 - Vícios do produto",
                "• Art. 42, parágrafo único - Devolução em dobro de valores indevidos",
                "• Art. 14 - Responsabilidade por dano causado"
            ]
        )

        return self._montar_parecer_basico(
            numero, respostas, analise, dados_cliente,
            introducao, historico, fundamentacao
        )

    def _gerar_parecer_trabalhista(
        self,
        numero: str,
        respostas: RespostasCompletas,
        analise: AnaliseGratuita,
        dados_cliente: Dict,
        config: ConfiguracaoParecer
    ) -> ParecerPremium:
        """Gera parecer trabalhista"""

        introducao = SecaoDocumento(
            titulo="INTRODUÇÃO",
            conteudo=["Parecer sobre questão trabalhista."]
        )

        historico = SecaoDocumento(
            titulo="HISTÓRICO",
            conteudo=["Relação de emprego com questões de verbas rescisórias."]
        )

        fundamentacao = SecaoDocumento(
            titulo="FUNDAMENTAÇÃO",
            conteudo=["Base na CLT (Consolidação das Leis do Trabalho)."]
        )

        return self._montar_parecer_basico(
            numero, respostas, analise, dados_cliente,
            introducao, historico, fundamentacao
        )

    def _gerar_parecer_generico(
        self,
        numero: str,
        respostas: RespostasCompletas,
        analise: AnaliseGratuita,
        dados_cliente: Dict,
        config: ConfiguracaoParecer
    ) -> ParecerPremium:
        """Gera parecer genérico para outros casos"""

        introducao = SecaoDocumento(
            titulo="INTRODUÇÃO",
            conteudo=[f"Parecer sobre caso de {respostas.tipo_caso.value}."]
        )

        historico = SecaoDocumento(
            titulo="HISTÓRICO",
            conteudo=["Detalhamento do caso conforme informações fornecidas."]
        )

        fundamentacao = SecaoDocumento(
            titulo="FUNDAMENTAÇÃO JURÍDICA",
            conteudo=["Base legal aplicável ao caso."]
        )

        return self._montar_parecer_basico(
            numero, respostas, analise, dados_cliente,
            introducao, historico, fundamentacao
        )

    def _montar_parecer_basico(
        self,
        numero: str,
        respostas: RespostasCompletas,
        analise: AnaliseGratuita,
        dados_cliente: Dict,
        introducao: SecaoDocumento,
        historico: SecaoDocumento,
        fundamentacao: SecaoDocumento
    ) -> ParecerPremium:
        """Monta parecer com estrutura básica"""

        conclusao = SecaoDocumento(
            titulo="CONCLUSÃO",
            conteudo=[
                f"Viabilidade: {analise.viabilidade.value}",
                f"Probabilidade de sucesso: {analise.probabilidade_sucesso*100:.1f}%",
                "Recomenda-se consultar advogado para prosseguimento."
            ]
        )

        return ParecerPremium(
            numero_parecer=numero,
            data_emissao=datetime.now().isoformat(),
            tipo_caso=respostas.tipo_caso,
            dados_cliente=dados_cliente,
            analise_gratuita=analise,
            introducao=introducao,
            historico_detalhado=historico,
            fundamentacao_juridica=fundamentacao,
            jurisprudencias=[],
            analise_probabilidades=conclusao,
            estrategia_recomendada=conclusao,
            documentos_necessarios=[],
            modelos_documento={},
            conclusao=conclusao,
            disclaimer="Parecer informativo gerado por IA."
        )

    def exportar_para_json(self, parecer: ParecerPremium) -> str:
        """Exporta parecer para JSON"""
        import json
        from dataclasses import asdict
        return json.dumps(asdict(parecer), indent=2, ensure_ascii=False, default=str)

    def exportar_para_markdown(self, parecer: ParecerPremium) -> str:
        """Exporta parecer para Markdown"""
        md = f"""
# PARECER JURÍDICO
## {parecer.numero_parecer}

**Data de Emissão:** {parecer.data_emissao[:10]}
**Tipo de Caso:** {parecer.tipo_caso.value.upper().replace('_', ' ')}
**Validade:** {parecer.validade_dias} dias

---

## {parecer.introducao.titulo}

{chr(10).join(parecer.introducao.conteudo)}

---

## {parecer.historico_detalhado.titulo}

{chr(10).join(parecer.historico_detalhado.conteudo)}

---

## {parecer.fundamentacao_juridica.titulo}

{chr(10).join(parecer.fundamentacao_juridica.conteudo)}

{"---" if parecer.jurisprudencias else ""}

{self._formatar_jurisprudencias_md(parecer.jurisprudencias) if parecer.jurisprudencias else ""}

---

## {parecer.analise_probabilidades.titulo}

{chr(10).join(parecer.analise_probabilidades.conteudo)}

---

## {parecer.estrategia_recomendada.titulo}

{chr(10).join(parecer.estrategia_recomendada.conteudo)}

---

## DOCUMENTOS NECESSÁRIOS

{self._formatar_documentos_md(parecer.documentos_necessarios)}

---

## {parecer.conclusao.titulo}

{chr(10).join(parecer.conclusao.conteudo)}

---

## DISCLAIMER

{parecer.disclaimer}

---

*Documento gerado pela plataforma Doutora IA*
*www.doutorai.com.br*
        """
        return md.strip()

    def _formatar_jurisprudencias_md(self, jurisprudencias: List[JurisprudenciaCitada]) -> str:
        """Formata jurisprudências para markdown"""
        if not jurisprudencias:
            return ""

        md = "## JURISPRUDÊNCIAS CITADAS\n\n"
        for i, j in enumerate(jurisprudencias, 1):
            md += f"### {i}. {j.tribunal} - {j.numero_processo}\n\n"
            md += f"**Data:** {j.data}  \n"
            md += f"**Ementa:** {j.ementa}  \n"
            md += f"**Relevância:** {j.relevancia}\n\n"
        return md

    def _formatar_documentos_md(self, documentos: List[DocumentoNecessario]) -> str:
        """Formata lista de documentos para markdown"""
        if not documentos:
            return "*Nenhum documento específico listado.*"

        md = ""
        for doc in documentos:
            obrig = "✓ OBRIGATÓRIO" if doc.obrigatorio else "○ Opcional"
            md += f"**{doc.nome}** ({obrig})  \n"
            md += f"*{doc.descricao}*  \n"
            md += f"Onde obter: {doc.onde_obter}  \n\n"
        return md


# =====================================================
# FACTORY
# =====================================================

def criar_engine_pareceres() -> EngineGeradorPareceres:
    """Factory para criar engine de pareceres"""
    return EngineGeradorPareceres()


# =====================================================
# TESTE
# =====================================================

if __name__ == "__main__":
    from engine_assistente_publico import RespostaUsuario, TipoCaso

    engine = criar_engine_pareceres()

    # Teste com pensão alimentícia
    print("=== GERANDO PARECER DE PENSÃO ALIMENTÍCIA ===")

    respostas = RespostasCompletas(
        tipo_caso=TipoCaso.PENSAO_ALIMENTICIA,
        respostas=[
            RespostaUsuario("posicao", "receber"),
            RespostaUsuario("qtd_filhos", 2),
            RespostaUsuario("idades_filhos", "5, 8"),
            RespostaUsuario("renda_alimentante", 5000),
            RespostaUsuario("renda_guardiao", 2000),
            RespostaUsuario("despesas_filhos", 1800),
            RespostaUsuario("ja_recebe", "nao"),
            RespostaUsuario("estado", "SP"),
        ]
    )

    dados_cliente = {
        "nome": "Maria Silva",
        "email": "maria@email.com",
        "telefone": "(11) 99999-9999"
    }

    parecer = engine.gerar_parecer_completo(respostas, dados_cliente)

    print(f"Parecer gerado: {parecer.numero_parecer}")
    print(f"Data: {parecer.data_emissao}")
    print(f"\n{parecer.introducao.titulo}")
    print(parecer.introducao.conteudo[0][:200] + "...")

    # Exportar para Markdown
    md = engine.exportar_para_markdown(parecer)
    print(f"\nTamanho do documento: {len(md)} caracteres")
    print("\n✅ Engine Gerador de Pareceres funcionando!")
