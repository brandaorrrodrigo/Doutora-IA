"""
Database models for Doutora IA
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Numeric, DateTime, Text,
    ForeignKey, JSON, Enum as SQLEnum, ARRAY
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class CaseStatus(str, enum.Enum):
    PENDING = "pending"
    ANALYZED = "analyzed"
    PAID = "paid"
    REFERRED = "referred"
    CLOSED = "closed"


class ReferralStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ProbabilityLevel(str, enum.Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255))
    phone = Column(String(50))
    cpf = Column(String(14), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    cases = relationship("Case", back_populates="user")


class Lawyer(Base):
    __tablename__ = "lawyers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    oab = Column(String(50), unique=True, index=True, nullable=False)
    phone = Column(String(50))
    cpf = Column(String(14), unique=True)
    hashed_password = Column(String(255))

    # Professional info
    areas = Column(ARRAY(String), default=[])  # familia, consumidor, bancario, saude, aereo
    cities = Column(ARRAY(String), default=[])
    states = Column(ARRAY(String), default=[])
    bio = Column(Text)

    # Performance metrics
    success_score = Column(Numeric(5, 2), default=0.0)  # 0-100
    total_leads = Column(Integer, default=0)
    accepted_leads = Column(Integer, default=0)
    rejected_leads = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_lead_at = Column(DateTime(timezone=True))

    # Relationships
    subscription = relationship("Subscription", back_populates="lawyer", uselist=False)
    referrals = relationship("Referral", back_populates="lawyer")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # Pesquisa, Leads, Redacao, Pro, Full
    price = Column(Numeric(10, 2), nullable=False)

    # Features (boolean flags)
    feature_search = Column(Boolean, default=False)
    feature_advanced_search = Column(Boolean, default=False)
    feature_jurimetrics = Column(Boolean, default=False)
    feature_leads = Column(Boolean, default=False)
    feature_priority_leads = Column(Boolean, default=False)
    feature_document_generation = Column(Boolean, default=False)
    feature_premium_templates = Column(Boolean, default=False)

    # Limits
    leads_per_month = Column(Integer, default=0)
    docs_per_month = Column(Integer, default=0)
    searches_per_day = Column(Integer, default=0)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    lawyer_id = Column(Integer, ForeignKey("lawyers.id"), unique=True, nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)

    status = Column(String(50), default="active")  # active, cancelled, suspended
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))

    # Usage tracking
    leads_used = Column(Integer, default=0)
    docs_used = Column(Integer, default=0)
    searches_today = Column(Integer, default=0)
    last_search_date = Column(DateTime(timezone=True))

    # Payment info
    external_subscription_id = Column(String(255))  # Mercado Pago subscription ID

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    lawyer = relationship("Lawyer", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Case data
    description = Column(Text, nullable=False)
    area = Column(String(100))  # familia, consumidor, bancario, saude, aereo
    sub_area = Column(String(255))  # pensao, guarda, divorcio, pix, plano_saude, etc

    # Analysis results
    typification = Column(Text)
    strategies = Column(Text)
    risks = Column(Text)
    probability = Column(SQLEnum(ProbabilityLevel))
    cost_estimate = Column(Text)
    timeline_estimate = Column(Text)
    checklist = Column(JSON)
    draft_petition = Column(Text)
    citations = Column(JSON)  # Array of citation objects

    # Scoring
    score_prob = Column(Numeric(5, 2))  # Internal probability score 0-100

    # Status
    status = Column(SQLEnum(CaseStatus), default=CaseStatus.PENDING)
    report_paid = Column(Boolean, default=False)
    report_url = Column(String(500))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    analyzed_at = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="cases")
    referral = relationship("Referral", back_populates="case", uselist=False)
    payment = relationship("Payment", back_populates="case", uselist=False)


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), unique=True, nullable=False)
    lawyer_id = Column(Integer, ForeignKey("lawyers.id"), nullable=False)

    status = Column(SQLEnum(ReferralStatus), default=ReferralStatus.PENDING)

    # Exclusivity window
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))  # 24-48h window
    responded_at = Column(DateTime(timezone=True))

    # Lawyer response
    response_message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    case = relationship("Case", back_populates="referral")
    lawyer = relationship("Lawyer", back_populates="referrals")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), unique=True)

    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="BRL")

    # Status
    status = Column(String(50), default="pending")  # pending, approved, rejected, cancelled

    # External IDs
    external_payment_id = Column(String(255), unique=True)  # Payment provider ID
    provider = Column(String(50), default="stub")  # mercado_pago, stripe, binance_pay, stub
    payment_url = Column(Text)  # Checkout URL
    pix_qr_code = Column(Text)
    pix_qr_code_base64 = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True))

    # Relationships
    case = relationship("Case", back_populates="payment")


class CitationLog(Base):
    __tablename__ = "citations_log"

    id = Column(Integer, primary_key=True, index=True)

    # Source
    source_type = Column(String(50))  # report, document, search
    source_id = Column(Integer)  # ID of case, document, etc

    # Citation details
    citation_id = Column(String(255), nullable=False)  # ID from Qdrant
    citation_type = Column(String(50))  # lei, sumula, juris, regulatorio, doutrina
    citation_title = Column(String(500))
    citation_text = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CostTable(Base):
    __tablename__ = "cost_table"

    id = Column(Integer, primary_key=True, index=True)

    state = Column(String(2), nullable=False)  # UF
    area = Column(String(100), nullable=False)

    # Costs
    court_fees_jec = Column(Numeric(10, 2))
    court_fees_comum = Column(Numeric(10, 2))
    lawyer_fees_min = Column(Numeric(10, 2))
    lawyer_fees_max = Column(Numeric(10, 2))

    # Timeline (in days)
    timeline_jec_min = Column(Integer)
    timeline_jec_max = Column(Integer)
    timeline_comum_min = Column(Integer)
    timeline_comum_max = Column(Integer)

    notes = Column(Text)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)

    # Event data
    event_type = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    lawyer_id = Column(Integer, ForeignKey("lawyers.id"), index=True)

    # Event properties
    properties = Column(JSON)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
