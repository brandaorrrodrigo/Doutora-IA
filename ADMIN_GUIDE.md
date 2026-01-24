# GUIA DO DASHBOARD ADMIN - Doutora IA

Sistema completo de analytics e gestão para **controle total do negócio**.

---

## 🎯 O QUE FOI IMPLEMENTADO

### 9 Categorias de Endpoints Admin

✅ **Analytics Overview** - Visão geral em tempo real
- Total de usuários, advogados, casos, leads
- Receita total, diária, mensal
- Taxa de conversão de leads
- Taxa de pagamento de relatórios
- Crescimento de usuários

✅ **Activity Timeline** - Linha do tempo de atividade
- Gráfico diário de usuários, casos, receita
- Configurável (7, 30, 90 dias)
- Dados formatados para charts (Chart.js, Recharts)

✅ **System Metrics** - Saúde do sistema
- Cache hit rate e economia
- Email delivery rate
- API response time
- Database status

✅ **User Management** - Gestão de usuários
- Listar todos os usuários (com filtros)
- Ver detalhes de usuário específico
- Suspender/banir usuários
- Busca por nome/email

✅ **Lawyer Management** - Gestão de advogados
- Listar advogados (com filtros)
- Aprovar novos cadastros (verificação OAB)
- Suspender advogados
- Filtrar por área de atuação

✅ **Payment Management** - Gestão de pagamentos
- Listar todas as transações
- Filtrar por status (approved, pending, failed)
- Ver detalhes de pagamento

✅ **Revenue Analytics** - Analytics de receita
- MRR (Monthly Recurring Revenue)
- Receita por mês (últimos 6 meses)
- Gráficos de crescimento

✅ **Cache Management** - Gerenciar cache
- Ver estatísticas de cache
- Limpar cache (tudo ou por pattern)
- Monitorar economia com LLM

✅ **Logs** - Logs do sistema
- Placeholder para visualização de logs
- TODO: Implementar com ELK ou CloudWatch

---

## 🚀 COMO USAR

### 1. Configurar Token de Admin

```bash
# .env
ADMIN_SECRET_TOKEN=gere_token_aleatorio_seguro_aqui_123xyz
```

**IMPORTANTE**: Use token forte em produção!

```bash
# Gerar token seguro
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output: ZXJhc3VyZS1hZG1pbi10b2tlbi0xMjM0NTY3ODkwYWJjZGVm
```

---

### 2. Acessar Endpoints Admin

Todos os endpoints requerem parâmetro `admin_token`:

```bash
# Overview geral
curl "http://localhost:8000/admin/analytics/overview?admin_token=SEU_TOKEN"

# Atividade dos últimos 30 dias
curl "http://localhost:8000/admin/analytics/activity?days=30&admin_token=SEU_TOKEN"

# Métricas do sistema
curl "http://localhost:8000/admin/analytics/system?admin_token=SEU_TOKEN"
```

---

## 📊 ENDPOINTS DETALHADOS

### Analytics Overview

**Endpoint**: `GET /admin/analytics/overview`

**Response Example**:
```json
{
  "users": {
    "total": 1250,
    "today": 12,
    "week": 87,
    "growth_rate": 7.5
  },
  "lawyers": {
    "total": 45,
    "active": 38,
    "inactive": 7,
    "activation_rate": 84.44
  },
  "cases": {
    "total": 3420,
    "today": 23,
    "open": 145,
    "closed": 3275
  },
  "revenue": {
    "total": 24500.00,
    "today": 210.00,
    "month": 4800.00,
    "average_order_value": 70.00
  },
  "leads": {
    "total": 892,
    "pending": 34,
    "converted": 312,
    "conversion_rate": 35.0
  },
  "reports": {
    "total": 350,
    "paid": 280,
    "free": 70,
    "payment_rate": 80.0
  },
  "timestamp": "2024-01-15T14:30:00Z"
}
```

**Use cases**:
- Dashboard principal
- KPIs em tempo real
- Monitorar crescimento

---

### Activity Timeline

**Endpoint**: `GET /admin/analytics/activity?days=30`

**Parameters**:
- `days`: 1-90 (default: 7)

**Response Example**:
```json
{
  "days": 7,
  "data": [
    {
      "date": "2024-01-08",
      "users": 15,
      "cases": 42,
      "revenue": 350.00
    },
    {
      "date": "2024-01-09",
      "users": 18,
      "cases": 38,
      "revenue": 280.00
    },
    // ...
  ]
}
```

**Use cases**:
- Gráficos de linha/área
- Identificar tendências
- Comparar períodos

**Exemplo com Chart.js**:
```javascript
const response = await fetch('/admin/analytics/activity?days=30&admin_token=xxx');
const data = await response.json();

new Chart(ctx, {
  type: 'line',
  data: {
    labels: data.data.map(d => d.date),
    datasets: [
      {
        label: 'Receita (R$)',
        data: data.data.map(d => d.revenue),
        borderColor: 'rgb(75, 192, 192)'
      },
      {
        label: 'Casos',
        data: data.data.map(d => d.cases),
        borderColor: 'rgb(255, 99, 132)'
      }
    ]
  }
});
```

---

### System Metrics

**Endpoint**: `GET /admin/analytics/system`

**Response Example**:
```json
{
  "cache": {
    "enabled": true,
    "performance": {
      "hit_rate": "73.5%",
      "total_hits": 1523,
      "total_misses": 548
    },
    "storage": {
      "total_keys": 892,
      "memory_used": "12.4M"
    },
    "estimated_savings": {
      "llm_calls_saved": 1523,
      "cost_saved_usd": 15.23,
      "message": "Saved ~$15.23 in LLM costs"
    }
  },
  "email": {
    "provider": "resend",
    "enabled": true,
    "sent_today": 145,
    "delivery_rate": 99.2,
    "open_rate": 42.5
  },
  "api": {
    "uptime_percentage": 99.9,
    "avg_response_time_ms": 250,
    "requests_today": 2341,
    "errors_today": 3
  },
  "database": {
    "connection_pool": "healthy",
    "query_performance": "normal"
  },
  "timestamp": "2024-01-15T14:30:00Z"
}
```

**Use cases**:
- Monitorar saúde do sistema
- Alertas de performance
- Identificar gargalos

---

### User Management

#### List Users

**Endpoint**: `GET /admin/users`

**Parameters**:
- `skip`: Offset (default: 0)
- `limit`: Limit (default: 50, max: 100)
- `status`: Filter by status (active, suspended, banned)
- `search`: Search by name or email

**Example**:
```bash
# Listar usuários ativos, págna 2
curl "http://localhost:8000/admin/users?status=active&skip=50&limit=50&admin_token=xxx"

# Buscar por email
curl "http://localhost:8000/admin/users?search=joao@exemplo.com&admin_token=xxx"
```

#### Get User Details

**Endpoint**: `GET /admin/users/{user_id}`

**Example**:
```bash
curl "http://localhost:8000/admin/users/123?admin_token=xxx"
```

#### Update User Status

**Endpoint**: `PATCH /admin/users/{user_id}/status?status=suspended`

**Allowed statuses**: `active`, `suspended`, `banned`

**Example**:
```bash
# Suspender usuário
curl -X PATCH "http://localhost:8000/admin/users/123/status?status=suspended&admin_token=xxx"

# Reativar usuário
curl -X PATCH "http://localhost:8000/admin/users/123/status?status=active&admin_token=xxx"
```

**Use cases**:
- Moderar usuários
- Suspender por violação de termos
- Banir spammers

---

### Lawyer Management

#### List Lawyers

**Endpoint**: `GET /admin/lawyers`

**Parameters**:
- `skip`, `limit`: Pagination
- `status`: Filter by status
- `area`: Filter by area (familia, trabalhista, etc)

**Example**:
```bash
# Advogados pendentes de aprovação
curl "http://localhost:8000/admin/lawyers?status=pending&admin_token=xxx"

# Advogados de direito de família
curl "http://localhost:8000/admin/lawyers?area=familia&admin_token=xxx"
```

#### Approve Lawyer

**Endpoint**: `PATCH /admin/lawyers/{lawyer_id}/approve`

**Example**:
```bash
# Aprovar após verificar OAB
curl -X PATCH "http://localhost:8000/admin/lawyers/456/approve?admin_token=xxx"
```

**Response**:
```json
{
  "lawyer_id": 456,
  "status": "active",
  "approved_at": "2024-01-15T14:30:00Z"
}
```

**Use cases**:
- Verificar cadastros de advogados
- Validar OAB antes de aprovar
- Manter qualidade do marketplace

---

### Payment Management

**Endpoint**: `GET /admin/payments`

**Parameters**:
- `skip`, `limit`: Pagination
- `status`: Filter by status (approved, pending, failed, refunded)

**Example**:
```bash
# Listar pagamentos aprovados
curl "http://localhost:8000/admin/payments?status=approved&limit=100&admin_token=xxx"

# Listar falhas de pagamento (para análise)
curl "http://localhost:8000/admin/payments?status=failed&admin_token=xxx"
```

**Response**:
```json
{
  "total": 350,
  "payments": [
    {
      "id": 1,
      "amount": 70.00,
      "status": "approved",
      "provider": "mercado_pago",
      "external_id": "pay_abc123",
      "metadata": {"report_id": 123},
      "created_at": "2024-01-15T14:30:00Z"
    },
    // ...
  ]
}
```

---

### Revenue Analytics

**Endpoint**: `GET /admin/revenue/mrr`

**Response Example**:
```json
{
  "mrr": 4500.00,
  "by_month": [
    {
      "month": "2023-08",
      "revenue": 3200.00
    },
    {
      "month": "2023-09",
      "revenue": 3800.00
    },
    {
      "month": "2023-10",
      "revenue": 4200.00
    },
    {
      "month": "2023-11",
      "revenue": 4800.00
    },
    {
      "month": "2023-12",
      "revenue": 5100.00
    },
    {
      "month": "2024-01",
      "revenue": 4900.00
    }
  ]
}
```

**Métricas explicadas**:
- **MRR**: Average monthly revenue (últimos 3 meses)
- **by_month**: Receita real por mês (últimos 6 meses)

**Use cases**:
- Projeções financeiras
- Análise de crescimento
- Relatórios para investidores

---

### Cache Management

#### Get Cache Stats

**Endpoint**: `GET /admin/cache/stats`

(Mesmo que `/cache/stats` público)

#### Clear Cache

**Endpoint**: `POST /admin/cache/clear?pattern=*`

**Parameters**:
- `pattern`: Pattern to clear (default: `*` = all)
  - `*`: Clear all
  - `search`: Clear only search cache
  - `analysis`: Clear only analysis cache

**Example**:
```bash
# Limpar tudo
curl -X POST "http://localhost:8000/admin/cache/clear?pattern=*&admin_token=xxx"

# Limpar apenas análises
curl -X POST "http://localhost:8000/admin/cache/clear?pattern=analysis&admin_token=xxx"
```

**Use cases**:
- Forçar refresh após atualização de dados RAG
- Liberar memória
- Debugging

---

## 🔐 SEGURANÇA

### Autenticação Atual (MVP)

Atualmente usa token simples via query parameter:

```
GET /admin/analytics/overview?admin_token=xxx
```

**Limitações**:
- ❌ Token aparece em logs
- ❌ Sem expiração
- ❌ Sem permissões granulares
- ⚠️ OK para MVP, mas melhorar em produção

### Melhorias Recomendadas (Produção)

#### 1. JWT-based Admin Auth

```python
from fastapi.security import HTTPBearer
from jose import jwt

security = HTTPBearer()

def verify_admin_jwt(credentials: HTTPAuthCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        if payload.get("role") != "admin":
            raise HTTPException(403, "Not an admin")

        return payload

    except:
        raise HTTPException(403, "Invalid admin token")

# Usar
@router.get("/admin/analytics/overview")
async def get_overview(admin: dict = Depends(verify_admin_jwt)):
    # ...
```

#### 2. Role-Based Access Control (RBAC)

```python
# Diferentes níveis de admin
ADMIN_ROLES = {
    "super_admin": ["*"],  # Acesso total
    "finance_admin": ["/admin/payments", "/admin/revenue"],  # Só finanças
    "support_admin": ["/admin/users", "/admin/lawyers"],  # Só usuários
    "read_only": ["GET /admin/*"]  # Só leitura
}

def require_permission(permission: str):
    def dependency(admin: dict = Depends(verify_admin_jwt)):
        user_permissions = ADMIN_ROLES.get(admin["role"], [])

        if "*" not in user_permissions and permission not in user_permissions:
            raise HTTPException(403, "Insufficient permissions")

        return admin

    return dependency

# Usar
@router.post("/admin/users/{user_id}/ban")
async def ban_user(admin = Depends(require_permission("users:ban"))):
    # ...
```

#### 3. Audit Logging

```python
def log_admin_action(action: str, admin: dict, details: dict):
    db.add(AdminAuditLog(
        admin_id=admin["id"],
        action=action,
        details=details,
        ip_address=request.client.host,
        timestamp=datetime.utcnow()
    ))
    db.commit()

# Usar
@router.patch("/admin/users/{user_id}/ban")
async def ban_user(user_id: int, admin = Depends(verify_admin)):
    # ... ban logic ...

    log_admin_action(
        action="user_banned",
        admin=admin,
        details={"user_id": user_id, "reason": "spam"}
    )
```

#### 4. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/admin/analytics/overview")
@limiter.limit("60/minute")  # Max 60 requests/min
async def get_overview(request: Request, admin = Depends(verify_admin)):
    # ...
```

---

## 📈 FRONTEND INTEGRATION

### React Dashboard Example

```javascript
import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function AdminDashboard() {
  const [overview, setOverview] = useState(null);
  const [activity, setActivity] = useState(null);

  const ADMIN_TOKEN = process.env.REACT_APP_ADMIN_TOKEN;

  useEffect(() => {
    // Fetch overview
    fetch(`/admin/analytics/overview?admin_token=${ADMIN_TOKEN}`)
      .then(res => res.json())
      .then(setOverview);

    // Fetch activity
    fetch(`/admin/analytics/activity?days=30&admin_token=${ADMIN_TOKEN}`)
      .then(res => res.json())
      .then(setActivity);
  }, []);

  if (!overview || !activity) return <div>Loading...</div>;

  return (
    <div className="admin-dashboard">
      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <h3>Total Usuários</h3>
          <div className="kpi-value">{overview.users.total}</div>
          <div className="kpi-growth">+{overview.users.growth_rate}% esta semana</div>
        </div>

        <div className="kpi-card">
          <h3>Receita Mensal</h3>
          <div className="kpi-value">R$ {overview.revenue.month.toLocaleString()}</div>
        </div>

        <div className="kpi-card">
          <h3>Taxa de Conversão</h3>
          <div className="kpi-value">{overview.leads.conversion_rate}%</div>
        </div>

        <div className="kpi-card">
          <h3>Advogados Ativos</h3>
          <div className="kpi-value">{overview.lawyers.active}</div>
        </div>
      </div>

      {/* Activity Chart */}
      <div className="chart-container">
        <h2>Atividade dos Últimos 30 Dias</h2>
        <LineChart width={800} height={400} data={activity.data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="revenue" stroke="#8884d8" name="Receita (R$)" />
          <Line type="monotone" dataKey="cases" stroke="#82ca9d" name="Casos" />
          <Line type="monotone" dataKey="users" stroke="#ffc658" name="Usuários" />
        </LineChart>
      </div>
    </div>
  );
}

export default AdminDashboard;
```

---

## 🛠️ TROUBLESHOOTING

### 403 Forbidden

```bash
# Token inválido ou ausente
# Verificar .env
cat .env | grep ADMIN_SECRET_TOKEN

# Usar token correto
curl "http://localhost:8000/admin/analytics/overview?admin_token=CORRETO_TOKEN_AQUI"
```

### Dados incorretos / zerados

```bash
# 1. Verificar se DB está populado
docker-compose exec api python -c "
from db import get_db
from models import User, Case, Payment
db = next(get_db())
print('Users:', db.query(User).count())
print('Cases:', db.query(Case).count())
print('Payments:', db.query(Payment).count())
"

# 2. Seed database se necessário
curl -X POST "http://localhost:8000/seed"
```

### Performance lenta

```bash
# Adicionar índices no banco
# migrations/add_admin_indexes.sql

CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_cases_created_at ON cases(created_at);
CREATE INDEX idx_payments_created_at ON payments(created_at);
CREATE INDEX idx_payments_status ON payments(status);
```

---

## 📊 MÉTRICAS IMPORTANTES

### KPIs de Negócio

1. **User Growth Rate**: % crescimento de usuários
   - Meta: > 10%/mês
   - Alerta se < 5%/mês

2. **Lead Conversion Rate**: % leads convertidos
   - Meta: > 30%
   - Alerta se < 20%

3. **Payment Rate**: % de relatórios pagos
   - Meta: > 70%
   - Alerta se < 50%

4. **MRR (Monthly Recurring Revenue)**: Receita mensal recorrente
   - Meta: Crescimento contínuo
   - Alerta se queda > 10%

5. **Lawyer Activation Rate**: % advogados ativos
   - Meta: > 80%
   - Alerta se < 60%

### KPIs Técnicos

1. **Cache Hit Rate**: % requests do cache
   - Meta: > 60%
   - Alerta se < 40%

2. **API Response Time**: Tempo médio de resposta
   - Meta: < 500ms
   - Alerta se > 1000ms

3. **Email Delivery Rate**: % emails entregues
   - Meta: > 99%
   - Alerta se < 95%

4. **Uptime**: % de tempo online
   - Meta: > 99.9%
   - Alerta se < 99%

---

## 🚀 ROADMAP FUTURO

### Melhorias Planejadas

- [ ] **Dashboard visual completo**
  - Frontend React/Vue com gráficos
  - Real-time updates com WebSockets
  - Mobile-responsive

- [ ] **Alertas automáticos**
  - Email quando métrica crítica cai
  - Slack/Discord webhooks
  - SMS para emergências

- [ ] **Relatórios automáticos**
  - PDF semanal para stakeholders
  - CSV export de dados
  - Agendamento de relatórios

- [ ] **A/B Testing interno**
  - Testar features com % de usuários
  - Medir impacto de mudanças

- [ ] **User Journey Analytics**
  - Funil de conversão visual
  - Identificar drop-off points
  - Heatmaps de uso

- [ ] **Integração com ferramentas externas**
  - Google Analytics
  - Mixpanel / Amplitude
  - Datadog / New Relic

---

**Dashboard Admin implementado e funcionando! 🎛️**

Controle total do negócio em tempo real.

**Próximo passo**: Criar frontend visual e configurar alertas! 🚀
