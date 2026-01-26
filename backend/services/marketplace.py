"""
Marketplace de Leads Qualificados
Modelo invertido: Cliente paga R$ 7 → Lead quente para advogado
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import random


class LeadQualificado:
    """
    Representa um lead qualificado (cliente que já pagou relatório)
    """

    def __init__(self, case_id: int, db: Session):
        from models import Case, User, Payment

        self.db = db
        self.case = db.query(Case).filter(Case.id == case_id).first()
        self.user = self.case.user if self.case else None
        self.payment = db.query(Payment).filter(Payment.case_id == case_id).first()

    @property
    def score_qualidade(self) -> int:
        """
        Score de qualidade do lead (0-100)

        Quanto maior, melhor o lead para o advogado
        """
        score = 50  # Base

        # Pagou relatório? +30 pontos
        if self.case.report_paid:
            score += 30

        # Probabilidade alta? +20 pontos
        if self.case.probability and self.case.probability.value == "alta":
            score += 20
        elif self.case.probability and self.case.probability.value == "media":
            score += 10

        # Tem email? +10 pontos
        if self.user and self.user.email:
            score += 10

        # Tem telefone? +10 pontos
        if self.user and self.user.phone:
            score += 10

        # Descrição detalhada? +10 pontos
        if self.case.description and len(self.case.description) > 200:
            score += 10

        # Tem documentos anexados? +10 pontos
        if self.case.checklist and len(self.case.checklist) > 0:
            score += 10

        return min(score, 100)

    @property
    def valor_estimado_honorarios(self) -> float:
        """Estima honorários com base na área e probabilidade"""
        valores_base = {
            "familia": 3000,
            "consumidor": 2000,
            "bancario": 3500,
            "saude": 4000,
            "aereo": 2500
        }

        base = valores_base.get(self.case.area, 2500)

        # Ajustar por probabilidade
        if self.case.probability:
            if self.case.probability.value == "alta":
                base *= 1.3
            elif self.case.probability.value == "baixa":
                base *= 0.7

        return base

    def to_dict(self) -> Dict:
        """Converte lead para dict (para exibição ao advogado)"""
        return {
            "id": self.case.id,
            "area": self.case.area,
            "sub_area": self.case.sub_area,
            "descricao_resumida": self.case.description[:200] + "...",
            "probabilidade": self.case.probability.value if self.case.probability else "media",
            "score_qualidade": self.score_qualidade,
            "valor_estimado": self.valor_estimado_honorarios,
            "cliente": {
                "nome": self.user.name if self.user else "Anônimo",
                "cidade": "São Paulo",  # TODO: extrair da descrição ou adicionar campo
                "tem_email": bool(self.user and self.user.email),
                "tem_telefone": bool(self.user and self.user.phone)
            },
            "criado_em": self.case.created_at.isoformat() if self.case.created_at else None,
            "relatorio_pago": self.case.report_paid
        }


class MarketplaceEngine:
    """Engine do marketplace de leads"""

    def __init__(self, db: Session):
        self.db = db

    def criar_lead_de_caso(self, case_id: int) -> bool:
        """
        Cria lead qualificado a partir de um caso que pagou relatório

        Args:
            case_id: ID do caso

        Returns:
            True se lead criado com sucesso
        """
        from models import Case, Referral

        case = self.db.query(Case).filter(Case.id == case_id).first()

        if not case or not case.report_paid:
            return False

        # Verificar se já existe referral para este caso
        existing = self.db.query(Referral).filter(Referral.case_id == case_id).first()
        if existing:
            return False

        # Encontrar melhor advogado
        advogado = self.encontrar_melhor_advogado(
            area=case.area,
            cidade=None,  # TODO: extrair cidade do caso
            estado="SP"  # TODO: extrair estado
        )

        if not advogado:
            print(f"Nenhum advogado disponível para área {case.area}")
            return False

        # Criar referral
        from models import Referral, ReferralStatus

        referral = Referral(
            case_id=case.id,
            lawyer_id=advogado.id,
            status=ReferralStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(hours=48)  # 48h de exclusividade
        )

        self.db.add(referral)

        # Atualizar contador do advogado
        advogado.total_leads += 1
        advogado.last_lead_at = datetime.utcnow()

        self.db.commit()

        # Enviar notificação ao advogado
        self._notificar_novo_lead(advogado, case)

        print(f"✓ Lead {case.id} atribuído a {advogado.name} (OAB {advogado.oab})")
        return True

    def encontrar_melhor_advogado(
        self,
        area: str,
        cidade: Optional[str] = None,
        estado: Optional[str] = None
    ):
        """
        Encontra melhor advogado usando algoritmo de matching inteligente

        Critérios (em ordem de prioridade):
        1. Plano ativo (Full > Pro > Redação > Pesquisa > Leads)
        2. Área de atuação
        3. Localização (cidade > estado)
        4. Success score (% de aceite)
        5. Tempo desde último lead (rodízio)
        6. Disponibilidade (não atingiu limite do plano)
        """
        from models import Lawyer, Subscription, Plan

        query = self.db.query(Lawyer).join(Subscription).join(Plan).filter(
            and_(
                Lawyer.is_active == True,
                Lawyer.is_verified == True,
                Subscription.status == "active",
                Subscription.expires_at > datetime.utcnow(),
                or_(
                    Plan.feature_leads == True,
                    Plan.feature_priority_leads == True
                )
            )
        )

        # Filtrar por área
        if area:
            query = query.filter(Lawyer.areas.contains([area]))

        # Filtrar por localização
        if estado:
            query = query.filter(Lawyer.states.contains([estado]))

        if cidade:
            query = query.filter(Lawyer.cities.contains([cidade]))

        # Obter candidatos
        candidatos = query.all()

        if not candidatos:
            return None

        # Scoring
        scored_candidatos = []

        for advogado in candidatos:
            score = 0.0

            # 1. Plano (peso 40)
            if advogado.subscription.plan.feature_priority_leads:
                score += 40
            elif advogado.subscription.plan.feature_leads:
                score += 25

            # 2. Success score (peso 25)
            score += (advogado.success_score or 0) * 0.25

            # 3. Rodízio - tempo desde último lead (peso 20)
            if advogado.last_lead_at:
                horas_desde = (datetime.utcnow() - advogado.last_lead_at).total_seconds() / 3600
                score += min(horas_desde / 24 * 20, 20)  # Max 20 pontos se passou 24h+
            else:
                score += 20  # Nunca recebeu lead

            # 4. Disponibilidade de limite (peso 15)
            if advogado.subscription.plan.leads_per_month == 0:  # Ilimitado
                score += 15
            elif advogado.subscription.leads_used < advogado.subscription.plan.leads_per_month:
                score += 15

            # 5. Localização match (peso 10)
            if cidade and cidade in (advogado.cities or []):
                score += 10
            elif estado and estado in (advogado.states or []):
                score += 5

            scored_candidatos.append((advogado, score))

        # Ordenar por score
        scored_candidatos.sort(key=lambda x: x[1], reverse=True)

        # Retornar melhor
        return scored_candidatos[0][0] if scored_candidatos else None

    def _notificar_novo_lead(self, advogado, case):
        """Notifica advogado sobre novo lead"""
        from services.alerts import get_alert_system

        alert = get_alert_system()

        lead = LeadQualificado(case.id, self.db)

        mensagem = f"""
🎯 NOVO LEAD QUALIFICADO!

Dr(a). {advogado.name},

Você recebeu um novo cliente potencial:

📋 Área: {case.area.title()}
🎲 Probabilidade: {case.probability.value.upper() if case.probability else 'MÉDIA'}
💰 Honorários estimados: R$ {lead.valor_estimado_honorarios:,.2f}
⭐ Score de qualidade: {lead.score_qualidade}/100

O cliente JÁ PAGOU pelo relatório jurídico e está aguardando contato!

Você tem 48 horas de exclusividade.

👉 Acesse: doutoraia.com.br/leads

Doutora IA
        """.strip()

        # WhatsApp
        if advogado.phone:
            alert.enviar_whatsapp(advogado.phone, mensagem)

        # Email
        if advogado.email:
            alert.enviar_email(
                advogado.email,
                f"🎯 Novo Lead Qualificado - {case.area.title()}",
                mensagem
            )

    def listar_leads_disponiveis(
        self,
        lawyer_id: int,
        area: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Lista leads disponíveis para um advogado

        Args:
            lawyer_id: ID do advogado
            area: Filtrar por área
            limit: Máximo de resultados

        Returns:
            Lista de leads qualificados
        """
        from models import Case, Referral, ReferralStatus, Lawyer

        # Buscar advogado
        advogado = self.db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()

        if not advogado:
            return []

        # Leads atribuídos a este advogado (pendentes)
        query = self.db.query(Case).join(Referral).filter(
            and_(
                Referral.lawyer_id == lawyer_id,
                Referral.status == ReferralStatus.PENDING,
                Referral.expires_at > datetime.utcnow()
            )
        )

        if area:
            query = query.filter(Case.area == area)

        casos = query.order_by(desc(Case.created_at)).limit(limit).all()

        # Converter para LeadQualificado
        leads = []
        for caso in casos:
            lead = LeadQualificado(caso.id, self.db)
            leads.append(lead.to_dict())

        return leads

    def aceitar_lead(self, lawyer_id: int, case_id: int) -> Dict:
        """
        Advogado aceita um lead

        Args:
            lawyer_id: ID do advogado
            case_id: ID do caso

        Returns:
            Dict com dados de contato do cliente
        """
        from models import Referral, ReferralStatus, Lawyer, Case, User

        # Buscar referral
        referral = self.db.query(Referral).filter(
            and_(
                Referral.case_id == case_id,
                Referral.lawyer_id == lawyer_id,
                Referral.status == ReferralStatus.PENDING
            )
        ).first()

        if not referral:
            return {"erro": "Lead não encontrado ou expirado"}

        # Verificar se ainda está na janela de exclusividade
        if referral.expires_at < datetime.utcnow():
            referral.status = ReferralStatus.EXPIRED
            self.db.commit()
            return {"erro": "Lead expirou"}

        # Aceitar
        referral.status = ReferralStatus.ACCEPTED
        referral.responded_at = datetime.utcnow()

        # Atualizar métricas do advogado
        advogado = referral.lawyer
        advogado.accepted_leads += 1

        # Recalcular success score
        if advogado.total_leads > 0:
            advogado.success_score = (advogado.accepted_leads / advogado.total_leads) * 100

        self.db.commit()

        # Retornar dados de contato do cliente
        case = referral.case
        user = case.user

        return {
            "sucesso": True,
            "cliente": {
                "nome": user.name if user else "Cliente",
                "email": user.email if user else None,
                "telefone": user.phone if user else None,
                "cpf": user.cpf if user else None
            },
            "caso": {
                "id": case.id,
                "descricao": case.description,
                "area": case.area,
                "probabilidade": case.probability.value if case.probability else "media",
                "relatorio_url": case.report_url
            },
            "mensagem": "Lead aceito! Entre em contato com o cliente nas próximas 24h."
        }

    def rejeitar_lead(self, lawyer_id: int, case_id: int, motivo: str = "") -> bool:
        """
        Advogado rejeita um lead

        Args:
            lawyer_id: ID do advogado
            case_id: ID do caso
            motivo: Motivo da rejeição

        Returns:
            True se rejeitado com sucesso
        """
        from models import Referral, ReferralStatus

        referral = self.db.query(Referral).filter(
            and_(
                Referral.case_id == case_id,
                Referral.lawyer_id == lawyer_id,
                Referral.status == ReferralStatus.PENDING
            )
        ).first()

        if not referral:
            return False

        # Rejeitar
        referral.status = ReferralStatus.REJECTED
        referral.responded_at = datetime.utcnow()
        referral.response_message = motivo

        # Atualizar métricas
        advogado = referral.lawyer
        advogado.rejected_leads += 1

        # Recalcular success score
        if advogado.total_leads > 0:
            advogado.success_score = (advogado.accepted_leads / advogado.total_leads) * 100

        self.db.commit()

        # Reatribuir lead a outro advogado
        self.criar_lead_de_caso(case_id)

        return True

    def estatisticas_marketplace(self) -> Dict:
        """Estatísticas gerais do marketplace"""
        from models import Case, Referral, ReferralStatus

        total_leads = self.db.query(Case).filter(Case.report_paid == True).count()

        total_atribuidos = self.db.query(Referral).count()

        aceitos = self.db.query(Referral).filter(
            Referral.status == ReferralStatus.ACCEPTED
        ).count()

        rejeitados = self.db.query(Referral).filter(
            Referral.status == ReferralStatus.REJECTED
        ).count()

        pendentes = self.db.query(Referral).filter(
            Referral.status == ReferralStatus.PENDING,
            Referral.expires_at > datetime.utcnow()
        ).count()

        taxa_conversao = (aceitos / total_atribuidos * 100) if total_atribuidos > 0 else 0

        return {
            "total_leads_qualificados": total_leads,
            "total_atribuidos": total_atribuidos,
            "aceitos": aceitos,
            "rejeitados": rejeitados,
            "pendentes": pendentes,
            "taxa_conversao": round(taxa_conversao, 2),
            "valor_medio_honorarios": 3500  # TODO: calcular real
        }


# Singleton
_marketplace = None


def get_marketplace(db: Session) -> MarketplaceEngine:
    global _marketplace
    if _marketplace is None or _marketplace.db != db:
        _marketplace = MarketplaceEngine(db)
    return _marketplace
