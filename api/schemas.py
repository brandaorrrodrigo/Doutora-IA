"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProbabilityLevel(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"


class AreaType(str, Enum):
    FAMILIA = "familia"
    CONSUMIDOR = "consumidor"
    BANCARIO = "bancario"
    SAUDE = "saude"
    AEREO = "aereo"


class CitationType(str, Enum):
    LEI = "lei"
    SUMULA = "sumula"
    JURIS = "juris"
    REGULATORIO = "regulatorio"
    DOUTRINA = "doutrina"


class PetitionType(str, Enum):
    INICIAL = "inicial"
    CONTESTACAO = "contestacao"
    RECURSO = "recurso"
    AGRAVO = "agravo"
    APELACAO = "apelacao"


# Request schemas
class AnalyzeCaseRequest(BaseModel):
    descricao: str = Field(..., min_length=50, max_length=5000)
    detalhado: bool = False
    user_email: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3)
    tipo: Optional[CitationType] = None
    area: Optional[AreaType] = None
    orgao: Optional[str] = None
    tribunal: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)


class Citation(BaseModel):
    id: str
    tipo: CitationType
    titulo: str
    texto: str
    artigo_ou_tema: Optional[str] = None
    orgao: Optional[str] = None
    tribunal: Optional[str] = None
    data: Optional[str] = None
    fonte_url: Optional[str] = None
    hierarquia: Optional[float] = None


class ComposeRequest(BaseModel):
    tipo_peca: PetitionType
    area: AreaType

    # Partes
    autor_nome: str
    autor_qualificacao: str
    reu_nome: str
    reu_qualificacao: str

    # Foro
    foro: str
    vara: str
    valor_causa: Optional[float] = None

    # Conteúdo
    fatos_resumo: str
    citacoes: List[Citation]
    pedidos: List[str]

    # Advogado
    advogado_nome: str
    advogado_oab: str

    # Output
    export_format: str = Field(default="docx", pattern="^(docx|pdf)$")


class ReportRequest(BaseModel):
    case_id: int


class LawyerRegisterRequest(BaseModel):
    email: EmailStr
    name: str
    oab: str
    phone: str
    cpf: str
    password: str
    areas: List[str]
    cities: List[str]
    states: List[str]
    bio: Optional[str] = None


class LawyerSubscribeRequest(BaseModel):
    lawyer_id: int
    plan_id: int
    payment_method: str = "credit_card"


class LeadAssignRequest(BaseModel):
    case_id: int
    lawyer_id: Optional[int] = None  # If None, use queue/round-robin


# Response schemas
class AnalysisResponse(BaseModel):
    case_id: Optional[int] = None
    tipificacao: str
    area: str
    sub_area: Optional[str] = None
    estrategias: str
    riscos: str
    probabilidade: ProbabilityLevel
    probabilidade_detalhes: str
    custos: str
    prazos: str
    checklist: List[str]
    rascunho_peticao: str
    citacoes: List[Citation]
    base_atualizada_em: str


class ReportResponse(BaseModel):
    report_id: int
    case_id: int
    report_url: str
    created_at: datetime


class SearchResult(BaseModel):
    results: List[Citation]
    total: int
    query: str


class ComposeResponse(BaseModel):
    document_id: str
    document_url: str
    format: str
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]


class PaymentWebhookRequest(BaseModel):
    """Mercado Pago webhook payload"""
    id: Optional[int] = None
    action: Optional[str] = None
    api_version: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    date_created: Optional[str] = None
    live_mode: Optional[bool] = None
    type: Optional[str] = None
    user_id: Optional[str] = None


class CreateCheckoutRequest(BaseModel):
    case_id: int
    provider: str = Field(default="stripe", pattern="^(stripe|mercado_pago|mercadopago)$")
    payer_email: Optional[str] = None


class CreateCheckoutResponse(BaseModel):
    payment_id: int
    checkout_url: str
    provider: str


class PaymentStatusResponse(BaseModel):
    payment_id: int
    status: str
    provider: str
    report_url: Optional[str] = None


class LawyerProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    oab: str
    areas: List[str]
    cities: List[str]
    states: List[str]
    bio: Optional[str] = None
    success_score: float
    total_leads: int
    accepted_leads: int


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    feature_search: bool
    feature_advanced_search: bool
    feature_jurimetrics: bool
    feature_leads: bool
    feature_priority_leads: bool
    feature_document_generation: bool
    feature_premium_templates: bool
    leads_per_month: int
    docs_per_month: int
    searches_per_day: int
