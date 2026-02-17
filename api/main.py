"""
Main FastAPI application for Doutora IA
"""
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

# Debug: Track import status
_import_status = {
    "auth_endpoints": {"loaded": False, "error": None},
    "dashboard_endpoints": {"loaded": False, "error": None},
    "dashboard_extras": {"loaded": False, "error": None},
}
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import re

from models import Base, User, Case, Lawyer, Referral, Payment, CitationLog, CaseStatus, ReferralStatus, ProbabilityLevel
from schemas import (
    AnalyzeCaseRequest, AnalysisResponse, ReportRequest, ReportResponse,
    SearchRequest, SearchResult, ComposeRequest, ComposeResponse,
    LawyerRegisterRequest, LawyerSubscribeRequest, LeadAssignRequest,
    PaymentWebhookRequest, HealthResponse, Citation, CitationType,
    CreateCheckoutRequest, CreateCheckoutResponse, PaymentStatusResponse
)
from rag import get_rag_system
from prompts import get_system_prompt, get_triagem_prompt, get_relatorio_prompt, get_compose_prompt
# from services.pdf import generate_pdf_report  # Comentado temporariamente para teste
from services.citations import CitationManager
from services.payments import PaymentService
from services.queues import LeadQueue
from services.auth import get_password_hash
from database import engine, SessionLocal, get_db

# Build version for deployment tracking
BUILD_VERSION = "2.0.0-auth"  # Change this to track deployments

# Initialize FastAPI
app = FastAPI(
    title="Doutora IA API",
    description="API for legal case analysis and document generation",
    version=BUILD_VERSION
)

# ============================================================
# CORS CONFIGURATION - SOLUÇÃO DEFINITIVA
# ============================================================

ALLOWED_ORIGINS = [
    "https://www.doutoraia.com",
    "https://doutoraia.com",
    "https://doutora-ia-landing.vercel.app",
    "https://www.nutrifitvision.com",
    "https://nutrifitvision.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3002",
    "http://127.0.0.1:3002",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

# Adiciona origens do ambiente se existirem
env_origins = os.getenv("ALLOWED_ORIGINS", "")
if env_origins:
    for origin in env_origins.split(","):
        origin = origin.strip()
        if origin and origin not in ALLOWED_ORIGINS:
            ALLOWED_ORIGINS.append(origin)

CORS_HEADERS = {
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
    "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, Origin, X-Requested-With",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Max-Age": "600",
}

def get_cors_origin(request_origin: str) -> str:
    """Retorna a origem se permitida, senão retorna a primeira origem da lista"""
    if request_origin in ALLOWED_ORIGINS:
        return request_origin
    return ALLOWED_ORIGINS[0]

class CORSHandler(BaseHTTPMiddleware):
    """Middleware CORS customizado que GARANTE headers em TODAS as respostas"""

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin", "")

        # Preflight OPTIONS - responde imediatamente
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            response.headers["Access-Control-Allow-Origin"] = get_cors_origin(origin)
            for key, value in CORS_HEADERS.items():
                response.headers[key] = value
            return response

        # Processa requisição normal
        response = await call_next(request)

        # Adiciona headers CORS em TODAS as respostas
        response.headers["Access-Control-Allow-Origin"] = get_cors_origin(origin)
        for key, value in CORS_HEADERS.items():
            if key not in response.headers:
                response.headers[key] = value

        return response

# Adiciona o middleware customizado (executa ANTES do CORSMiddleware padrão)
app.add_middleware(CORSHandler)

# Adiciona também o CORSMiddleware padrão do FastAPI como fallback
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log das origens permitidas
print(f"[CORS] Allowed origins: {ALLOWED_ORIGINS}")

# ============================================================
# HANDLERS OPTIONS EXPLÍCITOS (fallback extra)
# ============================================================

@app.options("/auth/register")
@app.options("/auth/login")
@app.options("/auth/refresh")
@app.options("/auth/me")
@app.options("/auth/forgot-password")
@app.options("/auth/reset-password")
@app.options("/auth/verify-email")
async def auth_options(request: Request):
    """Handler OPTIONS explícito para endpoints de autenticação"""
    origin = request.headers.get("origin", ALLOWED_ORIGINS[0])
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": get_cors_origin(origin),
            **CORS_HEADERS
        }
    )

@app.options("/{path:path}")
async def global_options(request: Request, path: str):
    """Handler OPTIONS global para qualquer endpoint"""
    origin = request.headers.get("origin", ALLOWED_ORIGINS[0])
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": get_cors_origin(origin),
            **CORS_HEADERS
        }
    )

# Create tables
# TEMPORARIAMENTE COMENTADO - tabelas já foram criadas via migrations
# Base.metadata.create_all(bind=engine)

# OpenAI client for vLLM
from openai import OpenAI

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:11434/v1")
VLLM_API_KEY = os.getenv("VLLM_API_KEY", "ollama")
VLLM_MODEL = os.getenv("VLLM_MODEL", "llama3.1:8b")
CORPUS_UPDATE_DATE = datetime.now().strftime('%d/%m/%Y')

llm_client = OpenAI(
    base_url=VLLM_BASE_URL,
    api_key=VLLM_API_KEY
)

# Initialize services with error handling
try:
    rag = get_rag_system()
except Exception as e:
    print(f"Warning: Could not initialize RAG system: {e}")
    rag = None

try:
    payment_service = PaymentService()
except Exception as e:
    print(f"Warning: Could not initialize payment service: {e}")
    payment_service = None

try:
    lead_queue = LeadQueue()
except Exception as e:
    print(f"Warning: Could not initialize lead queue: {e}")
    lead_queue = None

try:
    citation_manager = CitationManager()
except Exception as e:
    print(f"Warning: Could not initialize citation manager: {e}")
    citation_manager = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Create Qdrant collections if they don't exist
        if rag and rag.client:
            rag.create_collections()
            print("[OK] Qdrant collections ready")
        else:
            print("⚠ Qdrant not available - RAG features disabled")
    except Exception as e:
        print(f"Warning: Could not initialize Qdrant: {e}")


@app.get("/")
async def root():
    """Root endpoint with version info"""
    return {
        "message": "Doutora IA API",
        "version": BUILD_VERSION,
        "auth_loaded": _import_status["auth_endpoints"]["loaded"],
        "auth_error": _import_status["auth_endpoints"]["error"]
    }


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
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except:
        services["database"] = "error"

    # Check Qdrant
    try:
        if rag and rag.client:
            rag.client.get_collections()
        else:
            services["qdrant"] = "unavailable"
    except:
        services["qdrant"] = "error"

    # Check LLM
    try:
        if llm_client:
            llm_client.models.list()
        else:
            services["llm"] = "unavailable"
    except:
        services["llm"] = "error"

    status = "healthy" if all(v == "ok" for v in services.values()) else "degraded"

    return HealthResponse(
        status=status,
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services=services
    )


@app.get("/debug/imports")
async def debug_imports():
    """Debug endpoint to check auth import status"""
    return {
        "imports": _import_status,
        "routes_count": len(app.routes),
        "routes": [r.path for r in app.routes if hasattr(r, 'path')]
    }


@app.post("/analyze_case", response_model=AnalysisResponse)
async def analyze_case(
    request: AnalyzeCaseRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a case and provide free triage or detailed analysis
    """
    # Get RAG context
    context = ""
    if rag and rag.client:
        try:
            context = rag.get_context_for_case(
                descricao=request.descricao,
                limit_per_type=5 if request.detalhado else 3
            )
        except Exception as e:
            print(f"Warning: RAG error: {e}")
            context = ""

    # Build prompt
    prompt = get_triagem_prompt(
        descricao=request.descricao,
        contexto_rag=context,
        data_atualizacao=CORPUS_UPDATE_DATE
    )

    # Call LLM
    try:
        response = llm_client.chat.completions.create(
            model=VLLM_MODEL,
            messages=[
                {"role": "system", "content": get_system_prompt(CORPUS_UPDATE_DATE)},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4096
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

    # Normalize citation type to valid enum values
    _CITATION_TYPE_MAP = {
        "lei": "lei", "legislação": "lei", "legislacao": "lei",
        "sumula": "sumula", "súmula": "sumula",
        "juris": "juris", "jurisprudência": "juris", "jurisprudencia": "juris",
        "regulatorio": "regulatorio", "regulatório": "regulatorio",
        "doutrina": "doutrina",
    }

    # Convert citations to schema
    citations_schema = [
        Citation(
            id=cit.get("id", ""),
            tipo=CitationType(_CITATION_TYPE_MAP.get(cit.get("tipo", "lei").lower(), "lei")),
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
        # report_path = generate_pdf_report(case, CORPUS_UPDATE_DATE)  # Comentado temporariamente
        report_path = "/reports/temp.pdf"  # Mockado para teste
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
            model=VLLM_MODEL,
            messages=[
                {"role": "system", "content": get_system_prompt(CORPUS_UPDATE_DATE)},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4096
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


@app.post("/payments/create-checkout", response_model=CreateCheckoutResponse)
async def create_checkout(
    request: CreateCheckoutRequest,
    db: Session = Depends(get_db)
):
    """Create a payment checkout session (Stripe or Mercado Pago)"""
    if not payment_service:
        raise HTTPException(status_code=503, detail="Payment service unavailable")

    case = db.query(Case).filter(Case.id == request.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if case.report_paid:
        raise HTTPException(status_code=400, detail="Report already paid")

    try:
        # Normalize provider name
        provider = request.provider
        if provider == "mercadopago":
            provider = "mercado_pago"

        payment = payment_service.create_payment(
            db=db,
            case_id=request.case_id,
            amount=7.0,
            description="Relatório Premium Doutora IA",
            payer_email=request.payer_email,
            provider=provider
        )

        return CreateCheckoutResponse(
            payment_id=payment.id,
            checkout_url=payment.payment_url,
            provider=payment.provider
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating checkout: {str(e)}")


@app.get("/payments/{payment_id}/status", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """Check payment status and return report URL if paid"""
    if not payment_service:
        raise HTTPException(status_code=503, detail="Payment service unavailable")

    status = payment_service.check_payment_status(db, payment_id)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Payment not found")

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    report_url = None
    if status == "approved" and payment and payment.case_id:
        case = db.query(Case).filter(Case.id == payment.case_id).first()
        if case and case.report_url:
            report_url = case.report_url

    return PaymentStatusResponse(
        payment_id=payment_id,
        status=status,
        provider=payment.provider if payment else "unknown",
        report_url=report_url
    )


@app.post("/payments/webhook")
async def payment_webhook(
    request: PaymentWebhookRequest,
    db: Session = Depends(get_db)
):
    """Handle Mercado Pago webhook for payment confirmation"""
    try:
        if request.type == "payment":
            payment_id = request.data.get("id") if request.data else None

            if payment_id:
                payment = db.query(Payment).filter(
                    Payment.external_payment_id == str(payment_id)
                ).first()

                if payment:
                    payment.status = "approved"
                    payment.approved_at = datetime.utcnow()

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


@app.post("/payments/webhook/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook with signature verification"""
    if not payment_service:
        raise HTTPException(status_code=503, detail="Payment service unavailable")

    try:
        raw_body = await request.body()
        payload = json.loads(raw_body)
        headers = dict(request.headers)

        result = payment_service.process_webhook(
            db=db,
            payload=payload,
            headers=headers,
            provider="stripe",
            raw_body=raw_body
        )

        return {"status": "ok", "processed": result is not None}

    except Exception as e:
        print(f"Stripe webhook error: {e}")
        return {"status": "error", "message": str(e)}


# Helper functions
def parse_analysis_response(text: str) -> dict:
    """Parse LLM response into structured data by extracting numbered sections"""
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

    # Define section headers to split on
    section_patterns = [
        (r'(?:1\.\s*\*?\*?)?TIPIFICA[ÇC][ÃA]O\s*(?:DA\s*CAUSA)?\*?\*?', 'tipificacao'),
        (r'(?:2\.\s*\*?\*?)?ESTRAT[ÉE]GIAS?\s*(?:E\s*RISCOS?)?\*?\*?', 'estrategias'),
        (r'(?:3\.\s*\*?\*?)?PROBABILIDADE\s*(?:DE\s*[ÊE]XITO)?\*?\*?', 'probabilidade_section'),
        (r'(?:4\.\s*\*?\*?)?CUSTOS?\s*(?:E\s*PRAZOS?)?\*?\*?', 'custos_prazos'),
        (r'(?:5\.\s*\*?\*?)?CHECKLIST\s*(?:DE\s*DOCUMENTOS?)?\*?\*?', 'checklist_section'),
        (r'(?:6\.\s*\*?\*?)?RASCUNHO\s*(?:DE\s*PETI[ÇC][ÃA]O)?\*?\*?', 'rascunho'),
        (r'(?:7\.\s*\*?\*?)?CITA[ÇC][ÕO]ES?\s*(?:DA\s*BASE)?\*?\*?', 'citacoes_section'),
        (r'(?:8\.\s*\*?\*?)?BASE\s*ATUALIZADA\*?\*?', 'base'),
    ]

    # Find all section positions
    sections = []
    for pattern, name in section_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            sections.append((match.start(), match.end(), name))

    sections.sort(key=lambda x: x[0])

    # Extract text between sections
    section_texts = {}
    for i, (start, end, name) in enumerate(sections):
        next_start = sections[i + 1][0] if i + 1 < len(sections) else len(text)
        section_texts[name] = text[end:next_start].strip().strip('*').strip(':').strip()

    # Fill result fields
    result["tipificacao"] = section_texts.get("tipificacao", text)

    estrategias_text = section_texts.get("estrategias", "")
    # Split estrategias and riscos if both are in same section
    riscos_match = re.search(r'\*?\*?(?:Riscos?|RISCOS?|Pontos?\s*de\s*aten[çc][ãa]o)\*?\*?', estrategias_text)
    if riscos_match:
        result["estrategias"] = estrategias_text[:riscos_match.start()].strip()
        result["riscos"] = estrategias_text[riscos_match.start():].strip()
    else:
        result["estrategias"] = estrategias_text

    # Probabilidade - look for "Classificação: X" first, then fallback
    prob_text = section_texts.get("probabilidade_section", "")
    classif_match = re.search(r'classifica[çc][ãa]o[:\s]+(\w+)', prob_text, re.IGNORECASE)
    if classif_match:
        classif = classif_match.group(1).upper()
    else:
        # Fallback: check first line only
        first_line = prob_text.split('\n')[0].upper() if prob_text else ""
        classif = first_line

    if "ALTA" in classif:
        result["probabilidade"] = ProbabilityLevel.ALTA
        result["score_prob"] = 75.0
    elif "BAIXA" in classif:
        result["probabilidade"] = ProbabilityLevel.BAIXA
        result["score_prob"] = 25.0
    else:
        result["probabilidade"] = ProbabilityLevel.MEDIA
        result["score_prob"] = 50.0
    result["probabilidade_detalhes"] = prob_text

    # Custos e Prazos
    custos_text = section_texts.get("custos_prazos", "")
    prazos_match = re.search(r'\*?\*?(?:Prazos?|PRAZOS?|Tramita[çc][ãa]o)\*?\*?', custos_text)
    if prazos_match:
        result["custos"] = custos_text[:prazos_match.start()].strip()
        result["prazos"] = custos_text[prazos_match.start():].strip()
    else:
        result["custos"] = custos_text

    # Checklist
    checklist_text = section_texts.get("checklist_section", "")
    items = re.findall(r'[-•*]\s*(.+)', checklist_text)
    if not items:
        items = re.findall(r'\d+[.)]\s*(.+)', checklist_text)
    result["checklist"] = [item.strip() for item in items if item.strip()]

    # Rascunho de petição
    result["rascunho_peticao"] = section_texts.get("rascunho", "")

    # Citations from <fonte> tags
    citations = []
    fonte_pattern = r'<fonte>(.*?)</fonte>'
    matches = re.findall(fonte_pattern, text, re.DOTALL)

    for match in matches:
        citation = {
            "id": f"cit_{len(citations)}",
            "tipo": "lei",
            "titulo": "",
            "texto": match.strip(),
            "artigo_ou_tema": None,
            "orgao": None,
            "tribunal": None,
            "data": None,
            "fonte_url": None,
            "hierarquia": 1.0
        }

        if "Tipo:" in match:
            tipo_match = re.search(r'Tipo:\s*(\w+)', match)
            if tipo_match:
                citation["tipo"] = tipo_match.group(1).lower()

        if "Título:" in match or "Titulo:" in match:
            titulo_match = re.search(r'T[ií]tulo:\s*(.+?)(?:\n|$)', match)
            if titulo_match:
                citation["titulo"] = titulo_match.group(1).strip()

        if "Trecho relevante:" in match:
            trecho_match = re.search(r'Trecho relevante:\s*(.+?)(?:\n|$)', match, re.DOTALL)
            if trecho_match:
                citation["texto"] = trecho_match.group(1).strip()

        if "Órgão" in match or "Tribunal:" in match:
            org_match = re.search(r'(?:Órgão|Tribunal)[/:]?\s*(.+?)(?:\n|$)', match)
            if org_match:
                citation["tribunal"] = org_match.group(1).strip()

        citations.append(citation)

    result["citacoes"] = citations

    # If no sections were found, use the full text as tipificacao
    if not sections:
        result["tipificacao"] = text

    # Detect area from tipificacao
    area_lower = result["tipificacao"].lower()
    if "trabalh" in area_lower:
        result["area"] = "Trabalhista"
    elif "consum" in area_lower:
        result["area"] = "Consumidor"
    elif "famíli" in area_lower or "alimento" in area_lower or "divórcio" in area_lower:
        result["area"] = "Família"
    elif "bancári" in area_lower or "financei" in area_lower:
        result["area"] = "Bancário"
    elif "saúde" in area_lower or "plano" in area_lower:
        result["area"] = "Saúde"
    elif "aére" in area_lower or "voo" in area_lower or "vôo" in area_lower:
        result["area"] = "Aéreo"

    return result


# =============================================
# FASE 2 + FASE 3: INTEGRAÇÃO DE NOVOS ENDPOINTS
# =============================================
try:
    from endpoints_fase2_fase3 import router as fase2_fase3_router
    app.include_router(fase2_fase3_router, tags=["Fase 2 + 3"])
    print("[OK] Endpoints Fase 2 + 3 integrados com sucesso")
except ImportError as e:
    print(f"⚠ Aviso: Não foi possível carregar endpoints_fase2_fase3: {e}")
except Exception as e:
    print(f"⚠ Erro ao integrar Fase 2 + 3: {e}")

# =============================================
# AUTENTICAÇÃO JWT E DASHBOARD
# =============================================
try:
    from auth_endpoints import router as auth_router
    _import_status["auth_endpoints"]["loaded"] = True
    app.include_router(auth_router)
    print("[OK] auth_endpoints carregado com sucesso")
except Exception as e:
    import traceback
    _import_status["auth_endpoints"]["error"] = f"{type(e).__name__}: {str(e)}"
    print(f"⚠ ERRO auth_endpoints: {e}")
    traceback.print_exc()

try:
    from dashboard_endpoints import router as dashboard_router
    _import_status["dashboard_endpoints"]["loaded"] = True
    app.include_router(dashboard_router)
    print("[OK] dashboard_endpoints carregado com sucesso")
except Exception as e:
    import traceback
    _import_status["dashboard_endpoints"]["error"] = f"{type(e).__name__}: {str(e)}"
    print(f"⚠ ERRO dashboard_endpoints: {e}")
    traceback.print_exc()

try:
    from dashboard_extras import router as dashboard_extras_router
    _import_status["dashboard_extras"]["loaded"] = True
    app.include_router(dashboard_extras_router)
    print("[OK] dashboard_extras carregado com sucesso")
except Exception as e:
    import traceback
    _import_status["dashboard_extras"]["error"] = f"{type(e).__name__}: {str(e)}"
    print(f"⚠ ERRO dashboard_extras: {e}")
    traceback.print_exc()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
