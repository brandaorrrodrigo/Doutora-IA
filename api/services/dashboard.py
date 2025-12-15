"""
Serviço de Dashboard para Advogados
Métricas, estatísticas e KPIs em tempo real
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_


class DashboardService:
    """Serviço de métricas e dashboard para advogados"""

    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # MÉTRICAS PRINCIPAIS
    # ==========================================

    def get_overview(self, lawyer_id: int) -> Dict[str, Any]:
        """
        Visão geral do dashboard (números principais)

        Returns:
            {
                "leads_pendentes": 5,
                "leads_aceitos_mes": 12,
                "taxa_conversao": 75.5,
                "valor_estimado_mes": 45000.00,
                "prazos_proximos": 3,
                "agendamentos_hoje": 2,
                "notificacoes_nao_lidas": 7,
                "avaliacao_media": 4.8,
                "total_avaliacoes": 23
            }
        """
        from models import Referral, Case, ReferralStatus

        # Leads pendentes (não expirados)
        leads_pendentes = self.db.query(Referral).filter(
            Referral.lawyer_id == lawyer_id,
            Referral.status == ReferralStatus.PENDING,
            Referral.expires_at > datetime.utcnow()
        ).count()

        # Leads aceitos este mês
        inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        leads_aceitos_mes = self.db.query(Referral).filter(
            Referral.lawyer_id == lawyer_id,
            Referral.status == ReferralStatus.ACCEPTED,
            Referral.accepted_at >= inicio_mes
        ).count()

        # Leads rejeitados este mês
        leads_rejeitados_mes = self.db.query(Referral).filter(
            Referral.lawyer_id == lawyer_id,
            Referral.status == ReferralStatus.REJECTED,
            Referral.rejected_at >= inicio_mes
        ).count()

        # Taxa de conversão
        total_respondidos = leads_aceitos_mes + leads_rejeitados_mes
        taxa_conversao = (leads_aceitos_mes / total_respondidos * 100) if total_respondidos > 0 else 0

        # Valor estimado (soma dos leads aceitos)
        valor_estimado = self.db.query(
            func.sum(Case.estimated_fees)
        ).join(
            Referral, Case.id == Referral.case_id
        ).filter(
            Referral.lawyer_id == lawyer_id,
            Referral.status == ReferralStatus.ACCEPTED,
            Referral.accepted_at >= inicio_mes,
            Case.estimated_fees.isnot(None)
        ).scalar() or 0

        # Prazos próximos (5 dias)
        try:
            from models import Prazo
            prazos_proximos = self.db.query(Prazo).filter(
                Prazo.lawyer_id == lawyer_id,
                Prazo.data_limite <= datetime.utcnow().date() + timedelta(days=5),
                Prazo.cumprido == False
            ).count()
        except:
            prazos_proximos = 0

        # Agendamentos hoje
        try:
            from models import Agendamento
            agendamentos_hoje = self.db.query(Agendamento).filter(
                Agendamento.lawyer_id == lawyer_id,
                func.date(Agendamento.data_hora) == datetime.utcnow().date(),
                Agendamento.status.in_(['pendente', 'confirmado'])
            ).count()
        except:
            agendamentos_hoje = 0

        # Notificações não lidas
        try:
            from models import Notificacao
            notificacoes_nao_lidas = self.db.query(Notificacao).filter(
                Notificacao.lawyer_id == lawyer_id,
                Notificacao.lida == False
            ).count()
        except:
            notificacoes_nao_lidas = 0

        # Avaliações
        from models import Lawyer
        lawyer = self.db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
        avaliacao_media = float(lawyer.rating) if lawyer and lawyer.rating else 0.0
        total_avaliacoes = lawyer.total_ratings if lawyer else 0

        return {
            "leads_pendentes": leads_pendentes,
            "leads_aceitos_mes": leads_aceitos_mes,
            "leads_rejeitados_mes": leads_rejeitados_mes,
            "taxa_conversao": round(taxa_conversao, 1),
            "valor_estimado_mes": float(valor_estimado),
            "prazos_proximos": prazos_proximos,
            "agendamentos_hoje": agendamentos_hoje,
            "notificacoes_nao_lidas": notificacoes_nao_lidas,
            "avaliacao_media": round(avaliacao_media, 1),
            "total_avaliacoes": total_avaliacoes
        }

    # ==========================================
    # HISTÓRICO DE LEADS
    # ==========================================

    def get_leads_history(
        self,
        lawyer_id: int,
        days: int = 30,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Histórico de leads com filtros

        Args:
            lawyer_id: ID do advogado
            days: Últimos N dias
            status: Filtrar por status (pending, accepted, rejected)

        Returns:
            Lista de leads com detalhes
        """
        from models import Referral, Case, ReferralStatus

        query = self.db.query(Referral, Case).join(
            Case, Referral.case_id == Case.id
        ).filter(
            Referral.lawyer_id == lawyer_id,
            Referral.sent_at >= datetime.utcnow() - timedelta(days=days)
        )

        if status:
            query = query.filter(Referral.status == status)

        results = query.order_by(desc(Referral.sent_at)).all()

        leads = []
        for referral, case in results:
            leads.append({
                "id": referral.id,
                "case_id": case.id,
                "area": case.area,
                "sub_area": case.sub_area,
                "description": case.description[:200] + "..." if len(case.description) > 200 else case.description,
                "probability": case.probability,
                "estimated_fees": float(case.estimated_fees) if case.estimated_fees else 0,
                "status": referral.status,
                "sent_at": referral.sent_at.isoformat() if referral.sent_at else None,
                "expires_at": referral.expires_at.isoformat() if referral.expires_at else None,
                "accepted_at": referral.accepted_at.isoformat() if referral.accepted_at else None,
                "rejected_at": referral.rejected_at.isoformat() if referral.rejected_at else None,
                "rejection_reason": referral.rejection_reason
            })

        return leads

    # ==========================================
    # GRÁFICOS E ESTATÍSTICAS
    # ==========================================

    def get_leads_by_day(self, lawyer_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """
        Leads recebidos por dia (para gráfico)

        Returns:
            [
                {"data": "2024-12-01", "total": 5, "aceitos": 3, "rejeitados": 2},
                ...
            ]
        """
        from models import Referral, ReferralStatus

        data_inicio = datetime.utcnow() - timedelta(days=days)

        # Query agrupada por data
        results = self.db.query(
            func.date(Referral.sent_at).label('data'),
            func.count(Referral.id).label('total'),
            func.sum(
                func.cast(Referral.status == ReferralStatus.ACCEPTED, type_=func.Integer())
            ).label('aceitos'),
            func.sum(
                func.cast(Referral.status == ReferralStatus.REJECTED, type_=func.Integer())
            ).label('rejeitados')
        ).filter(
            Referral.lawyer_id == lawyer_id,
            Referral.sent_at >= data_inicio
        ).group_by(
            func.date(Referral.sent_at)
        ).order_by(
            func.date(Referral.sent_at)
        ).all()

        # Preencher dias sem dados
        dados = {}
        current_date = data_inicio.date()
        end_date = datetime.utcnow().date()

        while current_date <= end_date:
            dados[current_date] = {"data": current_date.isoformat(), "total": 0, "aceitos": 0, "rejeitados": 0}
            current_date += timedelta(days=1)

        # Preencher com dados reais
        for row in results:
            if row.data in dados:
                dados[row.data] = {
                    "data": row.data.isoformat(),
                    "total": row.total or 0,
                    "aceitos": row.aceitos or 0,
                    "rejeitados": row.rejeitados or 0
                }

        return list(dados.values())

    def get_leads_by_area(self, lawyer_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """
        Distribuição de leads por área jurídica

        Returns:
            [
                {"area": "familia", "total": 15, "percentual": 45.5},
                {"area": "consumidor", "total": 10, "percentual": 30.3},
                ...
            ]
        """
        from models import Referral, Case

        data_inicio = datetime.utcnow() - timedelta(days=days)

        results = self.db.query(
            Case.area,
            func.count(Referral.id).label('total')
        ).join(
            Case, Referral.case_id == Case.id
        ).filter(
            Referral.lawyer_id == lawyer_id,
            Referral.sent_at >= data_inicio
        ).group_by(
            Case.area
        ).order_by(
            desc('total')
        ).all()

        total_geral = sum(r.total for r in results)

        areas = []
        for row in results:
            areas.append({
                "area": row.area,
                "total": row.total,
                "percentual": round((row.total / total_geral * 100), 1) if total_geral > 0 else 0
            })

        return areas

    def get_conversion_funnel(self, lawyer_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Funil de conversão

        Returns:
            {
                "recebidos": 100,
                "visualizados": 85,
                "aceitos": 60,
                "convertidos": 45  # Cliente fechou contrato
            }
        """
        from models import Referral, ReferralStatus

        data_inicio = datetime.utcnow() - timedelta(days=days)

        # Leads recebidos
        recebidos = self.db.query(Referral).filter(
            Referral.lawyer_id == lawyer_id,
            Referral.sent_at >= data_inicio
        ).count()

        # Leads visualizados (assumir que todos foram visualizados)
        visualizados = recebidos

        # Leads aceitos
        aceitos = self.db.query(Referral).filter(
            Referral.lawyer_id == lawyer_id,
            Referral.status == ReferralStatus.ACCEPTED,
            Referral.sent_at >= data_inicio
        ).count()

        # Convertidos (assumir 75% dos aceitos por enquanto)
        # TODO: Adicionar campo 'converted' em Referral
        convertidos = int(aceitos * 0.75)

        return {
            "recebidos": recebidos,
            "visualizados": visualizados,
            "aceitos": aceitos,
            "convertidos": convertidos,
            "taxa_aceitacao": round((aceitos / recebidos * 100), 1) if recebidos > 0 else 0,
            "taxa_conversao": round((convertidos / aceitos * 100), 1) if aceitos > 0 else 0
        }

    # ==========================================
    # PRAZOS E PROCESSOS
    # ==========================================

    def get_prazos_urgentes(self, lawyer_id: int, dias: int = 5) -> List[Dict[str, Any]]:
        """
        Prazos urgentes (próximos N dias)

        Returns:
            [
                {
                    "id": 1,
                    "processo_numero": "1234567-89.2024.8.26.0100",
                    "tipo": "recurso",
                    "data_limite": "2024-12-15",
                    "dias_restantes": 2,
                    "prioridade": "alta"
                },
                ...
            ]
        """
        try:
            from models import Prazo, Processo

            data_limite = datetime.utcnow().date() + timedelta(days=dias)

            results = self.db.query(Prazo, Processo).join(
                Processo, Prazo.processo_id == Processo.id
            ).filter(
                Prazo.lawyer_id == lawyer_id,
                Prazo.cumprido == False,
                Prazo.data_limite <= data_limite
            ).order_by(
                Prazo.data_limite
            ).all()

            prazos = []
            for prazo, processo in results:
                dias_restantes = (prazo.data_limite - datetime.utcnow().date()).days

                # Definir prioridade
                if dias_restantes <= 1:
                    prioridade = "critica"
                elif dias_restantes <= 3:
                    prioridade = "alta"
                else:
                    prioridade = "media"

                prazos.append({
                    "id": prazo.id,
                    "processo_numero": processo.numero,
                    "processo_id": processo.id,
                    "tipo": prazo.tipo,
                    "data_limite": prazo.data_limite.isoformat(),
                    "dias_restantes": dias_restantes,
                    "prioridade": prioridade
                })

            return prazos

        except Exception as e:
            print(f"Erro ao buscar prazos: {e}")
            return []

    def get_processos_recentes(self, lawyer_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Processos monitorados recentes

        Returns:
            Lista de processos com última atualização
        """
        try:
            from models import Processo

            processos = self.db.query(Processo).filter(
                Processo.lawyer_id == lawyer_id,
                Processo.monitorar == True
            ).order_by(
                desc(Processo.ultima_atualizacao)
            ).limit(limit).all()

            return [
                {
                    "id": p.id,
                    "numero": p.numero,
                    "tribunal": p.tribunal,
                    "classe": p.classe,
                    "assunto": p.assunto,
                    "ultima_atualizacao": p.ultima_atualizacao.isoformat() if p.ultima_atualizacao else None
                }
                for p in processos
            ]

        except Exception as e:
            print(f"Erro ao buscar processos: {e}")
            return []

    # ==========================================
    # AGENDAMENTOS
    # ==========================================

    def get_proximos_agendamentos(self, lawyer_id: int, dias: int = 7) -> List[Dict[str, Any]]:
        """
        Próximos agendamentos

        Returns:
            Lista de consultas agendadas
        """
        try:
            from models import Agendamento

            data_limite = datetime.utcnow() + timedelta(days=dias)

            agendamentos = self.db.query(Agendamento).filter(
                Agendamento.lawyer_id == lawyer_id,
                Agendamento.data_hora >= datetime.utcnow(),
                Agendamento.data_hora <= data_limite,
                Agendamento.status.in_(['pendente', 'confirmado'])
            ).order_by(
                Agendamento.data_hora
            ).all()

            return [
                {
                    "id": a.id,
                    "data_hora": a.data_hora.isoformat(),
                    "duracao_minutos": a.duracao_minutos,
                    "tipo": a.tipo,
                    "status": a.status,
                    "case_id": a.case_id
                }
                for a in agendamentos
            ]

        except Exception as e:
            print(f"Erro ao buscar agendamentos: {e}")
            return []

    # ==========================================
    # PERFIL E PERFORMANCE
    # ==========================================

    def get_performance_score(self, lawyer_id: int) -> Dict[str, Any]:
        """
        Score de performance do advogado

        Returns:
            {
                "score_geral": 85,
                "tempo_resposta_medio": 4.5,  # horas
                "taxa_aceitacao": 75.5,
                "avaliacao_media": 4.8,
                "casos_resolvidos": 23
            }
        """
        from models import Lawyer, Referral, ReferralStatus

        lawyer = self.db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()

        if not lawyer:
            return {}

        # Tempo médio de resposta (mock por enquanto)
        # TODO: Calcular tempo real entre sent_at e accepted_at/rejected_at
        tempo_resposta_medio = 4.5

        # Taxa de aceitação
        total_leads = self.db.query(Referral).filter(
            Referral.lawyer_id == lawyer_id
        ).count()

        leads_aceitos = self.db.query(Referral).filter(
            Referral.lawyer_id == lawyer_id,
            Referral.status == ReferralStatus.ACCEPTED
        ).count()

        taxa_aceitacao = (leads_aceitos / total_leads * 100) if total_leads > 0 else 0

        # Score geral (média ponderada)
        score_geral = int(
            (lawyer.success_score * 0.4) +
            (taxa_aceitacao * 0.3) +
            ((lawyer.rating or 0) * 20 * 0.3)  # rating de 0-5 convertido para 0-100
        )

        return {
            "score_geral": score_geral,
            "tempo_resposta_medio": tempo_resposta_medio,
            "taxa_aceitacao": round(taxa_aceitacao, 1),
            "avaliacao_media": float(lawyer.rating) if lawyer.rating else 0.0,
            "casos_resolvidos": lawyer.accepted_leads or 0
        }
