"""
Pytest configuration and fixtures for Doutora IA tests
"""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment
os.environ["ENV"] = "test"
os.environ["PAYMENTS_PROVIDER"] = "stub"
os.environ["QDRANT_URL"] = "http://localhost:6333"

from main import app
from db import Base, get_db
import models

# Test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    from services.auth import hash_password

    user = models.User(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_lawyer(db_session):
    """Create a test lawyer"""
    from services.auth import hash_password

    user = models.User(
        email="lawyer@example.com",
        password_hash=hash_password("lawyerpass123"),
        role="lawyer"
    )
    db_session.add(user)
    db_session.commit()

    lawyer = models.Lawyer(
        user_id=user.id,
        name="Dr. Test Lawyer",
        oab="SP123456",
        areas=["familia", "consumidor"],
        city="São Paulo",
        active=True
    )
    db_session.add(lawyer)
    db_session.commit()
    db_session.refresh(lawyer)
    return lawyer


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    response = client.post(
        "/auth/login",
        params={"email": test_user.email, "password": "testpassword123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_case(db_session, test_user):
    """Create a test case"""
    case = models.Case(
        user_id=test_user.id,
        area="familia",
        descricao="Preciso solicitar pensão alimentícia para meu filho",
        status="open"
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)
    return case


@pytest.fixture
def test_report(db_session, test_case):
    """Create a test report"""
    report = models.Report(
        case_id=test_case.id,
        pdf_path="/tmp/test_report.pdf",
        paid=False,
        content={"test": "data"}
    )
    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)
    return report


@pytest.fixture
def test_plan(db_session):
    """Create a test plan"""
    plan = models.Plan(
        code="test_plan",
        name="Test Plan",
        price_cents=2900,
        features={"search": True, "reports": 10},
        active=True
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    return plan


@pytest.fixture
def mock_rag_results():
    """Mock RAG search results"""
    return [
        {
            "id": "cdc_art_14",
            "tipo": "lei",
            "area": "consumidor",
            "titulo": "CDC Artigo 14",
            "texto": "O fornecedor de serviços responde, independentemente de culpa...",
            "score": 0.95,
            "colecao": "legis",
            "vigencia_fim": None
        },
        {
            "id": "stj_tema_106",
            "tipo": "tema",
            "area": "consumidor",
            "titulo": "STJ Tema 106 - Fraude PIX",
            "texto": "Responsabilidade objetiva das instituições financeiras...",
            "score": 0.90,
            "colecao": "temas"
        }
    ]


@pytest.fixture
def mock_llm_response():
    """Mock LLM response"""
    return """
## 1. TIPIFICAÇÃO

Trata-se de ação indenizatória decorrente de fraude em transferência PIX.

## 2. ESTRATÉGIAS E RISCOS

Estratégia principal: Responsabilidade objetiva do banco (CDC art. 14).

## 3. PROBABILIDADE DE ÊXITO

Alta probabilidade (80-90%) devido à jurisprudência consolidada.

## 4. CUSTOS E PRAZOS

Prazo estimado: 12-18 meses
Custos: Isento no JEC

## 5. CHECKLIST DOCUMENTAL

- Comprovante da transferência PIX
- Boletim de ocorrência
- Protocolos de atendimento bancário
- Extratos bancários

## 6. RASCUNHO DE PETIÇÃO

EXMO. SR. DR. JUIZ DE DIREITO...
"""


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    yield
    # Reset any global state if needed
