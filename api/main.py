"""
Main FastAPI application for Doutora IA
"""
import os
import json
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import re

from models import Base, User, Case, Lawyer, Referral, Payment, CitationLog, CaseStatus, ReferralStatus, ProbabilityLevel
from schemas import (
    AnalyzeCaseRequest, AnalysisResponse, ReportRequest, ReportResponse,
    SearchRequest, SearchResult, ComposeRequest, ComposeResponse,
    LawyerRegisterRequest, LawyerSubscribeRequest, LeadAssignRequest,
    PaymentWebhookRequest, HealthResponse, Citation, CitationType
)
from rag import get_rag_system
from prompts import get_system_prompt, get_triagem_prompt, get_relatorio_prompt, get_compose_prompt
from services.pdf import generate_pdf_report
from services.citations import CitationManager
from services.payments import PaymentService
from services.queues import LeadQueue
from services.auth import get_password_hash

# Initialize FastAPI
app = FastAPI(
    title="Doutora IA API",
    description="API for legal case analysis and document generation",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/doutora")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OpenAI client for vLLM
from openai import OpenAI

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
VLLM_API_KEY = os.getenv("VLLM_API_KEY", "token-xyz")
CORPUS_UPDATE_DATE = os.getenv("CORPUS_UPDATE_DATE", "09/12/2025")

llm_client = OpenAI(
    base_url=VLLM_BASE_URL,
    api_key=VLLM_API_KEY
)

# Initialize services
rag = get_rag_system()
payment_service = PaymentService()
lead_queue = LeadQueue()
citation_manager = CitationManager()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Create Qdrant collections if they don't exist
        rag.create_collections()
        print("✓ Qdrant collections ready")
    except Exception as e:
        print(f"Warning: Could not initialize Qdrant: {e}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = {
        "api": "ok",
        "database": "ok",
        "qdrant": "ok",
        "llm": "ok"
    }

    # Check database
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except:
        services["database"] = "error"

    # Check Qdrant
    try:
        rag.client.get_collections()
    except:
        services["qdrant"] = "error"

    # Check LLM
    try:
        llm_client.models.list()
    except:
        services["llm"] = "error"

    status = "healthy" if all(v == "ok" for v in services.values()) else "degraded"

    return HealthResponse(
        status=status,
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services=services
    )


@app.post("/analyze_case", response_model=AnalysisResponse)
async def analyze_case(
    request: AnalyzeCaseRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a case and provide free triage or detailed analysis
    """
    # Get RAG context
    context = rag.get_context_for_case(
        descricao=request.descricao,
        limit_per_type=5 if request.detalhado else 3
    )

    # Build prompt
    prompt = get_triagem_prompt(
        descricao=request.descricao,
        contexto_rag=context,
        data_atualizacao=CORPUS_UPDATE_DATE
    )

    # Call LLM
    try:
        response = llm_client.chat.completions.create(
            model="llama3",
            messages=[
                {"role": "system", "content": get_system_prompt(CORPUS_UPDATE_DATE)},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2048 if request.detalhado else 1024
        )

        analysis_text = response.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    # Parse analysis
    parsed = parse_analysis_response(analysis_text)

    # Create case record
    case = Case(
        description=request.descricao,
        area=parsed.get("area", ""),
        sub_area=parsed.get("sub_area", ""),
        typification=parsed.get("tipificacao", ""),
        strategies=parsed.get("estrategias", ""),
        risks=parsed.get("riscos", ""),
        probability=parsed.get("probabilidade", ProbabilityLevel.MEDIA),
        cost_estimate=parsed.get("custos", ""),
        timeline_estimate=parsed.get("prazos", ""),
        checklist=parsed.get("checklist", []),
        draft_petition=parsed.get("rascunho_peticao", ""),
        citations=parsed.get("citacoes", []),
        score_prob=parsed.get("score_prob", 50.0),
        status=CaseStatus.ANALYZED,
        analyzed_at=datetime.utcnow()
    )

    # Link to user if email provided
    if request.user_email:
        user = db.query(User).filter(User.email == request.user_email).first()
        if not user:
            user = User(email=request.user_email, is_active=True)
            db.add(user)
            db.flush()
        case.user_id = user.id

    db.add(case)
    db.commit()
    db.refresh(case)

    # Log citations
    for cit in parsed.get("citacoes", []):
        citation_log = CitationLog(
            source_type="report",
            source_id=case.id,
            citation_id=cit.get("id", ""),
            citation_type=cit.get("tipo", ""),
            citation_title=cit.get("titulo", ""),
            citation_text=cit.get("texto", "")
        )
        db.add(citation_log)

    db.commit()

    # Convert citations to schema
    citations_schema = [
        Citation(
            id=cit.get("id", ""),
            tipo=CitationType(cit.get("tipo", "lei")),
            titulo=cit.get("titulo", ""),
            texto=cit.get("texto", ""),
            artigo_ou_tema=cit.get("artigo_ou_tema"),
            orgao=cit.get("orgao"),
            tribunal=cit.get("tribunal"),
            data=cit.get("data"),
            fonte_url=cit.get("fonte_url"),
            hierarquia=cit.get("hierarquia")
        )
        for cit in parsed.get("citacoes", [])
    ]

    return AnalysisResponse(
        case_id=case.id,
        tipificacao=parsed.get("tipificacao", ""),
        area=parsed.get("area", ""),
        sub_area=parsed.get("sub_area"),
        estrategias=parsed.get("estrategias", ""),
        riscos=parsed.get("riscos", ""),
        probabilidade=parsed.get("probabilidade", ProbabilityLevel.MEDIA),
        probabilidade_detalhes=parsed.get("probabilidade_detalhes", ""),
        custos=parsed.get("custos", ""),
        prazos=parsed.get("prazos", ""),
        checklist=parsed.get("checklist", []),
        rascunho_peticao=parsed.get("rascunho_peticao", ""),
        citacoes=citations_schema,
        base_atualizada_em=CORPUS_UPDATE_DATE
    )


@app.post("/report", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate premium PDF report for a case (R$ 7)
    """
    # Get case
    case = db.query(Case).filter(Case.id == request.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Check if already paid
    if not case.report_paid:
        raise HTTPException(status_code=402, detail="Payment required for report")

    # Generate PDF
    try:
        report_path = generate_pdf_report(case, CORPUS_UPDATE_DATE)
        case.report_url = f"/reports/{os.path.basename(report_path)}"
        db.commit()

        return ReportResponse(
            report_id=case.id,
            case_id=case.id,
            report_url=case.report_url,
            created_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@app.post("/search", response_model=SearchResult)
async def search(request: SearchRequest):
    """
    Unified search endpoint for laws, jurisprudence, súmulas, regulatory, doctrine
    """
    try:
        results = rag.search(
            query=request.query,
            tipo=request.tipo.value if request.tipo else None,
            area=request.area.value if request.area else None,
            orgao=request.orgao,
            tribunal=request.tribunal,
            data_inicio=request.data_inicio,
            data_fim=request.data_fim,
            limit=request.limit
        )

        citations = [
            Citation(
                id=r.get("id", ""),
                tipo=CitationType(r.get("tipo", "lei")),
                titulo=r.get("titulo", ""),
                texto=r.get("texto", ""),
                artigo_ou_tema=r.get("artigo_ou_tema"),
                orgao=r.get("orgao"),
                tribunal=r.get("tribunal"),
                data=r.get("data"),
                fonte_url=r.get("fonte_url"),
                hierarquia=r.get("hierarquia")
            )
            for r in results
        ]

        return SearchResult(
            results=citations,
            total=len(citations),
            query=request.query
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.post("/compose", response_model=ComposeResponse)
async def compose_document(
    request: ComposeRequest,
    db: Session = Depends(get_db)
):
    """
    Generate legal document (initial petition, contestation, appeal)
    """
    # Build metadata dict
    metadata = {
        "autor_nome": request.autor_nome,
        "autor_qualificacao": request.autor_qualificacao,
        "reu_nome": request.reu_nome,
        "reu_qualificacao": request.reu_qualificacao,
        "foro": request.foro,
        "vara": request.vara,
        "valor_causa": f"{request.valor_causa:,.2f}" if request.valor_causa else "0,00",
        "fatos_resumo": request.fatos_resumo,
        "citacoes_json": json.dumps([c.model_dump() for c in request.citacoes], ensure_ascii=False),
        "pedidos_lista": "\n".join(request.pedidos)
    }

    # Get LLM to generate blocks
    prompt = get_compose_prompt(
        tipo_peca=request.tipo_peca.value,
        area=request.area.value,
        metadata=metadata
    )

    try:
        response = llm_client.chat.completions.create(
            model="llama3",
            messages=[
                {"role": "system", "content": get_system_prompt(CORPUS_UPDATE_DATE)},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1536
        )

        llm_output = response.choices[0].message.content

        # Parse JSON response
        import json
        blocks = json.loads(llm_output)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation error: {str(e)}")

    # Generate document using template
    from services.pdf import generate_document

    doc_path = generate_document(
        tipo_peca=request.tipo_peca.value,
        area=request.area.value,
        metadata=metadata,
        blocks=blocks,
        citacoes=request.citacoes,
        format=request.export_format
    )

    # Generate unique ID
    import uuid
    doc_id = str(uuid.uuid4())

    doc_url = f"/documents/{os.path.basename(doc_path)}"

    return ComposeResponse(
        document_id=doc_id,
        document_url=doc_url,
        format=request.export_format,
        created_at=datetime.utcnow()
    )


@app.post("/lawyers/register")
async def register_lawyer(
    request: LawyerRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new lawyer"""
    # Check if already exists
    existing = db.query(Lawyer).filter(
        (Lawyer.email == request.email) | (Lawyer.oab == request.oab)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Lawyer already registered")

    # Create lawyer
    lawyer = Lawyer(
        email=request.email,
        name=request.name,
        oab=request.oab,
        phone=request.phone,
        cpf=request.cpf,
        hashed_password=get_password_hash(request.password),
        areas=request.areas,
        cities=request.cities,
        states=request.states,
        bio=request.bio,
        is_active=True,
        is_verified=False
    )

    db.add(lawyer)
    db.commit()
    db.refresh(lawyer)

    return {"id": lawyer.id, "message": "Lawyer registered successfully"}


@app.post("/lawyers/subscribe")
async def subscribe_lawyer(
    request: LawyerSubscribeRequest,
    db: Session = Depends(get_db)
):
    """Subscribe lawyer to a plan"""
    # Get lawyer
    lawyer = db.query(Lawyer).filter(Lawyer.id == request.lawyer_id).first()
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    # Create subscription using payment service
    subscription = payment_service.create_subscription(
        db=db,
        lawyer_id=request.lawyer_id,
        plan_id=request.plan_id
    )

    return {
        "subscription_id": subscription.id,
        "status": subscription.status,
        "message": "Subscription created successfully"
    }


@app.get("/lawyers/feed")
async def get_lawyer_feed(
    lawyer_id: int,
    db: Session = Depends(get_db)
):
    """Get lead feed for lawyer"""
    # Get pending referrals for this lawyer
    referrals = db.query(Referral).filter(
        Referral.lawyer_id == lawyer_id,
        Referral.status == ReferralStatus.PENDING,
        Referral.expires_at > datetime.utcnow()
    ).all()

    feed = []
    for ref in referrals:
        case = db.query(Case).filter(Case.id == ref.case_id).first()
        if case:
            feed.append({
                "referral_id": ref.id,
                "case_id": case.id,
                "area": case.area,
                "sub_area": case.sub_area,
                "description": case.description[:200] + "...",
                "probability": case.probability,
                "sent_at": ref.sent_at,
                "expires_at": ref.expires_at
            })

    return {"leads": feed}


@app.post("/leads/assign")
async def assign_lead(
    request: LeadAssignRequest,
    db: Session = Depends(get_db)
):
    """Assign case as lead to lawyer"""
    # Get case
    case = db.query(Case).filter(Case.id == request.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Get lawyer (or find from queue)
    if request.lawyer_id:
        lawyer = db.query(Lawyer).filter(Lawyer.id == request.lawyer_id).first()
        if not lawyer:
            raise HTTPException(status_code=404, detail="Lawyer not found")
    else:
        # Use round-robin/queue
        lawyer = lead_queue.get_next_lawyer(db, case.area)
        if not lawyer:
            raise HTTPException(status_code=404, detail="No available lawyers for this area")

    # Create referral with exclusivity window (24h)
    referral = Referral(
        case_id=case.id,
        lawyer_id=lawyer.id,
        status=ReferralStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )

    db.add(referral)
    lawyer.last_lead_at = datetime.utcnow()
    lawyer.total_leads += 1
    db.commit()

    return {
        "referral_id": referral.id,
        "lawyer_id": lawyer.id,
        "expires_at": referral.expires_at,
        "message": "Lead assigned successfully"
    }


@app.post("/payments/webhook")
async def payment_webhook(
    request: PaymentWebhookRequest,
    db: Session = Depends(get_db)
):
    """Handle Mercado Pago webhook for payment confirmation"""
    try:
        # Process payment confirmation
        if request.type == "payment":
            payment_id = request.data.get("id") if request.data else None

            if payment_id:
                # Get payment from database
                payment = db.query(Payment).filter(
                    Payment.external_payment_id == str(payment_id)
                ).first()

                if payment:
                    # Update payment status
                    payment.status = "approved"
                    payment.approved_at = datetime.utcnow()

                    # Mark case as paid
                    case = db.query(Case).filter(Case.id == payment.case_id).first()
                    if case:
                        case.report_paid = True
                        case.paid_at = datetime.utcnow()
                        case.status = CaseStatus.PAID

                    db.commit()

        return {"status": "ok"}

    except Exception as e:
        print(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}


# Helper functions
def parse_analysis_response(text: str) -> dict:
    """Parse LLM response into structured data"""
    result = {
        "tipificacao": "",
        "area": "",
        "sub_area": "",
        "estrategias": "",
        "riscos": "",
        "probabilidade": ProbabilityLevel.MEDIA,
        "probabilidade_detalhes": "",
        "custos": "",
        "prazos": "",
        "checklist": [],
        "rascunho_peticao": "",
        "citacoes": [],
        "score_prob": 50.0
    }

    # Extract sections (basic regex parsing)
    # In production, use more robust parsing

    # Extract probability
    if "PROBABILIDADE:" in text or "Probabilidade:" in text:
        if "ALTA" in text.upper():
            result["probabilidade"] = ProbabilityLevel.ALTA
            result["score_prob"] = 75.0
        elif "BAIXA" in text.upper():
            result["probabilidade"] = ProbabilityLevel.BAIXA
            result["score_prob"] = 25.0
        else:
            result["probabilidade"] = ProbabilityLevel.MEDIA
            result["score_prob"] = 50.0

    # Extract citations
    citations = []
    fonte_pattern = r'<fonte>(.*?)</fonte>'
    matches = re.findall(fonte_pattern, text, re.DOTALL)

    for match in matches:
        citation = {
            "id": f"cit_{len(citations)}",
            "tipo": "lei",
            "titulo": "",
            "texto": match[:200],
            "artigo_ou_tema": None,
            "orgao": None,
            "tribunal": None,
            "data": None,
            "fonte_url": None,
            "hierarquia": 1.0
        }

        # Parse citation fields
        if "Tipo:" in match:
            tipo_match = re.search(r'Tipo:\s*(\w+)', match)
            if tipo_match:
                citation["tipo"] = tipo_match.group(1).lower()

        if "Título:" in match:
            titulo_match = re.search(r'Título:\s*(.+?)(?:\n|Órgão|Tribunal)', match)
            if titulo_match:
                citation["titulo"] = titulo_match.group(1).strip()

        citations.append(citation)

    result["citacoes"] = citations

    # Store full text in appropriate fields (simplified)
    result["tipificacao"] = text[:500]
    result["estrategias"] = text[:500]

    return result


# =============================================
# FASE 2 + FASE 3: INTEGRAÇÃO DE NOVOS ENDPOINTS
# =============================================
try:
    from endpoints_fase2_fase3 import router as fase2_fase3_router
    app.include_router(fase2_fase3_router, tags=["Fase 2 + 3"])
    print("✓ Endpoints Fase 2 + 3 integrados com sucesso")
except ImportError as e:
    print(f"⚠ Aviso: Não foi possível carregar endpoints_fase2_fase3: {e}")
except Exception as e:
    print(f"⚠ Erro ao integrar Fase 2 + 3: {e}")

# =============================================
# AUTENTICAÇÃO JWT E DASHBOARD
# =============================================
try:
    from auth_endpoints import router as auth_router
    from dashboard_endpoints import router as dashboard_router
    from dashboard_extras import router as dashboard_extras_router

    app.include_router(auth_router)
    app.include_router(dashboard_router)
    app.include_router(dashboard_extras_router)
    print("✓ Autenticação JWT e Dashboard integrados com sucesso")
except ImportError as e:
    print(f"⚠ Aviso: Não foi possível carregar auth/dashboard endpoints: {e}")
except Exception as e:
    print(f"⚠ Erro ao integrar Auth/Dashboard: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
