"""
Novos endpoints para Fase 2 (Integração Tribunais) e Fase 3 (Marketplace)

Adicionar ao main.py com: app.include_router(router)
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Importar dependências
import sys
import os
sys.path.append(os.path.dirname(__file__))

from models import Lawyer, Case
from main import get_db
from services.jwt_auth import get_current_lawyer, get_optional_lawyer

router = APIRouter()


# ============================================
# SCHEMAS
# ============================================

class ProcessoConsultaRequest(BaseModel):
    numero_processo: str
    tribunal: str = "trf3"  # trf3, tjsp, etc


class ProcessoConsultaResponse(BaseModel):
    numero: str
    tribunal: str
    classe: str
    assunto: str
    partes: List[dict]
    movimentacoes: List[dict]
    documentos: List[dict]


class PeticaoProtocolarRequest(BaseModel):
    numero_processo: str
    tipo_peticao: str
    pdf_path: str
    descricao: str = ""


class LeadResponse(BaseModel):
    id: int
    area: str
    sub_area: Optional[str]
    descricao_resumida: str
    probabilidade: str
    score_qualidade: int
    valor_estimado: float
    cliente: dict


class LeadAcaoRequest(BaseModel):
    case_id: int
    acao: str  # "aceitar" ou "rejeitar"
    motivo: Optional[str] = ""


class AgendamentoRequest(BaseModel):
    lawyer_id: int
    case_id: int
    data_hora: str  # ISO format
    tipo: str = "consulta_inicial"  # consulta_inicial, retorno, etc


class AvaliacaoRequest(BaseModel):
    lawyer_id: int
    case_id: int
    nota: int  # 1-5
    comentario: Optional[str] = ""


# ============================================
# FASE 2: INTEGRAÇÃO COM TRIBUNAIS
# ============================================

@router.post("/tribunais/consultar-processo", response_model=ProcessoConsultaResponse)
async def consultar_processo_tribunal(
    request: ProcessoConsultaRequest,
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
):
    """
    Consulta processo nos tribunais (PJe, eProc, etc)

    FASE 2.1 - Integração com PJe/eProc
    """
    from services.tribunals import get_pje, EProcIntegration

    try:
        if request.tribunal.startswith("trf"):
            # PJe (Tribunais Federais)
            pje = get_pje(request.tribunal)
            processo = pje.consultar_processo(request.numero_processo)

        elif request.tribunal.startswith("tj"):
            # eProc (Tribunais Estaduais)
            eproc = EProcIntegration(request.tribunal)
            processo = eproc.consultar_processo(request.numero_processo)

        else:
            raise HTTPException(status_code=400, detail="Tribunal não suportado")

        if not processo:
            raise HTTPException(status_code=404, detail="Processo não encontrado")

        return ProcessoConsultaResponse(**processo)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar: {str(e)}")


@router.post("/tribunais/protocolar-peticao")
async def protocolar_peticao_tribunal(
    request: PeticaoProtocolarRequest,
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
):
    """
    Protocola petição direto no tribunal

    FASE 2.1 - Protocolamento eletrônico
    """
    from services.tribunals import get_pje

    try:
        pje = get_pje()
        resultado = pje.protocolar_peticao(
            numero_processo=request.numero_processo,
            tipo_peticao=request.tipo_peticao,
            pdf_path=request.pdf_path,
            descricao=request.descricao
        )

        if not resultado.get("sucesso"):
            raise HTTPException(status_code=400, detail=resultado.get("mensagem"))

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao protocolar: {str(e)}")


@router.get("/tribunais/diario-oficial")
async def consultar_diario_oficial(
    tribunal: str,
    data: Optional[str] = None,
    advogado_oab: Optional[str] = None,
    numero_processo: Optional[str] = None,
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
):
    """
    Consulta publicações no Diário Oficial Eletrônico

    FASE 2.3 - Integração com Diário Oficial
    """
    from services.tribunals import get_diario_monitor

    try:
        monitor = get_diario_monitor()
        publicacoes = monitor.buscar_publicacoes(
            tribunal=tribunal,
            data=data,
            advogado_oab=advogado_oab,
            numero_processo=numero_processo
        )

        return {
            "total": len(publicacoes),
            "publicacoes": publicacoes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar DJe: {str(e)}")


@router.get("/tribunais/jurisprudencia-unificada")
async def buscar_jurisprudencia_unificada(
    query: str,
    tribunais: Optional[str] = None,  # Comma-separated: "stf,stj,trf3"
    limit: int = 10
):
    """
    Busca jurisprudência em múltiplos tribunais simultaneamente

    FASE 2.2 - Busca unificada CNJ
    """
    from services.tribunals import get_jurisprudencia_unificada

    try:
        juris = get_jurisprudencia_unificada()

        tribunais_lista = tribunais.split(",") if tribunais else None

        resultados = juris.buscar_todos(
            query=query,
            tribunais=tribunais_lista,
            limit=limit
        )

        # Contar total
        total = sum(len(r) for r in resultados.values())

        return {
            "query": query,
            "total": total,
            "por_tribunal": resultados
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")


# ============================================
# FASE 3: MARKETPLACE DE LEADS
# ============================================

@router.get("/marketplace/leads", response_model=List[LeadResponse])
async def listar_meus_leads(
    area: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
):
    """
    Lista leads disponíveis para um advogado

    FASE 3.1 - Marketplace Invertido (cliente pagou R$ 7)
    """
    from services.marketplace import get_marketplace

    try:
        marketplace = get_marketplace(db)
        leads = marketplace.listar_leads_disponiveis(
            lawyer_id=lawyer.id,
            area=area,
            limit=limit
        )

        return leads

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar leads: {str(e)}")


@router.post("/marketplace/leads/acao")
async def acao_em_lead(
    request: LeadAcaoRequest,
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
):
    """
    Advogado aceita ou rejeita um lead

    FASE 3.1 - Aceitação de leads qualificados
    """
    from services.marketplace import get_marketplace

    try:
        marketplace = get_marketplace(db)

        if request.acao == "aceitar":
            resultado = marketplace.aceitar_lead(lawyer.id, request.case_id)

            if "erro" in resultado:
                raise HTTPException(status_code=400, detail=resultado["erro"])

            return resultado

        elif request.acao == "rejeitar":
            sucesso = marketplace.rejeitar_lead(
                lawyer.id,
                request.case_id,
                request.motivo
            )

            if not sucesso:
                raise HTTPException(status_code=404, detail="Lead não encontrado")

            return {"sucesso": True, "mensagem": "Lead rejeitado"}

        else:
            raise HTTPException(status_code=400, detail="Ação inválida")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.get("/marketplace/estatisticas")
async def estatisticas_marketplace(db: Session = Depends(get_db)):
    """
    Estatísticas gerais do marketplace

    FASE 3.1 - Métricas do marketplace
    """
    from services.marketplace import get_marketplace

    try:
        marketplace = get_marketplace(db)
        stats = marketplace.estatisticas_marketplace()

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


# ============================================
# PERFIL PÚBLICO DE ADVOGADOS
# ============================================

@router.get("/advogados/{estado}/{cidade}/{area}/{nome}")
async def perfil_publico_advogado(
    estado: str,
    cidade: str,
    area: str,
    nome: str,
    db: Session = Depends(get_db)
):
    """
    Retorna perfil público do advogado (HTML ou JSON)

    FASE 3.2 - SEO Local
    """
    from services.lawyer_profile import get_profile_generator

    try:
        # Buscar advogado pelo slug
        # TODO: adicionar campo slug na tabela Lawyer
        # Por ora, buscar por similaridade no nome

        lawyer = db.query(Lawyer).filter(
            Lawyer.name.ilike(f"%{nome.replace('-', ' ')}%")
        ).first()

        if not lawyer:
            raise HTTPException(status_code=404, detail="Advogado não encontrado")

        profile_gen = get_profile_generator(db)
        html = profile_gen.gerar_html_perfil(lawyer.id)

        # Retornar HTML diretamente
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.post("/advogados/{lawyer_id}/gerar-perfil")
async def gerar_perfil_publico(
    lawyer_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Gera/atualiza perfil público do advogado

    FASE 3.2 - Geração de landing page SEO
    """
    from services.lawyer_profile import get_profile_generator

    def gerar_perfil_task():
        profile_gen = get_profile_generator(db)
        url = profile_gen.gerar_url_publica(lawyer_id)
        profile_gen.salvar_perfil_html(lawyer_id)
        return url

    background_tasks.add_task(gerar_perfil_task)

    return {
        "mensagem": "Perfil será gerado em background",
        "lawyer_id": lawyer_id
    }


# ============================================
# AGENDAMENTO
# ============================================

@router.post("/agendamento/criar")
async def criar_agendamento(
    request: AgendamentoRequest,
    db: Session = Depends(get_db)
):
    """
    Cria agendamento entre cliente e advogado

    FASE 3.2 - Sistema de agendamento
    """
    # TODO: Implementar tabela Agendamento

    return {
        "sucesso": True,
        "agendamento_id": 1,
        "data_hora": request.data_hora,
        "mensagem": "Agendamento criado. Você receberá confirmação por email."
    }


# ============================================
# AVALIAÇÕES
# ============================================

@router.post("/avaliacoes/criar")
async def criar_avaliacao(
    request: AvaliacaoRequest,
    db: Session = Depends(get_db)
):
    """
    Cliente avalia advogado após atendimento

    FASE 3.2 - Sistema de avaliações
    """
    # TODO: Implementar tabela Avaliacao

    # Atualizar success_score do advogado
    lawyer = db.query(Lawyer).filter(Lawyer.id == request.lawyer_id).first()

    if lawyer:
        # TODO: Recalcular média real
        # Por ora, apenas confirmar
        pass

    return {
        "sucesso": True,
        "mensagem": "Avaliação registrada com sucesso!"
    }


@router.get("/avaliacoes/advogado/{lawyer_id}")
async def listar_avaliacoes_advogado(
    lawyer_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Lista avaliações de um advogado

    FASE 3.2 - Exibir avaliações
    """
    # TODO: Implementar query real

    # Mock data
    avaliacoes = [
        {
            "id": 1,
            "nota": 5,
            "comentario": "Excelente profissional! Resolveu meu caso rapidamente.",
            "data": "2024-11-15",
            "cliente": "Cliente Verificado"
        },
        {
            "id": 2,
            "nota": 5,
            "comentario": "Muito atencioso e competente.",
            "data": "2024-10-20",
            "cliente": "Cliente Verificado"
        }
    ]

    return {
        "lawyer_id": lawyer_id,
        "total": len(avaliacoes),
        "media": 4.8,
        "avaliacoes": avaliacoes
    }


# ============================================
# PARCERIAS B2B2C
# ============================================

@router.post("/parcerias/sindicato/lead")
async def criar_lead_parceria(
    parceiro_id: str,
    parceiro_tipo: str,  # sindicato, empresa, banco
    case_data: dict,
    db: Session = Depends(get_db)
):
    """
    Cria lead de parceria B2B2C

    FASE 3.3 - Parcerias (Sindicatos, Bancos, etc)
    """
    # Criar caso
    from models import Case

    case = Case(
        description=case_data.get("descricao"),
        area=case_data.get("area"),
        # TODO: adicionar campo parceiro_id
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    # Processar com marketplace
    from services.marketplace import get_marketplace

    marketplace = get_marketplace(db)

    # Marcar como pago (parceria já paga)
    case.report_paid = True
    db.commit()

    # Atribuir a advogado
    marketplace.criar_lead_de_caso(case.id)

    return {
        "sucesso": True,
        "case_id": case.id,
        "mensagem": "Lead de parceria criado e atribuído"
    }
