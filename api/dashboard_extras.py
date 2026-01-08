"""
Endpoints Extras do Dashboard
Gráficos de receita, timeline, exportação de relatórios
"""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json

from database import get_db
from services.jwt_auth import get_current_lawyer

router = APIRouter(prefix="/dashboard", tags=["Dashboard Extras"])


# ==========================================
# GRÁFICOS DE RECEITA
# ==========================================

@router.get("/charts/receita-mensal")
async def get_receita_mensal(
    meses: int = 6,
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> List[Dict[str, Any]]:
    """
    Gráfico de receita mensal (últimos N meses)

    **Retorna:**
    ```json
    [
        {
            "mes": "2024-12",
            "mes_nome": "Dezembro",
            "receita_real": 15000.00,
            "receita_estimada": 25000.00,
            "leads_convertidos": 5,
            "ticket_medio": 3000.00
        },
        ...
    ]
    ```
    """
    from models import Referral, Case, ReferralStatus

    # Calcular data de início
    data_inicio = datetime.utcnow() - timedelta(days=meses * 30)

    # Query agrupada por mês
    results = db.query(
        func.date_trunc('month', Referral.accepted_at).label('mes'),
        func.count(Referral.id).label('total_aceitos'),
        func.sum(Case.estimated_fees).label('receita_estimada')
    ).join(
        Case, Referral.case_id == Case.id
    ).filter(
        Referral.lawyer_id == lawyer.id,
        Referral.status == ReferralStatus.ACCEPTED,
        Referral.accepted_at >= data_inicio
    ).group_by(
        func.date_trunc('month', Referral.accepted_at)
    ).order_by(
        func.date_trunc('month', Referral.accepted_at)
    ).all()

    # Processar resultados
    meses_nomes = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    receita = []
    for row in results:
        if row.mes:
            mes_dt = row.mes
            receita.append({
                "mes": mes_dt.strftime("%Y-%m"),
                "mes_nome": meses_nomes[mes_dt.month - 1],
                "receita_real": 0,  # TODO: Implementar quando tiver dados de pagamento
                "receita_estimada": float(row.receita_estimada or 0),
                "leads_convertidos": row.total_aceitos,
                "ticket_medio": float(row.receita_estimada or 0) / row.total_aceitos if row.total_aceitos > 0 else 0
            })

    return receita


@router.get("/charts/receita-por-area")
async def get_receita_por_area(
    meses: int = 3,
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> List[Dict[str, Any]]:
    """
    Receita estimada por área jurídica

    **Retorna:**
    ```json
    [
        {
            "area": "familia",
            "receita_estimada": 45000.00,
            "leads_aceitos": 15,
            "ticket_medio": 3000.00,
            "percentual_receita": 35.5
        },
        ...
    ]
    ```
    """
    from models import Referral, Case, ReferralStatus

    data_inicio = datetime.utcnow() - timedelta(days=meses * 30)

    results = db.query(
        Case.area,
        func.count(Referral.id).label('total_aceitos'),
        func.sum(Case.estimated_fees).label('receita_estimada')
    ).join(
        Case, Referral.case_id == Case.id
    ).filter(
        Referral.lawyer_id == lawyer.id,
        Referral.status == ReferralStatus.ACCEPTED,
        Referral.accepted_at >= data_inicio
    ).group_by(
        Case.area
    ).order_by(
        desc('receita_estimada')
    ).all()

    receita_total = sum(float(r.receita_estimada or 0) for r in results)

    areas = []
    for row in results:
        receita_est = float(row.receita_estimada or 0)
        areas.append({
            "area": row.area,
            "receita_estimada": receita_est,
            "leads_aceitos": row.total_aceitos,
            "ticket_medio": receita_est / row.total_aceitos if row.total_aceitos > 0 else 0,
            "percentual_receita": round((receita_est / receita_total * 100), 1) if receita_total > 0 else 0
        })

    return areas


# ==========================================
# TIMELINE DE ATIVIDADES
# ==========================================

@router.get("/timeline")
async def get_timeline(
    dias: int = 7,
    limit: int = 50,
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> List[Dict[str, Any]]:
    """
    Timeline de atividades recentes

    **Retorna:**
    ```json
    [
        {
            "id": 1,
            "tipo": "lead_aceito",
            "titulo": "Lead aceito",
            "descricao": "Você aceitou um lead de Direito de Família",
            "icone": "check-circle",
            "cor": "success",
            "timestamp": "2024-12-09T14:30:00Z",
            "link": "/leads/123"
        },
        ...
    ]
    ```
    """
    from models import Referral, Case, ReferralStatus

    data_inicio = datetime.utcnow() - timedelta(days=dias)
    timeline = []

    # Leads aceitos
    leads_aceitos = db.query(Referral, Case).join(
        Case, Referral.case_id == Case.id
    ).filter(
        Referral.lawyer_id == lawyer.id,
        Referral.status == ReferralStatus.ACCEPTED,
        Referral.accepted_at >= data_inicio
    ).order_by(
        desc(Referral.accepted_at)
    ).limit(limit).all()

    for ref, case in leads_aceitos:
        timeline.append({
            "id": f"lead_aceito_{ref.id}",
            "tipo": "lead_aceito",
            "titulo": "Lead aceito",
            "descricao": f"Você aceitou um lead de {case.area.capitalize()} - R$ {case.estimated_fees:,.2f}",
            "icone": "check-circle",
            "cor": "success",
            "timestamp": ref.accepted_at.isoformat() if ref.accepted_at else None,
            "link": f"/leads/{ref.id}"
        })

    # Leads rejeitados
    leads_rejeitados = db.query(Referral, Case).join(
        Case, Referral.case_id == Case.id
    ).filter(
        Referral.lawyer_id == lawyer.id,
        Referral.status == ReferralStatus.REJECTED,
        Referral.rejected_at >= data_inicio
    ).order_by(
        desc(Referral.rejected_at)
    ).limit(limit).all()

    for ref, case in leads_rejeitados:
        timeline.append({
            "id": f"lead_rejeitado_{ref.id}",
            "tipo": "lead_rejeitado",
            "titulo": "Lead rejeitado",
            "descricao": f"Você rejeitou um lead de {case.area.capitalize()}",
            "icone": "times-circle",
            "cor": "danger",
            "timestamp": ref.rejected_at.isoformat() if ref.rejected_at else None,
            "link": None
        })

    # Prazos cumpridos
    try:
        from models import Prazo

        prazos_cumpridos = db.query(Prazo).filter(
            Prazo.lawyer_id == lawyer.id,
            Prazo.cumprido == True,
            Prazo.cumprido_em >= data_inicio
        ).order_by(
            desc(Prazo.cumprido_em)
        ).limit(limit).all()

        for prazo in prazos_cumpridos:
            timeline.append({
                "id": f"prazo_cumprido_{prazo.id}",
                "tipo": "prazo_cumprido",
                "titulo": "Prazo cumprido",
                "descricao": f"Você cumpriu o prazo de {prazo.tipo}",
                "icone": "calendar-check",
                "cor": "info",
                "timestamp": prazo.cumprido_em.isoformat() if prazo.cumprido_em else None,
                "link": f"/processos/{prazo.processo_id}"
            })
    except:
        pass

    # Ordenar por timestamp (mais recente primeiro)
    timeline.sort(key=lambda x: x['timestamp'] if x['timestamp'] else '', reverse=True)

    return timeline[:limit]


# ==========================================
# EXPORTAÇÃO DE RELATÓRIOS
# ==========================================

@router.get("/export/csv")
async def export_leads_csv(
    meses: int = 1,
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
):
    """
    Exporta leads em formato CSV

    **Retorna:** Arquivo CSV para download
    """
    from models import Referral, Case
    import csv
    from io import StringIO

    data_inicio = datetime.utcnow() - timedelta(days=meses * 30)

    # Query de leads
    results = db.query(Referral, Case).join(
        Case, Referral.case_id == Case.id
    ).filter(
        Referral.lawyer_id == lawyer.id,
        Referral.sent_at >= data_inicio
    ).order_by(
        desc(Referral.sent_at)
    ).all()

    # Criar CSV
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Data Recebido',
        'Área',
        'Sub-Área',
        'Probabilidade',
        'Valor Estimado',
        'Status',
        'Data Ação',
        'Motivo Rejeição'
    ])

    # Dados
    for ref, case in results:
        writer.writerow([
            ref.sent_at.strftime('%d/%m/%Y %H:%M') if ref.sent_at else '',
            case.area,
            case.sub_area or '',
            case.probability,
            f'R$ {case.estimated_fees:,.2f}' if case.estimated_fees else 'R$ 0,00',
            ref.status,
            (ref.accepted_at or ref.rejected_at or ref.expires_at).strftime('%d/%m/%Y %H:%M') if (ref.accepted_at or ref.rejected_at) else '',
            ref.rejection_reason or ''
        ])

    # Retornar CSV
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=leads_{lawyer.id}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/export/json")
async def export_dashboard_json(
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
):
    """
    Exporta todos os dados do dashboard em JSON

    **Retorna:** Arquivo JSON para download
    """
    from services.dashboard import DashboardService

    dashboard = DashboardService(db)

    # Coletar todos os dados
    data = {
        "advogado": {
            "id": lawyer.id,
            "nome": lawyer.name,
            "oab": lawyer.oab,
            "email": lawyer.email
        },
        "overview": dashboard.get_overview(lawyer.id),
        "performance": dashboard.get_performance_score(lawyer.id),
        "leads_history": dashboard.get_leads_history(lawyer.id, days=30),
        "charts": {
            "leads_by_day": dashboard.get_leads_by_day(lawyer.id, days=30),
            "leads_by_area": dashboard.get_leads_by_area(lawyer.id, days=30),
            "conversion_funnel": dashboard.get_conversion_funnel(lawyer.id, days=30)
        },
        "prazos_urgentes": dashboard.get_prazos_urgentes(lawyer.id, dias=5),
        "gerado_em": datetime.utcnow().isoformat()
    }

    return Response(
        content=json.dumps(data, indent=2, ensure_ascii=False),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=dashboard_{lawyer.id}_{datetime.utcnow().strftime('%Y%m%d')}.json"
        }
    )


# ==========================================
# COMPARAÇÕES E RANKINGS
# ==========================================

@router.get("/ranking/performance")
async def get_ranking_performance(
    limit: int = 10,
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
) -> Dict[str, Any]:
    """
    Ranking de performance (onde você está em relação a outros advogados)

    **Retorna:**
    ```json
    {
        "sua_posicao": 5,
        "total_advogados": 150,
        "percentil": 96.7,
        "seu_score": 85,
        "top_10": [...]
    }
    ```
    """
    from models import Lawyer

    # Buscar todos advogados ativos ordenados por success_score
    ranking = db.query(Lawyer).filter(
        Lawyer.is_active == True
    ).order_by(
        desc(Lawyer.success_score)
    ).all()

    # Encontrar posição do advogado atual
    sua_posicao = next((i + 1 for i, l in enumerate(ranking) if l.id == lawyer.id), None)

    total_advogados = len(ranking)
    percentil = ((total_advogados - sua_posicao + 1) / total_advogados * 100) if sua_posicao else 0

    # Top 10
    top_10 = [
        {
            "posicao": i + 1,
            "nome": l.name if i < 3 else f"Advogado #{l.id}",  # Anonimizar exceto top 3
            "score": float(l.success_score or 0),
            "total_leads": l.accepted_leads or 0,
            "rating": float(l.rating or 0)
        }
        for i, l in enumerate(ranking[:limit])
    ]

    return {
        "sua_posicao": sua_posicao,
        "total_advogados": total_advogados,
        "percentil": round(percentil, 1),
        "seu_score": float(lawyer.success_score or 0),
        "top_10": top_10
    }
