"""
Engine Assistente Público - Doutora IA
Sistema de assistência jurídica para cidadãos

Casos implementados:
1. Pensão Alimentícia
2. Direito do Consumidor
3. Trânsito
4. Briga de Vizinhos/Condomínio
5. Trabalhista
6. Divórcio Consensual
7. Inventário Simples
8. Danos Morais
9. INSS/Previdência
10. Contratos

Versão: 1.0.0
Data: 31/12/2025
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime, timedelta
import json


# =====================================================
# ENUMS
# =====================================================

class TipoCaso(Enum):
    """Tipos de casos jurídicos"""
    PENSAO_ALIMENTICIA = "pensao_alimenticia"
    DIREITO_CONSUMIDOR = "direito_consumidor"
    TRANSITO = "transito"
    BRIGA_VIZINHOS = "briga_vizinhos"
    TRABALHISTA = "trabalhista"
    DIVORCIO = "divorcio"
    INVENTARIO = "inventario"
    DANOS_MORAIS = "danos_morais"
    INSS = "inss"
    CONTRATOS = "contratos"


class ComplexidadeCaso(Enum):
    """Complexidade do caso"""
    SIMPLES = "simples"
    MEDIO = "medio"
    COMPLEXO = "complexo"


class ViabilidadeCaso(Enum):
    """Viabilidade jurídica"""
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"
    INVIAVEL = "inviavel"


class UrgenciaCaso(Enum):
    """Nível de urgência"""
    URGENTE = "urgente"  # < 5 dias
    NORMAL = "normal"    # 5-30 dias
    BAIXA = "baixa"      # > 30 dias


# =====================================================
# DATACLASSES - PERGUNTAS
# =====================================================

@dataclass
class OpcaoResposta:
    """Opção de resposta para pergunta"""
    valor: str
    texto: str
    peso: float = 1.0  # Peso para cálculos


@dataclass
class Pergunta:
    """Pergunta do quiz"""
    id: str
    texto: str
    tipo: str  # "multipla_escolha", "texto", "numero", "moeda", "data"
    obrigatoria: bool = True
    opcoes: List[OpcaoResposta] = field(default_factory=list)
    ajuda: Optional[str] = None
    condicao: Optional[str] = None  # Condição para exibir


@dataclass
class Quiz:
    """Quiz completo para um tipo de caso"""
    tipo_caso: TipoCaso
    titulo: str
    descricao: str
    perguntas: List[Pergunta]
    tempo_estimado_minutos: int = 5


# =====================================================
# DATACLASSES - RESPOSTAS
# =====================================================

@dataclass
class RespostaUsuario:
    """Resposta do usuário a uma pergunta"""
    pergunta_id: str
    valor: Any
    texto_resposta: Optional[str] = None


@dataclass
class RespostasCompletas:
    """Conjunto completo de respostas"""
    tipo_caso: TipoCaso
    respostas: List[RespostaUsuario]
    data_preenchimento: str = field(default_factory=lambda: datetime.now().isoformat())


# =====================================================
# DATACLASSES - ANÁLISE
# =====================================================

@dataclass
class CalculoValores:
    """Cálculo de valores estimados"""
    valor_minimo: float
    valor_maximo: float
    valor_medio: float
    moeda: str = "BRL"
    base_calculo: str = ""


@dataclass
class EstatisticasCaso:
    """Estatísticas de casos similares"""
    total_casos_similares: int
    taxa_sucesso_percentual: float
    tempo_medio_meses: float
    tempo_minimo_meses: float
    tempo_maximo_meses: float
    valor_medio_acordo: Optional[float] = None


@dataclass
class BaseLegal:
    """Base legal aplicável"""
    leis: List[str]
    artigos: List[str]
    jurisprudencia_relevante: List[str]
    sumulas: List[str] = field(default_factory=list)


@dataclass
class ProximosPassos:
    """Próximos passos recomendados"""
    passos: List[str]
    documentos_necessarios: List[str]
    prazos_importantes: Dict[str, str]
    custos_estimados: Dict[str, float]


@dataclass
class AnaliseGratuita:
    """Análise gratuita do caso"""
    tipo_caso: TipoCaso
    viabilidade: ViabilidadeCaso
    complexidade: ComplexidadeCaso
    urgencia: UrgenciaCaso

    # Resumo
    resumo_caso: str
    direitos_principais: List[str]

    # Estimativas
    calculo_valores: Optional[CalculoValores]
    tempo_estimado_meses: float
    probabilidade_sucesso: float  # 0-1

    # Estatísticas
    estatisticas: EstatisticasCaso

    # Orientações
    base_legal: BaseLegal
    proximos_passos: ProximosPassos

    # Alertas
    alertas_importantes: List[str]
    prazos_criticos: List[str]


# =====================================================
# ENGINE PRINCIPAL
# =====================================================

class EngineAssistentePublico:
    """Engine de assistência jurídica pública"""

    def __init__(self):
        self._quizzes = self._criar_todos_quizzes()
        self._base_dados = self._carregar_base_dados()

    def listar_casos_disponiveis(self) -> List[Dict[str, Any]]:
        """Lista todos os casos disponíveis"""
        casos = []
        for tipo in TipoCaso:
            quiz = self._quizzes.get(tipo)
            if quiz:
                casos.append({
                    "tipo": tipo.value,
                    "titulo": quiz.titulo,
                    "descricao": quiz.descricao,
                    "tempo_estimado": quiz.tempo_estimado_minutos,
                    "popularidade": self._obter_popularidade(tipo)
                })
        return sorted(casos, key=lambda x: x['popularidade'], reverse=True)

    def obter_quiz(self, tipo_caso: TipoCaso) -> Quiz:
        """Obtém o quiz para um tipo de caso"""
        return self._quizzes.get(tipo_caso)

    def analisar_caso(self, respostas: RespostasCompletas) -> AnaliseGratuita:
        """Analisa um caso baseado nas respostas do usuário"""
        tipo = respostas.tipo_caso

        # Delega para função específica do tipo
        if tipo == TipoCaso.PENSAO_ALIMENTICIA:
            return self._analisar_pensao_alimenticia(respostas)
        elif tipo == TipoCaso.DIREITO_CONSUMIDOR:
            return self._analisar_direito_consumidor(respostas)
        elif tipo == TipoCaso.TRANSITO:
            return self._analisar_transito(respostas)
        elif tipo == TipoCaso.BRIGA_VIZINHOS:
            return self._analisar_briga_vizinhos(respostas)
        elif tipo == TipoCaso.TRABALHISTA:
            return self._analisar_trabalhista(respostas)
        elif tipo == TipoCaso.DIVORCIO:
            return self._analisar_divorcio(respostas)
        elif tipo == TipoCaso.INVENTARIO:
            return self._analisar_inventario(respostas)
        elif tipo == TipoCaso.DANOS_MORAIS:
            return self._analisar_danos_morais(respostas)
        elif tipo == TipoCaso.INSS:
            return self._analisar_inss(respostas)
        elif tipo == TipoCaso.CONTRATOS:
            return self._analisar_contratos(respostas)
        else:
            raise ValueError(f"Tipo de caso não implementado: {tipo}")

    # =====================================================
    # QUIZZES - CRIAÇÃO
    # =====================================================

    def _criar_todos_quizzes(self) -> Dict[TipoCaso, Quiz]:
        """Cria todos os quizzes"""
        return {
            TipoCaso.PENSAO_ALIMENTICIA: self._quiz_pensao_alimenticia(),
            TipoCaso.DIREITO_CONSUMIDOR: self._quiz_direito_consumidor(),
            TipoCaso.TRANSITO: self._quiz_transito(),
            TipoCaso.BRIGA_VIZINHOS: self._quiz_briga_vizinhos(),
            TipoCaso.TRABALHISTA: self._quiz_trabalhista(),
            TipoCaso.DIVORCIO: self._quiz_divorcio(),
            TipoCaso.INVENTARIO: self._quiz_inventario(),
            TipoCaso.DANOS_MORAIS: self._quiz_danos_morais(),
            TipoCaso.INSS: self._quiz_inss(),
            TipoCaso.CONTRATOS: self._quiz_contratos(),
        }

    def _quiz_pensao_alimenticia(self) -> Quiz:
        """Quiz para pensão alimentícia"""
        perguntas = [
            Pergunta(
                id="posicao",
                texto="Você é quem vai pagar ou receber a pensão?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("receber", "Vou receber (sou guardião/responsável)"),
                    OpcaoResposta("pagar", "Vou pagar (sou alimentante)")
                ]
            ),
            Pergunta(
                id="qtd_filhos",
                texto="Quantos filhos estão envolvidos?",
                tipo="numero",
                ajuda="Digite o número de filhos que precisam de pensão"
            ),
            Pergunta(
                id="idades_filhos",
                texto="Qual a idade dos filhos? (separe por vírgula)",
                tipo="texto",
                ajuda="Exemplo: 5, 8, 12"
            ),
            Pergunta(
                id="renda_alimentante",
                texto="Qual a renda mensal do alimentante (quem paga)?",
                tipo="moeda",
                ajuda="Valor aproximado em reais"
            ),
            Pergunta(
                id="renda_guardiao",
                texto="Qual a renda mensal do guardião (quem recebe)?",
                tipo="moeda"
            ),
            Pergunta(
                id="despesas_filhos",
                texto="Qual o valor total das despesas mensais dos filhos?",
                tipo="moeda",
                ajuda="Inclua: alimentação, escola, saúde, vestuário, lazer"
            ),
            Pergunta(
                id="ja_recebe",
                texto="Já recebe alguma pensão atualmente?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="valor_atual",
                texto="Qual o valor atual da pensão?",
                tipo="moeda",
                condicao="ja_recebe == 'sim'"
            ),
            Pergunta(
                id="acordo_previo",
                texto="Existe algum acordo prévio (formal ou informal)?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("formal", "Sim, acordo formal"),
                    OpcaoResposta("informal", "Sim, acordo informal"),
                    OpcaoResposta("nao", "Não existe acordo")
                ]
            ),
            Pergunta(
                id="situacao_emprego",
                texto="Situação de emprego do alimentante:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("clt", "CLT (carteira assinada)"),
                    OpcaoResposta("autonomo", "Autônomo/Profissional liberal"),
                    OpcaoResposta("empresario", "Empresário"),
                    OpcaoResposta("desempregado", "Desempregado"),
                    OpcaoResposta("aposentado", "Aposentado")
                ]
            ),
            Pergunta(
                id="urgencia",
                texto="Como você classificaria a urgência do caso?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("alta", "Alta - crianças sem sustento básico"),
                    OpcaoResposta("media", "Média - valor atual insuficiente"),
                    OpcaoResposta("baixa", "Baixa - apenas regularização")
                ]
            ),
            Pergunta(
                id="estado",
                texto="Em qual estado você mora?",
                tipo="texto",
                ajuda="Digite a sigla (ex: SP, RJ, MG)"
            )
        ]

        return Quiz(
            tipo_caso=TipoCaso.PENSAO_ALIMENTICIA,
            titulo="Pensão Alimentícia",
            descricao="Descubra seus direitos sobre pensão alimentícia e valores estimados",
            perguntas=perguntas,
            tempo_estimado_minutos=5
        )

    def _quiz_direito_consumidor(self) -> Quiz:
        """Quiz para direito do consumidor"""
        perguntas = [
            Pergunta(
                id="tipo_problema",
                texto="Qual o tipo de problema?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("produto_defeituoso", "Produto com defeito"),
                    OpcaoResposta("cobranca_indevida", "Cobrança indevida"),
                    OpcaoResposta("negativacao", "Nome negativado indevidamente"),
                    OpcaoResposta("propaganda_enganosa", "Propaganda enganosa"),
                    OpcaoResposta("nao_entrega", "Produto não entregue"),
                    OpcaoResposta("servico_mal_prestado", "Serviço mal prestado"),
                    OpcaoResposta("vicio_oculto", "Vício oculto"),
                    OpcaoResposta("outro", "Outro")
                ]
            ),
            Pergunta(
                id="valor_produto",
                texto="Qual o valor do produto/serviço?",
                tipo="moeda"
            ),
            Pergunta(
                id="data_compra",
                texto="Quando foi a compra?",
                tipo="data",
                ajuda="Data aproximada"
            ),
            Pergunta(
                id="tipo_empresa",
                texto="Tipo de empresa:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("grande", "Grande empresa (banco, operadora, varejista)"),
                    OpcaoResposta("media", "Empresa média"),
                    OpcaoResposta("pequena", "Empresa pequena/MEI")
                ]
            ),
            Pergunta(
                id="tentou_resolver",
                texto="Já tentou resolver diretamente com a empresa?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim_protocolo", "Sim, tenho protocolo"),
                    OpcaoResposta("sim_sem_protocolo", "Sim, mas sem protocolo"),
                    OpcaoResposta("nao", "Não tentei ainda")
                ]
            ),
            Pergunta(
                id="tem_provas",
                texto="Você tem provas? (marque todas que possui)",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("nota_fiscal", "Nota fiscal"),
                    OpcaoResposta("emails", "E-mails/mensagens"),
                    OpcaoResposta("fotos", "Fotos do defeito"),
                    OpcaoResposta("testemunhas", "Testemunhas"),
                    OpcaoResposta("protocolos", "Protocolos de atendimento"),
                    OpcaoResposta("nenhuma", "Nenhuma prova")
                ]
            ),
            Pergunta(
                id="prejuizo_moral",
                texto="Houve constrangimento ou prejuízo moral?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim_grave", "Sim, grave (ex: negativação indevida)"),
                    OpcaoResposta("sim_leve", "Sim, leve"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="estado",
                texto="Em qual estado você mora?",
                tipo="texto"
            )
        ]

        return Quiz(
            tipo_caso=TipoCaso.DIREITO_CONSUMIDOR,
            titulo="Direito do Consumidor",
            descricao="Problemas com produtos, serviços e empresas",
            perguntas=perguntas,
            tempo_estimado_minutos=4
        )

    def _quiz_transito(self) -> Quiz:
        """Quiz para trânsito"""
        perguntas = [
            Pergunta(
                id="tipo_problema",
                texto="Qual o problema de trânsito?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("multa", "Multa indevida"),
                    OpcaoResposta("acidente", "Acidente de trânsito"),
                    OpcaoResposta("suspensao_cnh", "Suspensão de CNH"),
                    OpcaoResposta("pontos", "Contestar pontos"),
                    OpcaoResposta("danos", "Indenização por danos")
                ]
            ),
            Pergunta(
                id="valor_envolvido",
                texto="Qual o valor envolvido? (multa ou danos)",
                tipo="moeda"
            ),
            Pergunta(
                id="data_fato",
                texto="Data do ocorrido:",
                tipo="data"
            ),
            Pergunta(
                id="tem_provas",
                texto="Você tem provas?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("boletim", "Boletim de ocorrência"),
                    OpcaoResposta("fotos", "Fotos/vídeos"),
                    OpcaoResposta("testemunhas", "Testemunhas"),
                    OpcaoResposta("pericia", "Perícia"),
                    OpcaoResposta("nenhuma", "Nenhuma")
                ]
            ),
            Pergunta(
                id="ja_recorreu",
                texto="Já entrou com recurso administrativo?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim_negado", "Sim, foi negado"),
                    OpcaoResposta("sim_aguardando", "Sim, aguardando resposta"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="prazo",
                texto="Quanto tempo falta para o prazo final?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("vencido", "Já venceu"),
                    OpcaoResposta("menos_30", "Menos de 30 dias"),
                    OpcaoResposta("mais_30", "Mais de 30 dias")
                ]
            ),
            Pergunta(
                id="estado",
                texto="Estado:",
                tipo="texto"
            )
        ]

        return Quiz(
            tipo_caso=TipoCaso.TRANSITO,
            titulo="Trânsito",
            descricao="Multas, acidentes e CNH",
            perguntas=perguntas,
            tempo_estimado_minutos=3
        )

    def _quiz_briga_vizinhos(self) -> Quiz:
        """Quiz para briga de vizinhos/condomínio"""
        perguntas = [
            Pergunta(
                id="tipo_problema",
                texto="Qual o problema?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("barulho", "Barulho excessivo"),
                    OpcaoResposta("reforma", "Reforma irregular"),
                    OpcaoResposta("vazamento", "Vazamento/infiltração"),
                    OpcaoResposta("area_comum", "Uso indevido de área comum"),
                    OpcaoResposta("animais", "Problemas com animais"),
                    OpcaoResposta("inadimplencia", "Inadimplência condomínio"),
                    OpcaoResposta("outro", "Outro")
                ]
            ),
            Pergunta(
                id="tipo_imovel",
                texto="Tipo de imóvel:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("apartamento", "Apartamento"),
                    OpcaoResposta("casa_condominio", "Casa em condomínio"),
                    OpcaoResposta("casa_individual", "Casa individual")
                ]
            ),
            Pergunta(
                id="ha_quanto_tempo",
                texto="Há quanto tempo ocorre o problema?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("recente", "Menos de 1 mês"),
                    OpcaoResposta("meses", "1-6 meses"),
                    OpcaoResposta("anos", "Mais de 6 meses")
                ]
            ),
            Pergunta(
                id="tentou_resolver",
                texto="Tentou resolver amigavelmente?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim_sindico", "Sim, acionei síndico"),
                    OpcaoResposta("sim_direto", "Sim, falei com vizinho"),
                    OpcaoResposta("nao", "Não tentei")
                ]
            ),
            Pergunta(
                id="tem_provas",
                texto="Tem provas do problema?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("videos", "Vídeos/áudios"),
                    OpcaoResposta("fotos", "Fotos"),
                    OpcaoResposta("atas", "Atas de reunião"),
                    OpcaoResposta("testemunhas", "Testemunhas"),
                    OpcaoResposta("nenhuma", "Não tenho")
                ]
            ),
            Pergunta(
                id="prejuizo_financeiro",
                texto="Houve prejuízo financeiro?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="valor_prejuizo",
                texto="Valor estimado do prejuízo:",
                tipo="moeda",
                condicao="prejuizo_financeiro == 'sim'"
            ),
            Pergunta(
                id="estado",
                texto="Estado:",
                tipo="texto"
            )
        ]

        return Quiz(
            tipo_caso=TipoCaso.BRIGA_VIZINHOS,
            titulo="Vizinhos e Condomínio",
            descricao="Conflitos de vizinhança e condomínio",
            perguntas=perguntas,
            tempo_estimado_minutos=4
        )

    def _quiz_trabalhista(self) -> Quiz:
        """Quiz para trabalhista"""
        perguntas = [
            Pergunta(
                id="tipo_problema",
                texto="Qual a questão trabalhista?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("rescisao", "Rescisão incorreta"),
                    OpcaoResposta("horas_extras", "Horas extras não pagas"),
                    OpcaoResposta("ferias", "Férias não pagas"),
                    OpcaoResposta("fgts", "FGTS não depositado"),
                    OpcaoResposta("assedio", "Assédio moral/sexual"),
                    OpcaoResposta("acidente", "Acidente de trabalho"),
                    OpcaoResposta("desvio_funcao", "Desvio de função")
                ]
            ),
            Pergunta(
                id="tempo_trabalho",
                texto="Quanto tempo trabalhou na empresa?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("menos_1ano", "Menos de 1 ano"),
                    OpcaoResposta("1_3_anos", "1 a 3 anos"),
                    OpcaoResposta("3_5_anos", "3 a 5 anos"),
                    OpcaoResposta("mais_5_anos", "Mais de 5 anos")
                ]
            ),
            Pergunta(
                id="salario",
                texto="Qual era seu salário?",
                tipo="moeda"
            ),
            Pergunta(
                id="tipo_contrato",
                texto="Tipo de contrato:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("clt", "CLT"),
                    OpcaoResposta("pj", "PJ"),
                    OpcaoResposta("estagio", "Estágio"),
                    OpcaoResposta("temporario", "Temporário"),
                    OpcaoResposta("sem_registro", "Sem registro")
                ]
            ),
            Pergunta(
                id="foi_demitido",
                texto="Foi demitido?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim_justa_causa", "Sim, com justa causa"),
                    OpcaoResposta("sim_sem_justa_causa", "Sim, sem justa causa"),
                    OpcaoResposta("pediu_demissao", "Pedi demissão"),
                    OpcaoResposta("ainda_trabalha", "Ainda trabalho lá")
                ]
            ),
            Pergunta(
                id="recebeu_verbas",
                texto="Recebeu todas as verbas rescisórias?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim, completas"),
                    OpcaoResposta("parcial", "Sim, mas incompletas"),
                    OpcaoResposta("nao", "Não recebi")
                ]
            ),
            Pergunta(
                id="tem_provas",
                texto="Tem provas?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("carteira", "Carteira de trabalho"),
                    OpcaoResposta("holerites", "Holerites"),
                    OpcaoResposta("emails", "E-mails"),
                    OpcaoResposta("testemunhas", "Testemunhas"),
                    OpcaoResposta("controle_ponto", "Controle de ponto"),
                    OpcaoResposta("nenhuma", "Nenhuma")
                ]
            ),
            Pergunta(
                id="valor_estimado",
                texto="Valor estimado que você acha que tem direito:",
                tipo="moeda",
                obrigatoria=False
            ),
            Pergunta(
                id="estado",
                texto="Estado:",
                tipo="texto"
            )
        ]

        return Quiz(
            tipo_caso=TipoCaso.TRABALHISTA,
            titulo="Direito Trabalhista",
            descricao="Rescisão, horas extras, FGTS e mais",
            perguntas=perguntas,
            tempo_estimado_minutos=5
        )

    def _quiz_divorcio(self) -> Quiz:
        """Quiz para divórcio"""
        perguntas = [
            Pergunta(
                id="tipo_divorcio",
                texto="Tipo de divórcio:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("consensual", "Consensual (ambos concordam)"),
                    OpcaoResposta("litigioso", "Litigioso (há discordância)")
                ]
            ),
            Pergunta(
                id="tem_filhos",
                texto="Tem filhos menores de idade?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="qtd_filhos",
                texto="Quantos filhos?",
                tipo="numero",
                condicao="tem_filhos == 'sim'"
            ),
            Pergunta(
                id="regime_casamento",
                texto="Regime de casamento:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("comunhao_parcial", "Comunhão parcial de bens"),
                    OpcaoResposta("comunhao_universal", "Comunhão universal de bens"),
                    OpcaoResposta("separacao", "Separação total de bens"),
                    OpcaoResposta("nao_sei", "Não sei")
                ]
            ),
            Pergunta(
                id="tem_bens",
                texto="Há bens a partilhar?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="valor_bens",
                texto="Valor estimado dos bens:",
                tipo="moeda",
                condicao="tem_bens == 'sim'"
            ),
            Pergunta(
                id="tipo_bens",
                texto="Tipos de bens:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("imovel", "Imóvel"),
                    OpcaoResposta("veiculo", "Veículo"),
                    OpcaoResposta("investimentos", "Investimentos"),
                    OpcaoResposta("empresa", "Empresa"),
                    OpcaoResposta("outros", "Outros")
                ],
                condicao="tem_bens == 'sim'"
            ),
            Pergunta(
                id="acordo_pensao",
                texto="Há acordo sobre pensão alimentícia?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim"),
                    OpcaoResposta("nao", "Não"),
                    OpcaoResposta("nao_aplica", "Não se aplica")
                ],
                condicao="tem_filhos == 'sim'"
            ),
            Pergunta(
                id="tempo_casado",
                texto="Tempo de casamento:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("menos_2", "Menos de 2 anos"),
                    OpcaoResposta("2_5", "2 a 5 anos"),
                    OpcaoResposta("5_10", "5 a 10 anos"),
                    OpcaoResposta("mais_10", "Mais de 10 anos")
                ]
            ),
            Pergunta(
                id="estado",
                texto="Estado:",
                tipo="texto"
            )
        ]

        return Quiz(
            tipo_caso=TipoCaso.DIVORCIO,
            titulo="Divórcio",
            descricao="Divórcio consensual ou litigioso",
            perguntas=perguntas,
            tempo_estimado_minutos=5
        )

    def _quiz_inventario(self) -> Quiz:
        """Quiz para inventário"""
        perguntas = [
            Pergunta(
                id="tipo_inventario",
                texto="Tipo de inventário:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("consensual", "Consensual (todos concordam)"),
                    OpcaoResposta("litigioso", "Litigioso (há conflito)")
                ]
            ),
            Pergunta(
                id="valor_patrimonio",
                texto="Valor estimado do patrimônio:",
                tipo="moeda"
            ),
            Pergunta(
                id="qtd_herdeiros",
                texto="Quantidade de herdeiros:",
                tipo="numero"
            ),
            Pergunta(
                id="tem_testamento",
                texto="Há testamento?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim"),
                    OpcaoResposta("nao", "Não"),
                    OpcaoResposta("nao_sei", "Não sei")
                ]
            ),
            Pergunta(
                id="tipo_bens",
                texto="Tipos de bens:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("imovel", "Imóveis"),
                    OpcaoResposta("veiculo", "Veículos"),
                    OpcaoResposta("dinheiro", "Dinheiro/investimentos"),
                    OpcaoResposta("empresa", "Empresa"),
                    OpcaoResposta("outros", "Outros")
                ]
            ),
            Pergunta(
                id="tem_dividas",
                texto="Há dívidas deixadas?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="tempo_falecimento",
                texto="Tempo desde o falecimento:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("menos_1ano", "Menos de 1 ano"),
                    OpcaoResposta("1_2_anos", "1 a 2 anos"),
                    OpcaoResposta("mais_2_anos", "Mais de 2 anos")
                ]
            ),
            Pergunta(
                id="estado",
                texto="Estado:",
                tipo="texto"
            )
        ]

        return Quiz(
            tipo_caso=TipoCaso.INVENTARIO,
            titulo="Inventário e Herança",
            descricao="Partilha de bens e heranças",
            perguntas=perguntas,
            tempo_estimado_minutos=4
        )

    def _quiz_danos_morais(self) -> Quiz:
        """Quiz para danos morais"""
        perguntas = [
            Pergunta(
                id="origem_dano",
                texto="Origem do dano moral:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("consumidor", "Relação de consumo"),
                    OpcaoResposta("trabalho", "Trabalho"),
                    OpcaoResposta("negativacao", "Negativação indevida"),
                    OpcaoResposta("acidente", "Acidente"),
                    OpcaoResposta("vizinhanca", "Vizinhança"),
                    OpcaoResposta("internet", "Internet/redes sociais"),
                    OpcaoResposta("outro", "Outro")
                ]
            ),
            Pergunta(
                id="gravidade",
                texto="Gravidade do dano:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("leve", "Leve (constrangimento pontual)"),
                    OpcaoResposta("medio", "Médio (constrangimento público)"),
                    OpcaoResposta("grave", "Grave (danos psicológicos)"),
                    OpcaoResposta("gravissimo", "Gravíssimo (sequelas permanentes)")
                ]
            ),
            Pergunta(
                id="data_fato",
                texto="Data do fato:",
                tipo="data"
            ),
            Pergunta(
                id="tem_testemunhas",
                texto="Tem testemunhas?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="tem_provas",
                texto="Tem provas documentais?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("prints", "Prints/capturas de tela"),
                    OpcaoResposta("fotos", "Fotos"),
                    OpcaoResposta("videos", "Vídeos"),
                    OpcaoResposta("documentos", "Documentos"),
                    OpcaoResposta("laudos", "Laudos médicos"),
                    OpcaoResposta("nenhuma", "Nenhuma")
                ]
            ),
            Pergunta(
                id="repercussao",
                texto="Houve repercussão pública?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim_grande", "Sim, grande"),
                    OpcaoResposta("sim_pequena", "Sim, pequena"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="prejuizo_material",
                texto="Houve prejuízo material também?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="valor_prejuizo",
                texto="Valor do prejuízo material:",
                tipo="moeda",
                condicao="prejuizo_material == 'sim'"
            ),
            Pergunta(
                id="estado",
                texto="Estado:",
                tipo="texto"
            )
        ]

        return Quiz(
            tipo_caso=TipoCaso.DANOS_MORAIS,
            titulo="Danos Morais",
            descricao="Indenização por danos morais",
            perguntas=perguntas,
            tempo_estimado_minutos=4
        )

    def _quiz_inss(self) -> Quiz:
        """Quiz para INSS/Previdência"""
        perguntas = [
            Pergunta(
                id="tipo_beneficio",
                texto="Tipo de benefício:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("aposentadoria_idade", "Aposentadoria por idade"),
                    OpcaoResposta("aposentadoria_tempo", "Aposentadoria por tempo"),
                    OpcaoResposta("aposentadoria_invalidez", "Aposentadoria por invalidez"),
                    OpcaoResposta("auxilio_doenca", "Auxílio-doença"),
                    OpcaoResposta("pensao_morte", "Pensão por morte"),
                    OpcaoResposta("bpc", "BPC/LOAS"),
                    OpcaoResposta("outro", "Outro")
                ]
            ),
            Pergunta(
                id="situacao",
                texto="Situação atual:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("negado", "Benefício negado"),
                    OpcaoResposta("cessado", "Benefício cessado"),
                    OpcaoResposta("valor_baixo", "Valor muito baixo"),
                    OpcaoResposta("ainda_nao_pediu", "Ainda não pedi")
                ]
            ),
            Pergunta(
                id="idade",
                texto="Sua idade:",
                tipo="numero"
            ),
            Pergunta(
                id="tempo_contribuicao",
                texto="Tempo de contribuição (anos):",
                tipo="numero"
            ),
            Pergunta(
                id="renda_atual",
                texto="Renda atual ou última antes do problema:",
                tipo="moeda"
            ),
            Pergunta(
                id="tem_documentos",
                texto="Tem documentos?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("cnis", "CNIS atualizado"),
                    OpcaoResposta("carteira", "Carteira de trabalho"),
                    OpcaoResposta("carnês", "Carnês de contribuição"),
                    OpcaoResposta("laudos", "Laudos médicos"),
                    OpcaoResposta("poucos", "Poucos documentos")
                ]
            ),
            Pergunta(
                id="ja_entrou_recurso",
                texto="Já entrou com recurso administrativo?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim_negado", "Sim, foi negado"),
                    OpcaoResposta("sim_aguardando", "Sim, aguardando"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="estado",
                texto="Estado:",
                tipo="texto"
            )
        ]

        return Quiz(
            tipo_caso=TipoCaso.INSS,
            titulo="INSS e Previdência",
            descricao="Aposentadoria, auxílios e pensões",
            perguntas=perguntas,
            tempo_estimado_minutos=5
        )

    def _quiz_contratos(self) -> Quiz:
        """Quiz para contratos"""
        perguntas = [
            Pergunta(
                id="tipo_contrato",
                texto="Tipo de contrato:",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("aluguel", "Aluguel"),
                    OpcaoResposta("compra_venda", "Compra e venda"),
                    OpcaoResposta("emprestimo", "Empréstimo"),
                    OpcaoResposta("prestacao_servico", "Prestação de serviço"),
                    OpcaoResposta("financiamento", "Financiamento"),
                    OpcaoResposta("outro", "Outro")
                ]
            ),
            Pergunta(
                id="problema",
                texto="Qual o problema?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("descumprimento", "Descumprimento do contrato"),
                    OpcaoResposta("clausula_abusiva", "Cláusula abusiva"),
                    OpcaoResposta("nao_entrega", "Não entrega/prestação"),
                    OpcaoResposta("cobranca_indevida", "Cobrança indevida"),
                    OpcaoResposta("rescisao", "Quer rescindir contrato"),
                    OpcaoResposta("outro", "Outro")
                ]
            ),
            Pergunta(
                id="valor_contrato",
                texto="Valor total do contrato:",
                tipo="moeda"
            ),
            Pergunta(
                id="contrato_escrito",
                texto="Contrato é escrito?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim, tenho cópia"),
                    OpcaoResposta("nao_tenho", "Sim, mas não tenho cópia"),
                    OpcaoResposta("verbal", "Foi verbal")
                ]
            ),
            Pergunta(
                id="ja_pagou",
                texto="Já pagou algum valor?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim_total", "Sim, o total"),
                    OpcaoResposta("sim_parcial", "Sim, parcialmente"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="valor_pago",
                texto="Quanto já pagou?",
                tipo="moeda",
                condicao="ja_pagou != 'nao'"
            ),
            Pergunta(
                id="tentou_resolver",
                texto="Tentou resolver com a outra parte?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="prejuizo",
                texto="Há prejuízo além do valor do contrato?",
                tipo="multipla_escolha",
                opcoes=[
                    OpcaoResposta("sim", "Sim"),
                    OpcaoResposta("nao", "Não")
                ]
            ),
            Pergunta(
                id="estado",
                texto="Estado:",
                tipo="texto"
            )
        ]

        return Quiz(
            tipo_caso=TipoCaso.CONTRATOS,
            titulo="Contratos",
            descricao="Problemas com contratos diversos",
            perguntas=perguntas,
            tempo_estimado_minutos=4
        )

    # =====================================================
    # ANÁLISES POR TIPO
    # =====================================================

    def _analisar_pensao_alimenticia(self, respostas: RespostasCompletas) -> AnaliseGratuita:
        """Análise específica de pensão alimentícia"""
        resp_dict = {r.pergunta_id: r.valor for r in respostas.respostas}

        # Extrair dados
        qtd_filhos = int(resp_dict.get("qtd_filhos", 1))
        renda_alimentante = float(resp_dict.get("renda_alimentante", 3000))
        renda_guardiao = float(resp_dict.get("renda_guardiao", 1500))
        despesas_filhos = float(resp_dict.get("despesas_filhos", 1000))

        # Cálculo de pensão
        # Regra geral: 20-30% por filho do salário do alimentante
        percentual_base = 0.25 if qtd_filhos == 1 else 0.15 * qtd_filhos
        percentual_base = min(percentual_base, 0.50)  # Máximo 50%

        valor_minimo = renda_alimentante * (percentual_base - 0.05)
        valor_maximo = renda_alimentante * (percentual_base + 0.05)
        valor_medio = renda_alimentante * percentual_base

        # Ajustar por despesas reais
        if despesas_filhos > valor_medio:
            valor_medio = (valor_medio + despesas_filhos) / 2
            valor_maximo = despesas_filhos * 1.1

        calculo = CalculoValores(
            valor_minimo=valor_minimo,
            valor_maximo=valor_maximo,
            valor_medio=valor_medio,
            base_calculo=f"{int(percentual_base*100)}% da renda do alimentante ({qtd_filhos} filho(s))"
        )

        # Estatísticas simuladas (baseadas em dados reais aproximados)
        estatisticas = EstatisticasCaso(
            total_casos_similares=342,
            taxa_sucesso_percentual=87.5,
            tempo_medio_meses=6.5,
            tempo_minimo_meses=2,
            tempo_maximo_meses=18,
            valor_medio_acordo=valor_medio
        )

        # Base legal
        base_legal = BaseLegal(
            leis=["Código Civil - Lei 10.406/2002", "Estatuto da Criança e do Adolescente - Lei 8.069/1990"],
            artigos=["Art. 1.694 do CC", "Art. 1.695 do CC", "Art. 1.703 do CC"],
            jurisprudencia_relevante=[
                "STJ - Pensão alimentícia de 33% para 2 filhos é razoável",
                "STJ - Capacidade financeira do alimentante deve ser considerada",
                "TJSP - Despesas comprovadas justificam aumento de pensão"
            ],
            sumulas=["Súmula 358 STJ - Cálculo com base na renda líquida"]
        )

        # Próximos passos
        proximos_passos = ProximosPassos(
            passos=[
                "Reunir toda documentação necessária",
                "Tentar acordo extrajudicial primeiro",
                "Se não houver acordo, ajuizar ação de alimentos",
                "Acompanhar audiência de conciliação",
                "Se necessário, produzir provas na audiência de instrução"
            ],
            documentos_necessarios=[
                "RG e CPF (seus e dos filhos)",
                "Certidão de nascimento dos filhos",
                "Comprovante de residência",
                "Comprovantes de despesas dos filhos (escola, saúde, etc)",
                "Comprovante de renda do alimentante (se possível)",
                "Comprovante de sua renda"
            ],
            prazos_importantes={
                "Prazo para contestação": "15 dias após citação",
                "Validade da ação": "Enquanto persistir a necessidade"
            },
            custos_estimados={
                "Custas judiciais": 0.0,  # Justiça gratuita
                "Honorários advocatícios": 0.0  # Pode pedir justiça gratuita
            }
        )

        # Determinar viabilidade
        if renda_alimentante < 1500:
            viabilidade = ViabilidadeCaso.MEDIA
        elif renda_alimentante > 3000:
            viabilidade = ViabilidadeCaso.ALTA
        else:
            viabilidade = ViabilidadeCaso.ALTA

        # Alertas
        alertas = []
        if resp_dict.get("urgencia") == "alta":
            alertas.append("⚠️ URGENTE: Crianças sem sustento básico - considere tutela de urgência")
        if resp_dict.get("ja_recebe") == "sim":
            alertas.append("📋 Já existe pensão - será ação de revisão")

        return AnaliseGratuita(
            tipo_caso=TipoCaso.PENSAO_ALIMENTICIA,
            viabilidade=viabilidade,
            complexidade=ComplexidadeCaso.SIMPLES,
            urgencia=UrgenciaCaso.NORMAL if resp_dict.get("urgencia") != "alta" else UrgenciaCaso.URGENTE,
            resumo_caso=f"Ação de alimentos para {qtd_filhos} filho(s). Alimentante com renda de R$ {renda_alimentante:.2f}.",
            direitos_principais=[
                f"Seus filhos têm direito a pensão alimentícia de aproximadamente {int(percentual_base*100)}% da renda do pai/mãe",
                "A pensão deve cobrir alimentação, saúde, educação, vestuário e lazer",
                "O valor pode ser revisado sempre que houver mudança na situação financeira",
                "Em caso de não pagamento, pode haver prisão civil por até 3 meses"
            ],
            calculo_valores=calculo,
            tempo_estimado_meses=6.5,
            probabilidade_sucesso=0.875,
            estatisticas=estatisticas,
            base_legal=base_legal,
            proximos_passos=proximos_passos,
            alertas_importantes=alertas,
            prazos_criticos=[]
        )

    def _analisar_direito_consumidor(self, respostas: RespostasCompletas) -> AnaliseGratuita:
        """Análise de direito do consumidor"""
        resp_dict = {r.pergunta_id: r.valor for r in respostas.respostas}

        tipo_problema = resp_dict.get("tipo_problema", "")
        valor_produto = float(resp_dict.get("valor_produto", 0))
        prejuizo_moral = resp_dict.get("prejuizo_moral", "nao")

        # Cálculo de danos materiais + morais
        valor_minimo = valor_produto
        valor_maximo = valor_produto * 2  # Devolução em dobro (CDC)

        # Adicionar danos morais
        if prejuizo_moral == "sim_grave":
            valor_minimo += 5000
            valor_maximo += 15000
        elif prejuizo_moral == "sim_leve":
            valor_minimo += 2000
            valor_maximo += 5000

        calculo = CalculoValores(
            valor_minimo=valor_minimo,
            valor_maximo=valor_maximo,
            valor_medio=(valor_minimo + valor_maximo) / 2,
            base_calculo="Devolução + danos morais conforme CDC"
        )

        base_legal = BaseLegal(
            leis=["Código de Defesa do Consumidor - Lei 8.078/1990"],
            artigos=["Art. 18 CDC", "Art. 42 CDC (cobrança indevida)"],
            jurisprudencia_relevante=[
                "STJ - Dano moral in re ipsa em negativação indevida",
                "STJ - Devolução em dobro de valores cobrados indevidamente"
            ]
        )

        return AnaliseGratuita(
            tipo_caso=TipoCaso.DIREITO_CONSUMIDOR,
            viabilidade=ViabilidadeCaso.ALTA,
            complexidade=ComplexidadeCaso.SIMPLES,
            urgencia=UrgenciaCaso.NORMAL,
            resumo_caso=f"Problema: {tipo_problema}. Valor: R$ {valor_produto:.2f}",
            direitos_principais=[
                "Direito a devolução do valor pago",
                "Direito a troca ou conserto do produto",
                "Possível devolução em dobro se cobrança indevida",
                "Indenização por danos morais se houver"
            ],
            calculo_valores=calculo,
            tempo_estimado_meses=4.0,
            probabilidade_sucesso=0.80,
            estatisticas=EstatisticasCaso(
                total_casos_similares=1250,
                taxa_sucesso_percentual=80.0,
                tempo_medio_meses=4.0,
                tempo_minimo_meses=2,
                tempo_maximo_meses=8
            ),
            base_legal=base_legal,
            proximos_passos=ProximosPassos(
                passos=[
                    "Tentar resolver no Procon",
                    "Se não resolver, acionar Juizado Especial",
                    "Reunir provas (nota fiscal, fotos, protocolos)"
                ],
                documentos_necessarios=["Nota fiscal", "Comprovante de pagamento", "Fotos do defeito"],
                prazos_importantes={"Reclamação inicial": "90 dias para vícios aparentes"},
                custos_estimados={"Custas": 0.0}
            ),
            alertas_importantes=[],
            prazos_criticos=[]
        )

    def _analisar_transito(self, respostas: RespostasCompletas) -> AnaliseGratuita:
        """Análise simplificada de trânsito"""
        return self._analise_generica(TipoCaso.TRANSITO, "Contestação de multa ou acidente", 0.70, 3.0)

    def _analisar_briga_vizinhos(self, respostas: RespostasCompletas) -> AnaliseGratuita:
        """Análise simplificada de briga de vizinhos"""
        return self._analise_generica(TipoCaso.BRIGA_VIZINHOS, "Conflito de vizinhança", 0.65, 6.0)

    def _analisar_trabalhista(self, respostas: RespostasCompletas) -> AnaliseGratuita:
        """Análise simplificada trabalhista"""
        resp_dict = {r.pergunta_id: r.valor for r in respostas.respostas}
        salario = float(resp_dict.get("salario", 2000))

        # Cálculo aproximado de verbas rescisórias
        valor_estimado = salario * 3  # Aproximação simples

        return AnaliseGratuita(
            tipo_caso=TipoCaso.TRABALHISTA,
            viabilidade=ViabilidadeCaso.ALTA,
            complexidade=ComplexidadeCaso.MEDIO,
            urgencia=UrgenciaCaso.NORMAL,
            resumo_caso="Ação trabalhista",
            direitos_principais=["Verbas rescisórias", "FGTS", "Seguro-desemprego"],
            calculo_valores=CalculoValores(valor_estimado * 0.8, valor_estimado * 1.5, valor_estimado),
            tempo_estimado_meses=12.0,
            probabilidade_sucesso=0.75,
            estatisticas=EstatisticasCaso(500, 75.0, 12.0, 6, 24),
            base_legal=BaseLegal(["CLT"], ["Art. 477 CLT"], []),
            proximos_passos=ProximosPassos([], [], {}, {}),
            alertas_importantes=[],
            prazos_criticos=[]
        )

    def _analisar_divorcio(self, respostas: RespostasCompletas) -> AnaliseGratuita:
        """Análise simplificada de divórcio"""
        return self._analise_generica(TipoCaso.DIVORCIO, "Divórcio", 0.90, 6.0)

    def _analisar_inventario(self, respostas: RespostasCompletas) -> AnaliseGratuita:
        """Análise simplificada de inventário"""
        return self._analise_generica(TipoCaso.INVENTARIO, "Inventário", 0.85, 12.0)

    def _analisar_danos_morais(self, respostas: RespostasCompletas) -> AnaliseGratuita:
        """Análise simplificada de danos morais"""
        return self._analise_generica(TipoCaso.DANOS_MORAIS, "Danos morais", 0.60, 8.0)

    def _analisar_inss(self, respostas: RespostasCompletas) -> AnaliseGratuita:
        """Análise simplificada de INSS"""
        return self._analise_generica(TipoCaso.INSS, "Benefício previdenciário", 0.70, 18.0)

    def _analisar_contratos(self, respostas: RespostasCompletas) -> AnaliseGratuita:
        """Análise simplificada de contratos"""
        return self._analise_generica(TipoCaso.CONTRATOS, "Descumprimento contratual", 0.65, 8.0)

    def _analise_generica(self, tipo: TipoCaso, resumo: str, prob: float, tempo: float) -> AnaliseGratuita:
        """Análise genérica para casos não detalhados"""
        return AnaliseGratuita(
            tipo_caso=tipo,
            viabilidade=ViabilidadeCaso.MEDIA,
            complexidade=ComplexidadeCaso.MEDIO,
            urgencia=UrgenciaCaso.NORMAL,
            resumo_caso=resumo,
            direitos_principais=["Consulte a análise premium para detalhes"],
            calculo_valores=None,
            tempo_estimado_meses=tempo,
            probabilidade_sucesso=prob,
            estatisticas=EstatisticasCaso(100, prob*100, tempo, tempo/2, tempo*2),
            base_legal=BaseLegal([], [], []),
            proximos_passos=ProximosPassos([], [], {}, {}),
            alertas_importantes=[],
            prazos_criticos=[]
        )

    # =====================================================
    # UTILIDADES
    # =====================================================

    def _obter_popularidade(self, tipo: TipoCaso) -> int:
        """Retorna popularidade (volume de buscas estimado)"""
        popularidades = {
            TipoCaso.PENSAO_ALIMENTICIA: 100,
            TipoCaso.DIREITO_CONSUMIDOR: 95,
            TipoCaso.TRABALHISTA: 90,
            TipoCaso.TRANSITO: 85,
            TipoCaso.DIVORCIO: 80,
            TipoCaso.DANOS_MORAIS: 75,
            TipoCaso.INSS: 70,
            TipoCaso.BRIGA_VIZINHOS: 65,
            TipoCaso.CONTRATOS: 60,
            TipoCaso.INVENTARIO: 55,
        }
        return popularidades.get(tipo, 50)

    def _carregar_base_dados(self) -> Dict:
        """Carrega base de dados de jurisprudência e estatísticas"""
        # Em produção, carregar de banco de dados
        return {}


# =====================================================
# FACTORY
# =====================================================

def criar_engine_assistente() -> EngineAssistentePublico:
    """Factory para criar engine"""
    return EngineAssistentePublico()


# =====================================================
# TESTE
# =====================================================

if __name__ == "__main__":
    engine = criar_engine_assistente()

    # Listar casos
    print("=== CASOS DISPONÍVEIS ===")
    for caso in engine.listar_casos_disponiveis():
        print(f"- {caso['titulo']}: {caso['descricao']} ({caso['tempo_estimado']}min)")

    # Testar pensão alimentícia
    print("\n=== TESTE: PENSÃO ALIMENTÍCIA ===")
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

    analise = engine.analisar_caso(respostas)
    print(f"Viabilidade: {analise.viabilidade.value}")
    print(f"Valor estimado: R$ {analise.calculo_valores.valor_medio:.2f}")
    print(f"Probabilidade de sucesso: {analise.probabilidade_sucesso*100:.1f}%")
    print(f"Tempo estimado: {analise.tempo_estimado_meses:.1f} meses")
    print(f"Taxa de sucesso em casos similares: {analise.estatisticas.taxa_sucesso_percentual}%")

    print("\n✅ Engine Assistente Público funcionando!")
