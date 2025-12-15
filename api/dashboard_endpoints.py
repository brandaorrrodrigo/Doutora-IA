"""
Endpoints do Dashboard do Advogado
Métricas, estatísticas, gráficos e KPIs
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from main import get_db
from services.jwt_auth import get_current_lawyer
from services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ==========================================
# OVERVIEW E MÉTRICAS PRINCIPAIS
# ==========================================

@router.get("/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> Dict[str, Any]:
    """
    Visão geral do dashboard

    **Retorna:**
    - Leads pendentes
    - Leads aceitos no mês
    - Taxa de conversão
    - Valor estimado de honorários
    - Prazos próximos
    - Agendamentos hoje
    - Notificações não lidas
    - Avaliação média

    **Requer:** Bearer token
    """
    dashboard = DashboardService(db)
    return dashboard.get_overview(lawyer.id)


@router.get("/performance")
async def get_performance_score(
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> Dict[str, Any]:
    """
    Score de performance do advogado

    **Retorna:**
    - Score geral (0-100)
    - Tempo médio de resposta
    - Taxa de aceitação
    - Avaliação média
    - Casos resolvidos

    **Requer:** Bearer token
    """
    dashboard = DashboardService(db)
    return dashboard.get_performance_score(lawyer.id)


# ==========================================
# HISTÓRICO E FILTROS
# ==========================================

@router.get("/leads/history")
async def get_leads_history(
    days: int = Query(30, ge=1, le=365, description="Últimos N dias"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> List[Dict[str, Any]]:
    """
    Histórico de leads com filtros

    **Parâmetros:**
    - **days**: Últimos N dias (padrão: 30)
    - **status**: Filtrar por status (pending, accepted, rejected)

    **Retorna:** Lista de leads com detalhes completos

    **Requer:** Bearer token
    """
    dashboard = DashboardService(db)
    return dashboard.get_leads_history(lawyer.id, days, status)


# ==========================================
# GRÁFICOS E ESTATÍSTICAS
# ==========================================

@router.get("/charts/leads-by-day")
async def get_leads_by_day_chart(
    days: int = Query(30, ge=1, le=90, description="Últimos N dias"),
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> List[Dict[str, Any]]:
    """
    Dados para gráfico de leads por dia

    **Uso:** Gráfico de linha mostrando evolução de leads

    **Retorna:**
    ```json
    [
        {
            "data": "2024-12-01",
            "total": 5,
            "aceitos": 3,
            "rejeitados": 2
        },
        ...
    ]
    ```

    **Requer:** Bearer token
    """
    dashboard = DashboardService(db)
    return dashboard.get_leads_by_day(lawyer.id, days)


@router.get("/charts/leads-by-area")
async def get_leads_by_area_chart(
    days: int = Query(30, ge=1, le=365, description="Últimos N dias"),
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> List[Dict[str, Any]]:
    """
    Distribuição de leads por área jurídica

    **Uso:** Gráfico de pizza/rosca mostrando áreas mais frequentes

    **Retorna:**
    ```json
    [
        {
            "area": "familia",
            "total": 15,
            "percentual": 45.5
        },
        ...
    ]
    ```

    **Requer:** Bearer token
    """
    dashboard = DashboardService(db)
    return dashboard.get_leads_by_area(lawyer.id, days)


@router.get("/charts/conversion-funnel")
async def get_conversion_funnel(
    days: int = Query(30, ge=1, le=365, description="Últimos N dias"),
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> Dict[str, Any]:
    """
    Funil de conversão

    **Uso:** Gráfico de funil mostrando conversão de leads

    **Retorna:**
    ```json
    {
        "recebidos": 100,
        "visualizados": 85,
        "aceitos": 60,
        "convertidos": 45,
        "taxa_aceitacao": 60.0,
        "taxa_conversao": 75.0
    }
    ```

    **Requer:** Bearer token
    """
    dashboard = DashboardService(db)
    return dashboard.get_conversion_funnel(lawyer.id, days)


# ==========================================
# PRAZOS E PROCESSOS
# ==========================================

@router.get("/prazos/urgentes")
async def get_prazos_urgentes(
    dias: int = Query(5, ge=1, le=30, description="Próximos N dias"),
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> List[Dict[str, Any]]:
    """
    Prazos urgentes (próximos N dias)

    **Retorna:** Lista de prazos ordenados por data limite

    **Prioridades:**
    - **critica**: <= 1 dia
    - **alta**: 2-3 dias
    - **media**: 4-5 dias

    **Requer:** Bearer token
    """
    dashboard = DashboardService(db)
    return dashboard.get_prazos_urgentes(lawyer.id, dias)


@router.get("/processos/recentes")
async def get_processos_recentes(
    limit: int = Query(10, ge=1, le=50, description="Limite de resultados"),
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> List[Dict[str, Any]]:
    """
    Processos monitorados recentes

    **Retorna:** Lista dos processos com última atualização

    **Requer:** Bearer token
    """
    dashboard = DashboardService(db)
    return dashboard.get_processos_recentes(lawyer.id, limit)


# ==========================================
# AGENDAMENTOS
# ==========================================

@router.get("/agendamentos/proximos")
async def get_proximos_agendamentos(
    dias: int = Query(7, ge=1, le=30, description="Próximos N dias"),
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> List[Dict[str, Any]]:
    """
    Próximos agendamentos

    **Retorna:** Lista de consultas agendadas ordenadas por data/hora

    **Requer:** Bearer token
    """
    dashboard = DashboardService(db)
    return dashboard.get_proximos_agendamentos(lawyer.id, dias)


# ==========================================
# RESUMO COMPLETO (TUDO EM UM ENDPOINT)
# ==========================================

@router.get("/full")
async def get_full_dashboard(
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> Dict[str, Any]:
    """
    Dashboard completo com todos os dados

    **Uso:** Para carregar dashboard de uma vez (evitar múltiplas requisições)

    **Retorna:** Objeto com todas as seções do dashboard

    **Requer:** Bearer token
    """
    dashboard = DashboardService(db)

    return {
        "overview": dashboard.get_overview(lawyer.id),
        "performance": dashboard.get_performance_score(lawyer.id),
        "leads_history": dashboard.get_leads_history(lawyer.id, days=7),
        "charts": {
            "leads_by_day": dashboard.get_leads_by_day(lawyer.id, days=30),
            "leads_by_area": dashboard.get_leads_by_area(lawyer.id, days=30),
            "conversion_funnel": dashboard.get_conversion_funnel(lawyer.id, days=30)
        },
        "prazos_urgentes": dashboard.get_prazos_urgentes(lawyer.id, dias=5),
        "processos_recentes": dashboard.get_processos_recentes(lawyer.id, limit=5),
        "proximos_agendamentos": dashboard.get_proximos_agendamentos(lawyer.id, dias=7)
    }


# ==========================================
# ATALHOS E AÇÕES RÁPIDAS
# ==========================================

@router.get("/quick-stats")
async def get_quick_stats(
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> Dict[str, Any]:
    """
    Estatísticas rápidas para header/navbar

    **Uso:** Mostrar números importantes no topo da página

    **Retorna:**
    ```json
    {
        "leads_pendentes": 3,
        "prazos_urgentes": 1,
        "agendamentos_hoje": 2,
        "notificacoes": 5
    }
    ```

    **Requer:** Bearer token
    """
    dashboard = DashboardService(db)
    overview = dashboard.get_overview(lawyer.id)

    return {
        "leads_pendentes": overview.get("leads_pendentes", 0),
        "prazos_urgentes": overview.get("prazos_proximos", 0),
        "agendamentos_hoje": overview.get("agendamentos_hoje", 0),
        "notificacoes": overview.get("notificacoes_nao_lidas", 0)
    }


@router.get("/alerts")
async def get_dashboard_alerts(
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> List[Dict[str, Any]]:
    """
    Alertas e notificações importantes

    **Retorna:** Lista de alertas ordenados por prioridade

    **Tipos de alerta:**
    - Prazos críticos (< 24h)
    - Leads expirando
    - Agendamentos próximos
    - Ações pendentes

    **Requer:** Bearer token
    """
    dashboard = DashboardService(db)

    alerts = []

    # Prazos críticos
    prazos = dashboard.get_prazos_urgentes(lawyer.id, dias=2)
    for prazo in prazos:
        if prazo['prioridade'] == 'critica':
            alerts.append({
                "tipo": "prazo_critico",
                "titulo": f"Prazo crítico: {prazo['tipo']}",
                "mensagem": f"Processo {prazo['processo_numero']} vence em {prazo['dias_restantes']} dia(s)",
                "prioridade": "alta",
                "link": f"/processos/{prazo['processo_id']}",
                "data": prazo['data_limite']
            })

    # Agendamentos hoje
    agendamentos = dashboard.get_proximos_agendamentos(lawyer.id, dias=1)
    for agend in agendamentos:
        alerts.append({
            "tipo": "agendamento",
            "titulo": "Consulta agendada hoje",
            "mensagem": f"Consulta de {agend['tipo']} às {agend['data_hora'][:16]}",
            "prioridade": "media",
            "link": f"/agendamentos/{agend['id']}",
            "data": agend['data_hora']
        })

    # Leads expirando
    from models import Referral, ReferralStatus
    from datetime import datetime, timedelta

    leads_expirando = db.query(Referral).filter(
        Referral.lawyer_id == lawyer.id,
        Referral.status == ReferralStatus.PENDING,
        Referral.expires_at <= datetime.utcnow() + timedelta(hours=6),
        Referral.expires_at > datetime.utcnow()
    ).count()

    if leads_expirando > 0:
        alerts.append({
            "tipo": "leads_expirando",
            "titulo": f"{leads_expirando} lead(s) expirando em breve",
            "mensagem": "Você tem leads que expiram nas próximas 6 horas. Responda agora!",
            "prioridade": "alta",
            "link": "/leads",
            "data": None
        })

    # Ordenar por prioridade
    prioridade_ordem = {"alta": 0, "media": 1, "baixa": 2}
    alerts.sort(key=lambda x: prioridade_ordem.get(x['prioridade'], 3))

    return alerts
