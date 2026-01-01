"""
Engine Marketplace de Advogados - Doutora IA
Conecta cidadãos com advogados parceiros

Modelo de negócio:
- Cliente: paga R$ 7,00 pelo parecer
- Advogado: assina plano mensal para receber leads qualificados

Planos para Advogados:
1. Básico (R$ 197/mês): Recebe leads básicos (nome, contato, tipo de caso)
2. Profissional (R$ 397/mês): Leads + respostas do quiz completo
3. Premium (R$ 597/mês): Leads + quiz + parecer completo gerado

Versão: 1.0.0
Data: 31/12/2025
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime, timedelta
import hashlib


# =====================================================
# ENUMS
# =====================================================

class PlanoAdvogado(Enum):
    """Planos disponíveis para advogados"""
    BASICO = "basico"  # R$ 197/mês
    PROFISSIONAL = "profissional"  # R$ 397/mês
    PREMIUM = "premium"  # R$ 597/mês


class StatusAdvogado(Enum):
    """Status do advogado no marketplace"""
    PENDENTE = "pendente"  # Cadastro aguardando aprovação
    ATIVO = "ativo"  # Ativo e recebendo leads
    SUSPENSO = "suspenso"  # Temporariamente suspenso
    INATIVO = "inativo"  # Cancelou plano


class StatusLead(Enum):
    """Status do lead"""
    NOVO = "novo"  # Recém gerado
    ENVIADO = "enviado"  # Enviado para advogado(s)
    VISUALIZADO = "visualizado"  # Advogado visualizou
    CONTATADO = "contatado"  # Advogado contatou cliente
    CONVERTIDO = "convertido"  # Cliente contratou advogado
    PERDIDO = "perdido"  # Cliente não contratou


class EspecialidadeAdvogado(Enum):
    """Áreas de atuação"""
    FAMILIA = "familia"
    CONSUMIDOR = "consumidor"
    TRABALHISTA = "trabalhista"
    CIVIL = "civil"
    PREVIDENCIARIO = "previdenciario"
    CRIMINAL = "criminal"
    TRANSITO = "transito"
    TODAS = "todas"


# =====================================================
# DATACLASSES - ADVOGADO
# =====================================================

@dataclass
class EnderecoAdvogado:
    """Endereço do escritório"""
    logradouro: str
    numero: str
    complemento: Optional[str]
    bairro: str
    cidade: str
    estado: str
    cep: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class AvaliacaoAdvogado:
    """Avaliação feita por cliente"""
    cliente_id: str
    lead_id: str
    nota: float  # 0-5 estrelas
    comentario: Optional[str]
    data: str
    respondido: bool = False
    resposta: Optional[str] = None


@dataclass
class EstatisticasAdvogado:
    """Estatísticas de desempenho"""
    total_leads_recebidos: int = 0
    total_leads_visualizados: int = 0
    total_leads_contatados: int = 0
    total_leads_convertidos: int = 0
    taxa_conversao: float = 0.0
    tempo_medio_resposta_horas: float = 0.0
    nota_media: float = 0.0
    total_avaliacoes: int = 0


@dataclass
class Advogado:
    """Advogado parceiro"""
    id: str
    oab_numero: str
    oab_estado: str
    nome_completo: str
    email: str
    telefone: str
    especialidades: List[EspecialidadeAdvogado]

    # Plano e status
    plano_atual: PlanoAdvogado
    status: StatusAdvogado
    data_cadastro: str
    data_ativacao: Optional[str] = None

    # Localização
    endereco: EnderecoAdvogado = None

    # Perfil público
    foto_url: Optional[str] = None
    biografia: Optional[str] = None
    areas_atuacao: List[str] = field(default_factory=list)
    idiomas: List[str] = field(default_factory=lambda: ["Português"])
    site: Optional[str] = None

    # Avaliações
    avaliacoes: List[AvaliacaoAdvogado] = field(default_factory=list)
    estatisticas: EstatisticasAdvogado = field(default_factory=EstatisticasAdvogado)

    # Configurações
    receber_leads_automatico: bool = True
    raio_atendimento_km: int = 50
    horario_atendimento: Dict[str, str] = field(default_factory=dict)

    # Financeiro
    ultimo_pagamento: Optional[str] = None
    proximo_pagamento: Optional[str] = None


# =====================================================
# DATACLASSES - LEAD
# =====================================================

@dataclass
class DadosCliente:
    """Dados do cliente (lead)"""
    nome: str
    email: str
    telefone: str
    cidade: str
    estado: str


@dataclass
class Lead:
    """Lead qualificado"""
    # Campos obrigatórios (sem default)
    id: str
    tipo_caso: str
    urgencia: str
    viabilidade: str
    cliente: DadosCliente
    resumo_caso: str
    data_criacao: str

    # Campos opcionais (com default)
    respostas_quiz: Optional[Dict] = None  # Plano Profissional+
    parecer_completo: Optional[str] = None  # Plano Premium
    status: StatusLead = StatusLead.NOVO
    advogados_enviados: List[str] = field(default_factory=list)
    advogado_convertido: Optional[str] = None
    data_visualizacao: Optional[str] = None
    data_contato: Optional[str] = None
    data_conversao: Optional[str] = None


@dataclass
class MatchAdvogadoLead:
    """Match entre advogado e lead"""
    advogado_id: str
    lead_id: str
    score: float  # 0-1, baseado em proximidade, especialidade, etc
    distancia_km: Optional[float] = None
    data_envio: str = field(default_factory=lambda: datetime.now().isoformat())


# =====================================================
# ENGINE MARKETPLACE
# =====================================================

class EngineMarketplaceAdvogados:
    """Engine de marketplace de advogados"""

    def __init__(self):
        self._advogados: Dict[str, Advogado] = {}
        self._leads: Dict[str, Lead] = {}
        self._matches: List[MatchAdvogadoLead] = []
        self._contador_adv = 1000
        self._contador_lead = 5000

        # Carregar advogados demo
        self._carregar_advogados_demo()

    # =====================================================
    # GESTÃO DE ADVOGADOS
    # =====================================================

    def cadastrar_advogado(
        self,
        oab_numero: str,
        oab_estado: str,
        nome_completo: str,
        email: str,
        telefone: str,
        especialidades: List[EspecialidadeAdvogado],
        endereco: EnderecoAdvogado,
        plano: PlanoAdvogado
    ) -> Advogado:
        """Cadastra novo advogado parceiro"""

        self._contador_adv += 1
        adv_id = f"ADV-{self._contador_adv:05d}"

        advogado = Advogado(
            id=adv_id,
            oab_numero=oab_numero,
            oab_estado=oab_estado,
            nome_completo=nome_completo,
            email=email,
            telefone=telefone,
            especialidades=especialidades,
            plano_atual=plano,
            status=StatusAdvogado.PENDENTE,
            data_cadastro=datetime.now().isoformat(),
            endereco=endereco
        )

        self._advogados[adv_id] = advogado
        return advogado

    def aprovar_advogado(self, advogado_id: str) -> bool:
        """Aprova advogado e ativa conta"""
        if advogado_id not in self._advogados:
            return False

        adv = self._advogados[advogado_id]
        adv.status = StatusAdvogado.ATIVO
        adv.data_ativacao = datetime.now().isoformat()
        adv.proximo_pagamento = (datetime.now() + timedelta(days=30)).isoformat()

        return True

    def atualizar_plano_advogado(self, advogado_id: str, novo_plano: PlanoAdvogado) -> bool:
        """Atualiza plano do advogado"""
        if advogado_id not in self._advogados:
            return False

        self._advogados[advogado_id].plano_atual = novo_plano
        return True

    def listar_advogados(
        self,
        estado: Optional[str] = None,
        especialidade: Optional[EspecialidadeAdvogado] = None,
        plano: Optional[PlanoAdvogado] = None,
        status: Optional[StatusAdvogado] = None
    ) -> List[Advogado]:
        """Lista advogados com filtros"""

        advogados = list(self._advogados.values())

        if estado:
            advogados = [a for a in advogados if a.endereco and a.endereco.estado == estado]

        if especialidade:
            advogados = [a for a in advogados if especialidade in a.especialidades]

        if plano:
            advogados = [a for a in advogados if a.plano_atual == plano]

        if status:
            advogados = [a for a in advogados if a.status == status]

        return advogados

    def buscar_advogados_por_localizacao(
        self,
        cidade: str,
        estado: str,
        especialidade: Optional[EspecialidadeAdvogado] = None,
        limite: int = 3
    ) -> List[Dict[str, Any]]:
        """Busca advogados por localização"""

        candidatos = []

        for adv in self._advogados.values():
            if adv.status != StatusAdvogado.ATIVO:
                continue

            if not adv.receber_leads_automatico:
                continue

            # Filtro de especialidade
            if especialidade and especialidade not in adv.especialidades:
                if EspecialidadeAdvogado.TODAS not in adv.especialidades:
                    continue

            # Filtro de localização
            if adv.endereco:
                # Mesma cidade = prioridade alta
                if adv.endereco.cidade.lower() == cidade.lower() and adv.endereco.estado == estado:
                    score = 1.0
                # Mesmo estado = prioridade média
                elif adv.endereco.estado == estado:
                    score = 0.7
                # Outros = prioridade baixa
                else:
                    score = 0.3
            else:
                score = 0.5

            # Ajustar score por avaliações
            if adv.estatisticas.nota_media > 0:
                score *= (adv.estatisticas.nota_media / 5.0)

            # Ajustar score por taxa de conversão
            if adv.estatisticas.taxa_conversao > 0:
                score *= (1 + adv.estatisticas.taxa_conversao)

            candidatos.append({
                "advogado": adv,
                "score": score,
                "distancia_estimada": 0 if adv.endereco and adv.endereco.cidade.lower() == cidade.lower() else 50
            })

        # Ordenar por score
        candidatos.sort(key=lambda x: x['score'], reverse=True)

        return candidatos[:limite]

    # =====================================================
    # GESTÃO DE LEADS
    # =====================================================

    def criar_lead(
        self,
        tipo_caso: str,
        urgencia: str,
        viabilidade: str,
        cliente: DadosCliente,
        resumo_caso: str,
        respostas_quiz: Optional[Dict] = None,
        parecer_completo: Optional[str] = None
    ) -> Lead:
        """Cria novo lead"""

        self._contador_lead += 1
        lead_id = f"LEAD-{datetime.now().strftime('%Y%m%d')}-{self._contador_lead:05d}"

        lead = Lead(
            id=lead_id,
            tipo_caso=tipo_caso,
            urgencia=urgencia,
            viabilidade=viabilidade,
            cliente=cliente,
            resumo_caso=resumo_caso,
            respostas_quiz=respostas_quiz,
            parecer_completo=parecer_completo,
            data_criacao=datetime.now().isoformat()
        )

        self._leads[lead_id] = lead
        return lead

    def distribuir_lead(
        self,
        lead_id: str,
        especialidade: Optional[EspecialidadeAdvogado] = None
    ) -> List[MatchAdvogadoLead]:
        """Distribui lead para advogados adequados"""

        if lead_id not in self._leads:
            return []

        lead = self._leads[lead_id]

        # Buscar advogados por localização
        candidatos = self.buscar_advogados_por_localizacao(
            cidade=lead.cliente.cidade,
            estado=lead.cliente.estado,
            especialidade=especialidade,
            limite=3
        )

        matches = []

        for cand in candidatos:
            adv = cand['advogado']

            # Criar match
            match = MatchAdvogadoLead(
                advogado_id=adv.id,
                lead_id=lead_id,
                score=cand['score'],
                distancia_km=cand['distancia_estimada']
            )

            self._matches.append(match)
            lead.advogados_enviados.append(adv.id)

            # Atualizar estatísticas do advogado
            adv.estatisticas.total_leads_recebidos += 1

            matches.append(match)

        if matches:
            lead.status = StatusLead.ENVIADO

        return matches

    def obter_lead_para_advogado(self, advogado_id: str, lead_id: str) -> Optional[Dict]:
        """Retorna lead formatado conforme plano do advogado"""

        if advogado_id not in self._advogados or lead_id not in self._leads:
            return None

        adv = self._advogados[advogado_id]
        lead = self._leads[lead_id]

        # Verificar se lead foi enviado para este advogado
        if advogado_id not in lead.advogados_enviados:
            return None

        # Marcar como visualizado
        if lead.status == StatusLead.ENVIADO:
            lead.status = StatusLead.VISUALIZADO
            lead.data_visualizacao = datetime.now().isoformat()
            adv.estatisticas.total_leads_visualizados += 1

        # Montar dados conforme plano
        dados_lead = {
            "id": lead.id,
            "tipo_caso": lead.tipo_caso,
            "urgencia": lead.urgencia,
            "viabilidade": lead.viabilidade,
            "resumo": lead.resumo_caso,
            "cliente": {
                "nome": lead.cliente.nome,
                "telefone": lead.cliente.telefone,
                "email": lead.cliente.email,
                "localizacao": f"{lead.cliente.cidade}/{lead.cliente.estado}"
            },
            "data_criacao": lead.data_criacao
        }

        # Plano Profissional: adiciona respostas do quiz
        if adv.plano_atual in [PlanoAdvogado.PROFISSIONAL, PlanoAdvogado.PREMIUM]:
            dados_lead["respostas_quiz"] = lead.respostas_quiz

        # Plano Premium: adiciona parecer completo
        if adv.plano_atual == PlanoAdvogado.PREMIUM:
            dados_lead["parecer_completo"] = lead.parecer_completo

        return dados_lead

    def marcar_lead_contatado(self, advogado_id: str, lead_id: str) -> bool:
        """Marca que advogado contatou o cliente"""

        if lead_id not in self._leads or advogado_id not in self._advogados:
            return False

        lead = self._leads[lead_id]
        adv = self._advogados[advogado_id]

        if advogado_id not in lead.advogados_enviados:
            return False

        lead.status = StatusLead.CONTATADO
        lead.data_contato = datetime.now().isoformat()
        adv.estatisticas.total_leads_contatados += 1

        return True

    def marcar_lead_convertido(self, advogado_id: str, lead_id: str) -> bool:
        """Marca que cliente contratou o advogado"""

        if lead_id not in self._leads or advogado_id not in self._advogados:
            return False

        lead = self._leads[lead_id]
        adv = self._advogados[advogado_id]

        lead.status = StatusLead.CONVERTIDO
        lead.data_conversao = datetime.now().isoformat()
        lead.advogado_convertido = advogado_id

        adv.estatisticas.total_leads_convertidos += 1
        adv.estatisticas.taxa_conversao = (
            adv.estatisticas.total_leads_convertidos / adv.estatisticas.total_leads_recebidos
        ) if adv.estatisticas.total_leads_recebidos > 0 else 0.0

        return True

    # =====================================================
    # AVALIAÇÕES
    # =====================================================

    def avaliar_advogado(
        self,
        advogado_id: str,
        cliente_id: str,
        lead_id: str,
        nota: float,
        comentario: Optional[str] = None
    ) -> bool:
        """Cliente avalia advogado"""

        if advogado_id not in self._advogados:
            return False

        adv = self._advogados[advogado_id]

        avaliacao = AvaliacaoAdvogado(
            cliente_id=cliente_id,
            lead_id=lead_id,
            nota=min(5.0, max(0.0, nota)),
            comentario=comentario,
            data=datetime.now().isoformat()
        )

        adv.avaliacoes.append(avaliacao)

        # Recalcular nota média
        total_notas = sum(av.nota for av in adv.avaliacoes)
        adv.estatisticas.total_avaliacoes = len(adv.avaliacoes)
        adv.estatisticas.nota_media = total_notas / adv.estatisticas.total_avaliacoes

        return True

    # =====================================================
    # DASHBOARD ADVOGADO
    # =====================================================

    def obter_dashboard_advogado(self, advogado_id: str) -> Optional[Dict]:
        """Dashboard para advogado"""

        if advogado_id not in self._advogados:
            return None

        adv = self._advogados[advogado_id]

        # Leads recentes
        leads_recentes = [
            {
                "id": m.lead_id,
                "data": m.data_envio,
                "tipo": self._leads[m.lead_id].tipo_caso if m.lead_id in self._leads else "N/A",
                "status": self._leads[m.lead_id].status.value if m.lead_id in self._leads else "N/A"
            }
            for m in self._matches if m.advogado_id == advogado_id
        ][-10:]  # Últimos 10

        return {
            "advogado": {
                "nome": adv.nome_completo,
                "oab": f"{adv.oab_numero}/{adv.oab_estado}",
                "plano": adv.plano_atual.value,
                "status": adv.status.value
            },
            "estatisticas": {
                "leads_recebidos": adv.estatisticas.total_leads_recebidos,
                "leads_contatados": adv.estatisticas.total_leads_contatados,
                "leads_convertidos": adv.estatisticas.total_leads_convertidos,
                "taxa_conversao": f"{adv.estatisticas.taxa_conversao*100:.1f}%",
                "nota_media": f"{adv.estatisticas.nota_media:.1f}/5.0",
                "total_avaliacoes": adv.estatisticas.total_avaliacoes
            },
            "leads_recentes": leads_recentes,
            "financeiro": {
                "plano_valor": self._obter_valor_plano(adv.plano_atual),
                "proximo_pagamento": adv.proximo_pagamento
            }
        }

    # =====================================================
    # UTILIDADES
    # =====================================================

    def _obter_valor_plano(self, plano: PlanoAdvogado) -> float:
        """Retorna valor do plano"""
        valores = {
            PlanoAdvogado.BASICO: 197.00,
            PlanoAdvogado.PROFISSIONAL: 397.00,
            PlanoAdvogado.PREMIUM: 597.00
        }
        return valores.get(plano, 0.0)

    def _carregar_advogados_demo(self):
        """Carrega advogados de demonstração"""

        # Advogado 1 - SP, Família
        adv1 = self.cadastrar_advogado(
            oab_numero="123456",
            oab_estado="SP",
            nome_completo="Dr. João Silva",
            email="joao.silva@adv.com",
            telefone="(11) 98765-4321",
            especialidades=[EspecialidadeAdvogado.FAMILIA, EspecialidadeAdvogado.CIVIL],
            endereco=EnderecoAdvogado(
                logradouro="Av. Paulista",
                numero="1000",
                complemento="Sala 500",
                bairro="Bela Vista",
                cidade="São Paulo",
                estado="SP",
                cep="01310-100"
            ),
            plano=PlanoAdvogado.PREMIUM
        )
        self.aprovar_advogado(adv1.id)
        adv1.biografia = "Especialista em Direito de Família com 15 anos de experiência"
        adv1.estatisticas.nota_media = 4.8
        adv1.estatisticas.total_avaliacoes = 45

        # Advogado 2 - SP, Consumidor
        adv2 = self.cadastrar_advogado(
            oab_numero="654321",
            oab_estado="SP",
            nome_completo="Dra. Maria Santos",
            email="maria.santos@adv.com",
            telefone="(11) 91234-5678",
            especialidades=[EspecialidadeAdvogado.CONSUMIDOR, EspecialidadeAdvogado.CIVIL],
            endereco=EnderecoAdvogado(
                logradouro="Rua da Consolação",
                numero="2000",
                complemento=None,
                bairro="Consolação",
                cidade="São Paulo",
                estado="SP",
                cep="01302-000"
            ),
            plano=PlanoAdvogado.PROFISSIONAL
        )
        self.aprovar_advogado(adv2.id)
        adv2.biografia = "Advogada especializada em Direito do Consumidor"
        adv2.estatisticas.nota_media = 4.9
        adv2.estatisticas.total_avaliacoes = 32

        # Advogado 3 - RJ, Trabalhista
        adv3 = self.cadastrar_advogado(
            oab_numero="789012",
            oab_estado="RJ",
            nome_completo="Dr. Carlos Oliveira",
            email="carlos.oliveira@adv.com",
            telefone="(21) 99876-5432",
            especialidades=[EspecialidadeAdvogado.TRABALHISTA],
            endereco=EnderecoAdvogado(
                logradouro="Av. Rio Branco",
                numero="100",
                complemento="Sala 1200",
                bairro="Centro",
                cidade="Rio de Janeiro",
                estado="RJ",
                cep="20040-001"
            ),
            plano=PlanoAdvogado.BASICO
        )
        self.aprovar_advogado(adv3.id)
        adv3.biografia = "Especialista em causas trabalhistas"
        adv3.estatisticas.nota_media = 4.6
        adv3.estatisticas.total_avaliacoes = 28


# =====================================================
# FACTORY
# =====================================================

def criar_engine_marketplace() -> EngineMarketplaceAdvogados:
    """Factory para criar engine de marketplace"""
    return EngineMarketplaceAdvogados()


# =====================================================
# TESTE
# =====================================================

if __name__ == "__main__":
    engine = criar_engine_marketplace()

    print("=== MARKETPLACE DE ADVOGADOS ===")

    # Listar advogados ativos
    advogados = engine.listar_advogados(status=StatusAdvogado.ATIVO)
    print(f"\n{len(advogados)} advogados ativos:")
    for adv in advogados:
        print(f"- {adv.nome_completo} ({adv.oab_numero}/{adv.oab_estado})")
        print(f"  Plano: {adv.plano_atual.value} | Nota: {adv.estatisticas.nota_media:.1f}/5.0")
        print(f"  Cidade: {adv.endereco.cidade if adv.endereco else 'N/A'}")

    # Criar lead de teste
    print("\n=== CRIANDO LEAD ===")
    lead = engine.criar_lead(
        tipo_caso="pensao_alimenticia",
        urgencia="normal",
        viabilidade="alta",
        cliente=DadosCliente(
            nome="Ana Silva",
            email="ana@email.com",
            telefone="(11) 98888-7777",
            cidade="São Paulo",
            estado="SP"
        ),
        resumo_caso="Mãe de 2 filhos buscando pensão alimentícia",
        respostas_quiz={"qtd_filhos": 2, "renda_alimentante": 5000},
        parecer_completo="Parecer completo aqui..."
    )

    print(f"Lead criado: {lead.id}")

    # Distribuir lead
    print("\n=== DISTRIBUINDO LEAD ===")
    matches = engine.distribuir_lead(lead.id, EspecialidadeAdvogado.FAMILIA)

    print(f"{len(matches)} advogados receberam o lead:")
    for match in matches:
        adv = engine._advogados[match.advogado_id]
        print(f"- {adv.nome_completo} (score: {match.score:.2f})")

    # Simular advogado acessando lead
    if matches:
        primeiro_adv = matches[0].advogado_id
        print(f"\n=== ADVOGADO {primeiro_adv} VISUALIZANDO LEAD ===")
        dados_lead = engine.obter_lead_para_advogado(primeiro_adv, lead.id)
        print(f"Cliente: {dados_lead['cliente']['nome']}")
        print(f"Tipo: {dados_lead['tipo_caso']}")
        print(f"Tem quiz: {'Sim' if dados_lead.get('respostas_quiz') else 'Não'}")
        print(f"Tem parecer: {'Sim' if dados_lead.get('parecer_completo') else 'Não'}")

        # Simular conversão
        engine.marcar_lead_contatado(primeiro_adv, lead.id)
        engine.marcar_lead_convertido(primeiro_adv, lead.id)

        # Avaliar advogado
        engine.avaliar_advogado(primeiro_adv, "CLI-001", lead.id, 5.0, "Excelente profissional!")

        # Dashboard
        print(f"\n=== DASHBOARD ADVOGADO ===")
        dashboard = engine.obter_dashboard_advogado(primeiro_adv)
        print(f"Taxa de conversão: {dashboard['estatisticas']['taxa_conversao']}")
        print(f"Nota média: {dashboard['estatisticas']['nota_media']}")

    print("\n✅ Engine Marketplace funcionando!")
