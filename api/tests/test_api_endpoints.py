"""
Tests for main API endpoints
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test health check returns correct status"""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"


class TestSearchEndpoint:
    """Test RAG search endpoint"""

    @patch("rag.rag_system.search")
    def test_search_success(self, mock_search, client, mock_rag_results):
        """Test successful search"""
        mock_search.return_value = mock_rag_results

        response = client.post(
            "/search",
            json={
                "query": "responsabilidade do banco em fraude PIX",
                "filtros": {"area": "consumidor"},
                "limit": 10
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["tipo"] == "lei"
        assert data[0]["score"] > 0

    @patch("rag.rag_system.search")
    def test_search_with_filters(self, mock_search, client, mock_rag_results):
        """Test search with area filter"""
        mock_search.return_value = [mock_rag_results[0]]

        response = client.post(
            "/search",
            json={
                "query": "CDC artigo 14",
                "filtros": {"area": "consumidor", "tipo": "lei"},
                "limit": 5
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    @patch("rag.rag_system.search")
    def test_search_empty_results(self, mock_search, client):
        """Test search with no results"""
        mock_search.return_value = []

        response = client.post(
            "/search",
            json={
                "query": "termo que não existe",
                "filtros": {},
                "limit": 10
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestAnalyzeCaseEndpoint:
    """Test case analysis endpoint"""

    @patch("rag.rag_system.search")
    @patch("main.llm_client.chat.completions.create")
    def test_analyze_case_success(
        self,
        mock_llm,
        mock_search,
        client,
        mock_rag_results,
        mock_llm_response
    ):
        """Test successful case analysis"""
        mock_search.return_value = mock_rag_results

        # Mock LLM response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = mock_llm_response
        mock_llm.return_value = mock_completion

        response = client.post(
            "/analyze_case",
            json={
                "descricao": "Sofri fraude PIX no valor de R$ 5.000. O banco se recusa a devolver.",
                "detalhado": False
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "tipificacao" in data
        assert "estrategias_riscos" in data
        assert "probabilidade" in data
        assert "custos_prazos" in data
        assert "checklist" in data
        assert "rascunho" in data
        assert "vigencia_base" in data

    @patch("rag.rag_system.search")
    def test_analyze_case_no_rag_results(self, mock_search, client):
        """Test case analysis when RAG finds no results"""
        mock_search.return_value = []

        response = client.post(
            "/analyze_case",
            json={
                "descricao": "Descrição muito vaga sem contexto jurídico",
                "detalhado": False
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No relevant content found" in response.json()["detail"]

    @patch("rag.rag_system.search")
    @patch("main.llm_client.chat.completions.create")
    def test_analyze_case_detalhado(
        self,
        mock_llm,
        mock_search,
        client,
        mock_rag_results,
        mock_llm_response
    ):
        """Test detailed case analysis"""
        mock_search.return_value = mock_rag_results

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = mock_llm_response
        mock_llm.return_value = mock_completion

        response = client.post(
            "/analyze_case",
            json={
                "descricao": "Análise detalhada de fraude PIX",
                "detalhado": True
            }
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify RAG was called with higher limit for detailed analysis
        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs["limit"] == 10  # Detailed mode uses limit=10


class TestGenerateReportEndpoint:
    """Test PDF report generation endpoint"""

    @patch("services.pdf.pdf_service.generate_report_pdf")
    @patch("services.payments.payment_service.create_payment")
    def test_generate_report_success(
        self,
        mock_payment,
        mock_pdf,
        client,
        db_session
    ):
        """Test successful report generation"""
        mock_pdf.return_value = "/tmp/report_123.pdf"
        mock_payment.return_value = {
            "payment_id": "pay_123",
            "payment_url": "https://payment.url/checkout",
            "status": "pending"
        }

        response = client.post(
            "/report",
            json={
                "payload": {
                    "tipificacao": "Ação indenizatória",
                    "custos_prazos": "R$ 100"
                }
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "id" in data
        assert data["pdf_path"] == "/tmp/report_123.pdf"
        assert data["paid"] is False
        assert "payment" in data["content"]

    @patch("services.pdf.pdf_service.generate_report_pdf")
    def test_generate_report_pdf_error(self, mock_pdf, client):
        """Test report generation when PDF generation fails"""
        mock_pdf.side_effect = Exception("PDF generation failed")

        response = client.post(
            "/report",
            json={
                "payload": {"test": "data"}
            }
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestComposeEndpoint:
    """Test document composition endpoint"""

    @patch("services.compose_docx.docx_composer.compose_peca")
    def test_compose_document_success(self, mock_compose, client):
        """Test successful document composition"""
        mock_compose.return_value = "/tmp/inicial_familia_alimentos_20240115.docx"

        response = client.post(
            "/compose",
            json={
                "tipo_peca": "inicial_familia_alimentos",
                "metadados": {
                    "foro": "Vara de Família e Sucessões",
                    "comarca": "São Paulo",
                    "autor": {"nome": "João Silva"},
                    "reu": {"nome": "Maria Silva"}
                },
                "carrinho_citacoes": [
                    {"tipo": "lei", "titulo": "CF/88 art. 227", "texto": "..."}
                ]
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["tipo"] == "docx"
        assert "inicial_familia_alimentos" in data["file_path"]

    @patch("services.compose_docx.docx_composer.compose_peca")
    def test_compose_document_template_not_found(self, mock_compose, client):
        """Test composition when template doesn't exist"""
        mock_compose.side_effect = FileNotFoundError("Template not found")

        response = client.post(
            "/compose",
            json={
                "tipo_peca": "template_inexistente",
                "metadados": {},
                "carrinho_citacoes": []
            }
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestPaymentWebhook:
    """Test payment webhook endpoint"""

    @patch("services.payments.payment_service.verify_webhook")
    def test_webhook_payment_approved(
        self,
        mock_verify,
        client,
        db_session,
        test_report
    ):
        """Test webhook for approved payment"""
        mock_verify.return_value = {
            "payment_id": "pay_123",
            "status": "approved",
            "metadata": {"report_id": test_report.id}
        }

        response = client.post(
            "/payments/webhook",
            json={
                "type": "payment",
                "data": {"id": "12345"}
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "processed"

        # Verify report was marked as paid
        db_session.refresh(test_report)
        assert test_report.paid is True

    @patch("services.payments.payment_service.verify_webhook")
    def test_webhook_payment_pending(self, mock_verify, client):
        """Test webhook for pending payment"""
        mock_verify.return_value = {
            "payment_id": "pay_123",
            "status": "pending",
            "metadata": {}
        }

        response = client.post(
            "/payments/webhook",
            json={"type": "payment"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "processed"

    @patch("services.payments.payment_service.verify_webhook")
    def test_webhook_invalid_signature(self, mock_verify, client):
        """Test webhook with invalid signature"""
        mock_verify.return_value = None  # Invalid signature

        response = client.post(
            "/payments/webhook",
            json={"type": "payment"}
        )

        assert response.status_code == status.HTTP_200_OK


class TestLawyerEndpoints:
    """Test lawyer-related endpoints"""

    def test_register_lawyer(self, client, db_session):
        """Test lawyer registration"""
        response = client.post(
            "/lawyers/register",
            json={
                "name": "Dr. Novo Advogado",
                "oab": "SP999999",
                "areas": ["familia", "trabalhista"],
                "city": "Rio de Janeiro"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Dr. Novo Advogado"
        assert data["oab"] == "SP999999"

    def test_get_lawyer_feed(self, client, db_session, test_lawyer, test_case):
        """Test getting lawyer feed"""
        # Update case to match lawyer's area
        test_case.area = "familia"
        test_case.status = "open"
        db_session.commit()

        response = client.get(f"/lawyers/feed?lawyer_id={test_lawyer.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_assign_lead(self, client, db_session, test_lawyer, test_case):
        """Test assigning a lead to a lawyer"""
        response = client.post(
            "/leads/assign",
            json={
                "case_id": test_case.id,
                "lawyer_id": test_lawyer.id
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "pending"
        assert "expires_at" in data


class TestSeedEndpoint:
    """Test database seeding endpoint"""

    def test_seed_database(self, client, db_session):
        """Test seeding database with initial data"""
        response = client.post("/seed")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "seeded"

        # Verify plans were created
        from models import Plan
        plans = db_session.query(Plan).all()
        assert len(plans) >= 3
