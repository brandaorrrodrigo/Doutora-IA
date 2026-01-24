"""
Tests for service modules
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os


class TestAuthService:
    """Test authentication service"""

    def test_create_access_token(self):
        """Test JWT token creation"""
        from services.auth import create_access_token, verify_token

        data = {
            "sub": "123",
            "email": "test@example.com",
            "role": "user"
        }

        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token
        payload = verify_token(token)
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "user"

    def test_verify_invalid_token(self):
        """Test verifying invalid token"""
        from services.auth import verify_token

        result = verify_token("invalid_token_string")
        assert result is None

    def test_hash_password(self):
        """Test password hashing"""
        from services.auth import hash_password

        password = "my_password_123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        from services.auth import hash_password, verify_password

        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        from services.auth import hash_password, verify_password

        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password("wrong_password", hashed) is False


class TestPaymentService:
    """Test payment service"""

    def test_stub_payment_creation(self):
        """Test creating stub payment"""
        from services.payments import payment_service

        payment = payment_service.create_payment(
            amount_cents=700,
            description="Test Report",
            metadata={"report_id": 123}
        )

        assert payment["provider"] == "stub"
        assert payment["amount_cents"] == 700
        assert payment["status"] == "pending"
        assert "payment_id" in payment
        assert "payment_url" in payment

    def test_stub_webhook_verification(self):
        """Test verifying stub webhook"""
        from services.payments import payment_service

        payload = {
            "payment_id": "stub_123",
            "metadata": {"report_id": 123}
        }

        result = payment_service.verify_webhook(payload)

        assert result is not None
        assert result["status"] == "approved"
        assert result["metadata"]["report_id"] == 123


class TestMultiPaymentService:
    """Test multi-provider payment service"""

    def test_provider_detection(self):
        """Test auto-detection of payment providers"""
        from services.payments_multi import MultiPaymentService

        service = MultiPaymentService()
        assert isinstance(service.providers, list)
        assert len(service.providers) >= 1  # At least stub

    def test_stub_payment_creation(self):
        """Test creating payment in stub mode"""
        from services.payments_multi import multi_payment_service

        payment = multi_payment_service.create_payment(
            amount_cents=2900,
            description="Assinatura Mensal",
            metadata={"user_id": 123},
            provider="stub"
        )

        assert "stub" in payment["provider"]
        assert payment["amount_cents"] == 2900
        assert "payment_url" in payment

    def test_provider_selection_brazil(self):
        """Test provider selection for Brazilian email"""
        from services.payments_multi import MultiPaymentService

        service = MultiPaymentService()
        provider = service._select_best_provider(
            amount_cents=700,
            payer_email="user@gmail.com.br"
        )

        # Should prefer Mercado Pago for .br emails
        assert provider in ["mercado_pago", "stub", "binance_pay", "stripe"]

    def test_get_provider_info(self):
        """Test getting provider information"""
        from services.payments_multi import multi_payment_service

        info = multi_payment_service.get_provider_info("mercado_pago")

        assert info["name"] == "Mercado Pago"
        assert "BRL" in info["currencies"]
        assert info["region"] == "Latin America"


class TestCitationService:
    """Test citation extraction service"""

    def test_extract_citations(self):
        """Test extracting citations from LLM output"""
        from services.citations import citation_service

        text = """
        Conforme <fonte tipo="lei" id="cdc_art_14">CDC Artigo 14</fonte>,
        o fornecedor responde objetivamente.

        Jurisprudência: <fonte tipo="juris" id="stj_resp_123">STJ REsp 123</fonte>.
        """

        citations = citation_service.extract_citations(text)

        assert len(citations) >= 2
        assert any(c["id"] == "cdc_art_14" for c in citations)
        assert any(c["tipo"] == "juris" for c in citations)

    def test_extract_citations_empty(self):
        """Test extracting citations from text without citations"""
        from services.citations import citation_service

        text = "Este texto não contém citações formatadas."
        citations = citation_service.extract_citations(text)

        assert len(citations) == 0


class TestPDFService:
    """Test PDF generation service"""

    @patch("services.pdf.weasyprint")
    def test_generate_report_pdf(self, mock_weasyprint):
        """Test PDF generation"""
        from services.pdf import pdf_service

        content = {
            "tipificacao": "Ação indenizatória",
            "probabilidade": "Alta (80-90%)",
            "custos_prazos": "R$ 100, 12 meses"
        }

        # Mock WeasyPrint
        mock_html = MagicMock()
        mock_weasyprint.HTML.return_value = mock_html

        pdf_path = pdf_service.generate_report_pdf(content, case_id=123)

        assert isinstance(pdf_path, str)
        assert pdf_path.endswith(".pdf")
        assert "report_" in pdf_path


class TestDocxComposer:
    """Test DOCX composition service"""

    def test_prepare_context(self):
        """Test context preparation for template rendering"""
        from services.compose_docx import docx_composer

        metadados = {
            "foro": "1ª Vara de Família",
            "comarca": "São Paulo",
            "autor": {"nome": "João Silva"},
            "reu": {"nome": "Maria Silva"}
        }

        citacoes = [
            {"tipo": "lei", "titulo": "CF/88 art. 227", "texto": "..."},
            {"tipo": "juris", "titulo": "STJ REsp 123", "ementa": "..."},
            {"tipo": "regulatorio", "titulo": "ANS 123", "texto": "..."}
        ]

        context = docx_composer._prepare_context(metadados, citacoes)

        assert context["foro"] == "1ª Vara de Família"
        assert "fundamentos_legais" in context
        assert "jurisprudencia" in context
        assert "regulacao_ans" in context
        assert "data" in context

        # Check citation separation
        assert len(context["fundamentos_legais"]) == 1
        assert len(context["jurisprudencia"]) == 1
        assert len(context["regulacao_ans"]) == 1

    @patch("services.compose_docx.DocxTemplate")
    def test_compose_peca(self, mock_docx_template):
        """Test composing legal document"""
        from services.compose_docx import docx_composer

        # Mock template
        mock_template = MagicMock()
        mock_docx_template.return_value = mock_template

        # Create template file
        template_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "templates",
            "inicial_familia_alimentos.docx"
        )

        os.makedirs(os.path.dirname(template_path), exist_ok=True)

        # Mock template existence
        with patch("os.path.exists", return_value=True):
            output_path = docx_composer.compose_peca(
                tipo_peca="inicial_familia_alimentos",
                metadados={
                    "foro": "Vara de Família",
                    "comarca": "São Paulo"
                },
                carrinho_citacoes=[]
            )

        assert isinstance(output_path, str)
        assert ".docx" in output_path


class TestRAGSystem:
    """Test RAG (Retrieval-Augmented Generation) system"""

    @patch("rag.rag_system.qdrant_client.search")
    def test_search(self, mock_search):
        """Test RAG search functionality"""
        from rag import rag_system

        # Mock Qdrant response
        mock_search.return_value = [
            MagicMock(
                id="cdc_art_14",
                score=0.95,
                payload={
                    "tipo": "lei",
                    "area": "consumidor",
                    "titulo": "CDC Artigo 14",
                    "texto": "...",
                    "vigencia_fim": None
                }
            )
        ]

        results = rag_system.search(
            query="responsabilidade do fornecedor",
            filtros={"area": "consumidor"},
            limit=5
        )

        assert len(results) > 0
        assert results[0]["tipo"] == "lei"
        assert results[0]["score"] > 0

    def test_format_rag_context(self):
        """Test formatting RAG results for LLM context"""
        from prompts import format_rag_context

        rag_results = [
            {
                "tipo": "lei",
                "titulo": "CDC Artigo 14",
                "texto": "O fornecedor responde...",
                "score": 0.95
            },
            {
                "tipo": "juris",
                "titulo": "STJ REsp 123",
                "texto": "Responsabilidade objetiva...",
                "score": 0.90
            }
        ]

        context = format_rag_context(rag_results)

        assert isinstance(context, str)
        assert "CDC Artigo 14" in context
        assert "STJ REsp 123" in context
        assert "lei" in context.lower()


class TestPrompts:
    """Test prompt templates"""

    def test_system_prompt_exists(self):
        """Test that system prompt is defined"""
        from prompts import SYSTEM_PROMPT

        assert isinstance(SYSTEM_PROMPT, str)
        assert len(SYSTEM_PROMPT) > 0
        assert "advogado" in SYSTEM_PROMPT.lower() or "jurídico" in SYSTEM_PROMPT.lower()

    def test_report_template_exists(self):
        """Test that report template is defined"""
        from prompts import REPORT_TEMPLATE

        assert isinstance(REPORT_TEMPLATE, str)
        assert "{descricao}" in REPORT_TEMPLATE
        assert "{rag_context}" in REPORT_TEMPLATE

    def test_get_current_date(self):
        """Test getting current date in Portuguese"""
        from prompts import get_current_date

        date_str = get_current_date()

        assert isinstance(date_str, str)
        assert "/" in date_str or "de" in date_str
