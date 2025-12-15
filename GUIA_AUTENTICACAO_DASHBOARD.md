# 🔐 GUIA DE AUTENTICAÇÃO JWT + DASHBOARD

Sistema completo de autenticação JWT e dashboard para advogados.

---

## ✅ O QUE FOI IMPLEMENTADO

### **Autenticação JWT**
- ✅ Login com email/senha
- ✅ Registro de novo advogado
- ✅ Refresh token (renovação automática)
- ✅ Verificação de email
- ✅ Recuperação de senha
- ✅ Logout
- ✅ Proteção de rotas
- ✅ Tokens com expiração configurável

### **Dashboard Completo**
- ✅ Visão geral com 8 métricas principais
- ✅ Gráficos interativos (Chart.js)
- ✅ Alertas urgentes em tempo real
- ✅ Histórico de leads
- ✅ Funil de conversão
- ✅ Prazos próximos
- ✅ Performance score
- ✅ Auto-refresh a cada 5 minutos

---

## 📦 ARQUIVOS CRIADOS

### Backend (Python)
1. **`api/services/jwt_auth.py`** - Serviço de autenticação JWT
2. **`api/services/dashboard.py`** - Serviço de métricas e KPIs
3. **`api/auth_endpoints.py`** - Endpoints de autenticação
4. **`api/dashboard_endpoints.py`** - Endpoints do dashboard
5. **`migrations/003_auth_fields.sql`** - Migration com tabelas de auth

### Frontend (HTML/JS)
6. **`web/public/login.html`** - Página de login/registro
7. **`web/public/login.js`** - Lógica de autenticação
8. **`web/public/dashboard.html`** - Dashboard principal
9. **`web/public/dashboard.js`** - Lógica do dashboard

### Documentação
10. **`GUIA_AUTENTICACAO_DASHBOARD.md`** - Este arquivo

---

## 🚀 COMO USAR

### 1️⃣ Executar Migration do Banco

```bash
# Conectar ao banco
docker compose exec db psql -U postgres -d doutora

# Executar migration
\i /docker-entrypoint-initdb.d/003_auth_fields.sql

# Verificar tabelas criadas
\dt

# Sair
\q
```

**Ou via script:**
```bash
docker compose exec -T db psql -U postgres -d doutora < migrations/003_auth_fields.sql
```

### 2️⃣ Reiniciar API

```bash
docker compose restart api
```

Verifique os logs:
```bash
docker compose logs -f api
```

Você deve ver:
```
✓ Autenticação JWT e Dashboard integrados com sucesso
```

### 3️⃣ Testar Autenticação

Acesse: `http://localhost:3000/login.html`

**Criar nova conta:**
1. Clique na aba "Cadastro"
2. Preencha os dados
3. Clique em "Criar Conta"
4. Será redirecionado para o dashboard

**Fazer login:**
1. Digite email e senha
2. Clique em "Entrar"
3. Será redirecionado para o dashboard

### 4️⃣ Acessar Dashboard

Após login: `http://localhost:3000/dashboard.html`

Você verá:
- 8 cards com métricas principais
- Gráfico de leads por dia (30 dias)
- Gráfico de distribuição por área
- Funil de conversão
- Prazos urgentes
- Histórico de leads

---

## 🔌 ENDPOINTS DA API

### **Autenticação** (`/auth`)

#### POST `/auth/register`
Criar nova conta de advogado

**Body:**
```json
{
  "email": "advogado@example.com",
  "password": "senha123",
  "name": "Dr. João Silva",
  "oab": "OAB/SP 123456",
  "phone": "+5511999999999",
  "areas": ["familia", "consumidor"],
  "cities": ["São Paulo"],
  "states": ["SP"]
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

#### POST `/auth/login`
Fazer login

**Body:**
```json
{
  "email": "advogado@example.com",
  "password": "senha123"
}
```

**Response:**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

#### POST `/auth/refresh`
Renovar access token

**Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

#### GET `/auth/me`
Obter dados do usuário autenticado

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "email": "advogado@example.com",
  "name": "Dr. João Silva",
  "oab": "OAB/SP 123456",
  "phone": "+5511999999999",
  "areas": ["familia", "consumidor"],
  "rating": 4.8,
  "total_ratings": 23,
  "is_verified": true,
  "created_at": "2024-12-09T10:00:00Z"
}
```

---

#### POST `/auth/verify-email`
Verificar email com token

**Body:**
```json
{
  "token": "token_recebido_por_email"
}
```

---

#### POST `/auth/forgot-password`
Solicitar reset de senha

**Body:**
```json
{
  "email": "advogado@example.com"
}
```

---

#### POST `/auth/reset-password`
Resetar senha com token

**Body:**
```json
{
  "token": "token_recebido_por_email",
  "new_password": "novaSenha123"
}
```

---

#### POST `/auth/change-password`
Alterar senha (autenticado)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body:**
```json
{
  "old_password": "senhaAtual",
  "new_password": "novaSenha123"
}
```

---

### **Dashboard** (`/dashboard`)

**TODOS os endpoints requerem autenticação (Bearer token)**

#### GET `/dashboard/overview`
Visão geral - métricas principais

**Response:**
```json
{
  "leads_pendentes": 5,
  "leads_aceitos_mes": 12,
  "leads_rejeitados_mes": 3,
  "taxa_conversao": 80.0,
  "valor_estimado_mes": 45000.00,
  "prazos_proximos": 3,
  "agendamentos_hoje": 2,
  "notificacoes_nao_lidas": 7,
  "avaliacao_media": 4.8,
  "total_avaliacoes": 23
}
```

---

#### GET `/dashboard/performance`
Score de performance

**Response:**
```json
{
  "score_geral": 85,
  "tempo_resposta_medio": 4.5,
  "taxa_aceitacao": 75.5,
  "avaliacao_media": 4.8,
  "casos_resolvidos": 23
}
```

---

#### GET `/dashboard/leads/history?days=30&status=accepted`
Histórico de leads

**Parâmetros:**
- `days` (opcional): Últimos N dias (padrão: 30)
- `status` (opcional): pending, accepted, rejected

**Response:**
```json
[
  {
    "id": 1,
    "case_id": 10,
    "area": "familia",
    "sub_area": "divorcio",
    "description": "Cliente deseja divórcio consensual...",
    "probability": "alta",
    "estimated_fees": 5000.00,
    "status": "accepted",
    "sent_at": "2024-12-08T10:00:00Z",
    "accepted_at": "2024-12-08T14:30:00Z"
  }
]
```

---

#### GET `/dashboard/charts/leads-by-day?days=30`
Dados para gráfico de leads por dia

**Response:**
```json
[
  {
    "data": "2024-12-01",
    "total": 5,
    "aceitos": 3,
    "rejeitados": 2
  },
  ...
]
```

---

#### GET `/dashboard/charts/leads-by-area?days=30`
Distribuição por área

**Response:**
```json
[
  {
    "area": "familia",
    "total": 15,
    "percentual": 45.5
  },
  {
    "area": "consumidor",
    "total": 10,
    "percentual": 30.3
  }
]
```

---

#### GET `/dashboard/charts/conversion-funnel?days=30`
Funil de conversão

**Response:**
```json
{
  "recebidos": 100,
  "visualizados": 85,
  "aceitos": 60,
  "convertidos": 45,
  "taxa_aceitacao": 60.0,
  "taxa_conversao": 75.0
}
```

---

#### GET `/dashboard/prazos/urgentes?dias=5`
Prazos urgentes

**Response:**
```json
[
  {
    "id": 1,
    "processo_numero": "1234567-89.2024.8.26.0100",
    "processo_id": 10,
    "tipo": "recurso",
    "data_limite": "2024-12-15",
    "dias_restantes": 2,
    "prioridade": "alta"
  }
]
```

---

#### GET `/dashboard/full`
Dashboard completo (todos os dados)

**Response:** Objeto com todas as seções

---

## 🔒 SEGURANÇA

### Configuração de Tokens

Edite as constantes em `api/services/jwt_auth.py`:

```python
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hora
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 dias
```

**IMPORTANTE:**
- ⚠️ Altere `SECRET_KEY` em produção
- ⚠️ Use uma chave longa e aleatória
- ⚠️ Nunca comite a chave real no Git

**Gerar SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Proteção de Rotas

**Exemplo de endpoint protegido:**

```python
from services.jwt_auth import get_current_lawyer

@router.get("/protected")
async def protected_route(lawyer = Depends(get_current_lawyer)):
    return {
        "message": f"Olá {lawyer.name}!",
        "lawyer_id": lawyer.id
    }
```

### Headers de Autenticação

**Formato:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Refresh Token Strategy

1. **Access Token** expira em 1 hora
2. **Refresh Token** expira em 30 dias
3. Cliente deve renovar automaticamente quando access token expirar
4. Se refresh token expirar, usuário precisa fazer login novamente

---

## 🎨 PERSONALIZAR DASHBOARD

### Alterar Cores

Edite em `dashboard.html`:

```css
:root {
    --primary: #1a5490;    /* Azul principal */
    --success: #28a745;    /* Verde sucesso */
    --warning: #ffc107;    /* Amarelo aviso */
    --danger: #dc3545;     /* Vermelho perigo */
}
```

### Adicionar Novo Card de Métrica

```javascript
// Em dashboard.js, função renderStats()
<div class="stat-card primary">
    <div class="icon">
        <i class="fas fa-icon-name"></i>
    </div>
    <div class="value">${overview.sua_metrica}</div>
    <div class="label">Sua Métrica</div>
</div>
```

### Adicionar Novo Gráfico

```javascript
// 1. Adicionar canvas no HTML
<canvas id="meuGrafico"></canvas>

// 2. Criar função de renderização
function renderMeuGrafico(data) {
    const ctx = document.getElementById('meuGrafico').getContext('2d');
    new Chart(ctx, {
        type: 'bar',  // bar, line, pie, doughnut
        data: { /* seus dados */ },
        options: { /* suas opções */ }
    });
}

// 3. Chamar na função loadDashboard()
renderMeuGrafico(data.meus_dados);
```

---

## 🧪 TESTES

### Teste Manual via CURL

**1. Registrar:**
```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "senha123",
    "name": "Dr. Teste",
    "oab": "OAB/SP 999999",
    "phone": "+5511999999999",
    "areas": ["familia"],
    "cities": ["São Paulo"],
    "states": ["SP"]
  }'
```

**2. Login:**
```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "senha123"
  }'
```

Copie o `access_token` da resposta.

**3. Acessar Endpoint Protegido:**
```bash
curl http://localhost:8080/auth/me \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

**4. Dashboard:**
```bash
curl http://localhost:8080/dashboard/overview \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Teste via Interface Web

1. Acesse `http://localhost:3000/login.html`
2. Crie uma conta
3. Faça login
4. Verifique o dashboard
5. Abra Console do navegador (F12)
6. Verifique chamadas de API na aba "Network"

---

## 📊 TABELAS NO BANCO DE DADOS

### `refresh_tokens`
Armazena refresh tokens para controle de sessões

- `id` - ID único
- `lawyer_id` ou `user_id` - Dono do token
- `token_id` - JTI do JWT
- `token_hash` - Hash do token
- `issued_at` - Data de emissão
- `expires_at` - Data de expiração
- `is_revoked` - Se foi revogado
- `user_agent`, `ip_address` - Metadata

### `auth_logs`
Log de eventos de autenticação para auditoria

- `id` - ID único
- `lawyer_id` ou `user_id` - Usuário
- `event_type` - login, logout, register, etc
- `success` - Se foi bem-sucedido
- `error_message` - Erro se houver
- `user_agent`, `ip_address` - Metadata
- `created_at` - Timestamp

### Views

**`active_sessions`** - Sessões ativas no momento

---

## 🔧 TROUBLESHOOTING

### "Token inválido ou expirado"

**Causa:** Access token expirou (1 hora)

**Solução:** Use refresh token para renovar

```javascript
// Exemplo de renovação automática
async function refreshAccessToken() {
    const refreshToken = localStorage.getItem('refresh_token');

    const response = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ refresh_token: refreshToken })
    });

    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
}
```

---

### Dashboard não carrega dados

**Verificar:**
1. Token válido no localStorage
2. API rodando (`docker compose ps`)
3. Console do navegador (F12) - erros JS?
4. Network tab - chamadas de API falhando?

---

### Erro "Module jwt_auth not found"

**Causa:** API não reiniciada após adicionar arquivos

**Solução:**
```bash
docker compose restart api
docker compose logs -f api
```

---

### Migration falha

**Verificar:**
```bash
# Ver tabelas existentes
docker compose exec db psql -U postgres -d doutora -c "\dt"

# Ver estrutura de lawyers
docker compose exec db psql -U postgres -d doutora -c "\d lawyers"
```

**Reexecutar:**
```bash
docker compose exec -T db psql -U postgres -d doutora < migrations/003_auth_fields.sql
```

---

## 📈 PRÓXIMOS PASSOS

### Melhorias Sugeridas

1. **Email Real**
   - Integrar com SMTP (Gmail, SendGrid)
   - Enviar emails de verificação e reset de senha

2. **OAuth/Social Login**
   - Login com Google
   - Login com Facebook
   - Login com LinkedIn

3. **2FA (Autenticação de Dois Fatores)**
   - SMS via Twilio
   - Google Authenticator

4. **Rate Limiting**
   - Limitar tentativas de login
   - Prevenir brute force

5. **Session Management**
   - Ver sessões ativas
   - Revogar sessões remotamente
   - Logout de todos os dispositivos

6. **Analytics no Dashboard**
   - Mais gráficos
   - Exportar relatórios PDF
   - Comparação mês a mês

---

## 🎉 CONCLUSÃO

Sistema completo de **Autenticação JWT** e **Dashboard** implementado!

**Features:**
- ✅ Login/Registro seguro
- ✅ Tokens com refresh automático
- ✅ Dashboard com 8 métricas
- ✅ 4 gráficos interativos
- ✅ Alertas em tempo real
- ✅ Design responsivo e moderno

**Pronto para:**
- Teste local
- Deploy em staging
- Integração com Fase 2 + 3

---

**Documentação criada em:** 2024-12-09
**Versão:** 1.0
**Sistema:** Doutora IA - Autenticação + Dashboard
