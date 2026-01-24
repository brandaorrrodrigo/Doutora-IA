# GUIA DE TESTES - Doutora IA

Suite completa de testes automatizados com pytest, cobertura de código e CI/CD.

---

## 🎯 Cobertura de Testes

### Módulos Testados

✅ **Autenticação (test_auth.py)**
- Registro de usuários
- Login/logout
- Validação de JWT tokens
- Hashing de senhas
- Refresh tokens

✅ **API Endpoints (test_api_endpoints.py)**
- Health check
- RAG search
- Análise de casos
- Geração de relatórios PDF
- Composição de peças DOCX
- Webhooks de pagamento
- Endpoints de advogados
- Seed de banco de dados

✅ **Serviços (test_services.py)**
- RAG system (Qdrant)
- Payment service (stub, Mercado Pago, Binance, Stripe)
- PDF generation
- DOCX composition
- Citation extraction
- Auth service (JWT, bcrypt)

---

## 🚀 Executando os Testes

### Opção 1: Script Automático (Recomendado)

#### Linux/Mac:
```bash
./scripts/run_tests.sh
```

#### Windows PowerShell:
```powershell
.\scripts\run_tests.ps1
```

### Opção 2: Pytest Direto

```bash
cd api

# Instalar dependências de teste
pip install -r requirements-test.txt

# Rodar todos os testes
pytest

# Rodar com cobertura
pytest --cov=. --cov-report=html

# Rodar testes específicos
pytest tests/test_auth.py
pytest tests/test_api_endpoints.py::TestHealthEndpoint

# Rodar em modo verbose
pytest -v

# Rodar apenas testes rápidos (excluir slow)
pytest -m "not slow"
```

---

## 📊 Cobertura de Código

### Meta: 70%+ cobertura

Após rodar os testes, visualize o relatório de cobertura:

```bash
# Abrir relatório HTML (gerado em api/htmlcov/)
open api/htmlcov/index.html  # Mac
xdg-open api/htmlcov/index.html  # Linux
start api\htmlcov\index.html  # Windows
```

### Verificar cobertura por arquivo:

```bash
pytest --cov=. --cov-report=term-missing
```

Saída exemplo:
```
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
main.py                         156      8    95%   45-47, 89
models.py                        42      0   100%
services/auth.py                 38      2    95%   67-68
services/payments.py            124     15    88%   102-115
services/compose_docx.py         89      5    94%   78-82
rag.py                          112     18    84%   145-162
-----------------------------------------------------------
TOTAL                           561     48    91%
```

---

## 🧪 Tipos de Testes

### 1. Testes Unitários

Testam funções individuais isoladamente:

```python
def test_hash_password():
    from services.auth import hash_password

    password = "my_password_123"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 0
```

### 2. Testes de Integração

Testam fluxos completos da API:

```python
def test_analyze_case_success(client, mock_rag_results):
    response = client.post(
        "/analyze_case",
        json={
            "descricao": "Sofri fraude PIX...",
            "detalhado": False
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "tipificacao" in data
```

### 3. Testes com Mocks

Simulam dependências externas (Qdrant, LLM, etc.):

```python
@patch("rag.rag_system.search")
@patch("main.llm_client.chat.completions.create")
def test_with_mocks(mock_llm, mock_search, client):
    mock_search.return_value = [...]
    mock_llm.return_value = ...

    # Test code here
```

---

## 🏷️ Marcadores (Markers)

Use marcadores para categorizar testes:

```python
@pytest.mark.slow
def test_heavy_operation():
    # Teste demorado
    pass

@pytest.mark.integration
def test_full_flow():
    # Teste de integração
    pass

@pytest.mark.requires_qdrant
def test_rag_search():
    # Requer Qdrant rodando
    pass
```

Executar apenas testes marcados:

```bash
# Rodar apenas testes rápidos
pytest -m "not slow"

# Rodar apenas testes de integração
pytest -m integration

# Rodar apenas testes unitários
pytest -m unit
```

---

## 🔧 Fixtures

Fixtures são recursos reutilizáveis entre testes:

```python
@pytest.fixture
def test_user(db_session):
    """Cria um usuário de teste"""
    user = models.User(
        email="test@example.com",
        password_hash=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_login(client, test_user):
    # Usa a fixture test_user
    response = client.post(
        "/auth/login",
        params={
            "email": test_user.email,
            "password": "password123"
        }
    )
    assert response.status_code == 200
```

### Fixtures Disponíveis:

- `client`: TestClient do FastAPI
- `db_session`: Sessão de banco de dados (SQLite in-memory)
- `test_user`: Usuário de teste
- `test_lawyer`: Advogado de teste
- `auth_headers`: Headers de autenticação JWT
- `test_case`: Caso jurídico de teste
- `test_report`: Relatório de teste
- `mock_rag_results`: Resultados simulados do RAG
- `mock_llm_response`: Resposta simulada do LLM

---

## 📝 Escrevendo Novos Testes

### Template de Teste:

```python
"""
Tests for [module name]
"""

import pytest
from unittest.mock import patch


class Test[ModuleName]:
    """Test [functionality]"""

    def test_[scenario]_success(self, client):
        """Test [scenario] succeeds"""
        response = client.post("/endpoint", json={...})

        assert response.status_code == 200
        data = response.json()
        assert data["field"] == "expected_value"

    def test_[scenario]_failure(self, client):
        """Test [scenario] fails correctly"""
        response = client.post("/endpoint", json={...})

        assert response.status_code == 400
        assert "error message" in response.json()["detail"]
```

### Boas Práticas:

1. **Nomes descritivos**: `test_login_with_invalid_password`
2. **Uma asserção por teste** (quando possível)
3. **Arrange-Act-Assert** (AAA pattern):
   ```python
   # Arrange (preparar)
   user = create_test_user()

   # Act (executar)
   response = client.post("/login", ...)

   # Assert (verificar)
   assert response.status_code == 200
   ```
4. **Isolar testes**: Cada teste deve ser independente
5. **Usar fixtures**: Reutilizar código de setup
6. **Mockar dependências externas**: LLM, Qdrant, pagamentos

---

## 🐛 Debugging Testes

### Rodar um teste específico com debug:

```bash
# Rodar com print statements visíveis
pytest -s tests/test_auth.py::TestAuthEndpoints::test_login_success

# Rodar com debugger (pdb)
pytest --pdb tests/test_auth.py

# Ver traceback completo
pytest --tb=long tests/test_auth.py
```

### Logging em testes:

```python
import logging

def test_with_logging(caplog):
    with caplog.at_level(logging.INFO):
        # Código que gera logs
        result = some_function()

    # Verificar logs
    assert "Expected log message" in caplog.text
```

---

## 📈 Métricas de Qualidade

### Coverage Badge (GitHub)

```markdown
![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)
```

### Critérios de Qualidade:

- ✅ Cobertura >= 70%
- ✅ Todos os testes passando
- ✅ Sem warnings de deprecação
- ✅ Tempo de execução < 2 minutos (todos os testes)
- ✅ Todos os endpoints críticos testados

---

## 🔄 Integração CI/CD

Os testes rodam automaticamente em:

### GitHub Actions:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pip install -r api/requirements-test.txt
    cd api && pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

### Pre-commit Hook (opcional):

```bash
# Rodar testes antes de commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
./scripts/run_tests.sh
EOF

chmod +x .git/hooks/pre-commit
```

---

## 🎯 Testes por Funcionalidade

### Autenticação:
- ✅ Registro de usuário
- ✅ Login
- ✅ Validação de token
- ✅ Refresh token
- ✅ Proteção de rotas

### RAG Search:
- ✅ Busca básica
- ✅ Busca com filtros (área, tipo)
- ✅ Ranking hierárquico
- ✅ Formatação de contexto

### Análise de Casos:
- ✅ Análise simples
- ✅ Análise detalhada
- ✅ Extração de citações
- ✅ Parsing de resposta LLM

### Pagamentos:
- ✅ Criação de pagamento (stub)
- ✅ Webhook verification
- ✅ Multi-provider (MP, Binance, Stripe)
- ✅ Signature validation

### Documentos:
- ✅ Geração de PDF
- ✅ Composição de DOCX
- ✅ Template rendering
- ✅ Citações incorporadas

---

## 🔍 Troubleshooting

### Tests failing with "ModuleNotFoundError"

```bash
# Instalar em modo development
cd api
pip install -e .
```

### Tests failing with "Database connection error"

```bash
# Verificar que está usando SQLite in-memory (configurado em conftest.py)
# Se necessário, limpar banco de dados:
rm -f test.db
```

### Coverage não está sendo calculada

```bash
# Reinstalar pytest-cov
pip uninstall pytest-cov
pip install pytest-cov
```

### Tests muito lentos

```bash
# Rodar apenas testes rápidos
pytest -m "not slow"

# Rodar em paralelo (pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

---

## ✅ Checklist de Qualidade

Antes de fazer commit/deploy:

- [ ] Todos os testes passando (`pytest`)
- [ ] Cobertura >= 70% (`pytest --cov`)
- [ ] Sem warnings (`pytest --strict-warnings`)
- [ ] Linter passando (`flake8 .`)
- [ ] Type checking (opcional: `mypy .`)
- [ ] Documentação atualizada
- [ ] Changelog atualizado

---

## 📚 Recursos

- **Pytest Docs**: https://docs.pytest.org/
- **Coverage.py**: https://coverage.readthedocs.io/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Pytest Fixtures**: https://docs.pytest.org/en/stable/fixture.html

---

**Suite de testes pronta para produção!** 🎉

Cobertura de 70%+, testes automáticos e CI/CD integrado.
