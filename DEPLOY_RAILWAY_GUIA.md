# Deploy em Railway - Guia Completo

## 🚀 Visão Geral

Railway é uma plataforma de deployment moderno para aplicações backend. Vamos fazer deploy das 2 APIs em Railway:

- **API Questões** (porta 8042): Busca, filtros e respostas de 37k questões
- **API Mapas** (porta 8041): Mapas mentais e flashcards

**Tempo estimado**: 45 minutos até estar em produção ✅

---

## 📋 Pré-requisitos

- [x] Conta Railway (gratuita em https://railway.app)
- [x] Git instalado
- [x] GitHub account conectada ao Railway
- [x] Projeto local pronto com PostgreSQL
- [x] Script de explicações completado (37k questões com comentários)

---

## 🔑 PASSO 1: Criar Projeto Railway

### 1.1 Fazer Login

```bash
npm install -g @railway/cli

railway login
```

Abrirá navegador para autenticar. Clique em "Authorize" → Confirme acesso ao GitHub

### 1.2 Criar Novo Projeto

```bash
cd D:\doutora-ia

# Opção A: Via CLI
railway init

# Opção B: Via Dashboard
# 1. Acesse https://railway.app
# 2. Dashboard → New Project
# 3. Selecione "Deploy from GitHub"
```

**Se usar CLI, escolha opções:**
```
? Project name: doutora-ia-backend
? Environment: production
```

---

## 🗄️ PASSO 2: Configurar PostgreSQL no Railway

### 2.1 Adicionar Banco de Dados

```bash
railway service add
```

Escolha: **PostgreSQL 14**

### 2.2 Verificar Conexão

```bash
railway variables list

# Deve mostrar:
# DATABASE_URL = postgresql://user:pass@host:5432/doutora
```

### 2.3 Migrar Dados do Local

```bash
# Fazer dump do PostgreSQL local
docker exec doutora_postgres pg_dump -U doutora_user -d doutora > backup_37k.sql

# Restaurar no Railway (via conexão remota)
# Será feito após criar serviço
```

---

## 🐍 PASSO 3: Fazer Deploy da API Backend

### 3.1 Estrutura de Diretórios (Railway esperado)

```
D:\doutora-ia\
├── api/
│   ├── main.py              ← API principal FastAPI
│   ├── requirements.txt
│   └── Dockerfile
├── backend/
│   ├── api_questoes.py      ← Endpoint questões
│   ├── api_mapas_flashcards.py ← Endpoint mapas
│   └── requirements.txt
├── railway.json             ← Configuração Railway
└── .env.railway            ← Variáveis de ambiente
```

### 3.2 Criar Dockerfile para API

**Arquivo: D:\doutora-ia\api\Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY api/requirements.txt backend/requirements.txt ./

# Instalar Python packages
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r backend/requirements.txt && \
    pip install uvicorn gunicorn

# Copiar código
COPY api/ ./api/
COPY backend/ ./backend/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Executar API
CMD ["gunicorn", "-w 4", "-k uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:${PORT:-8080}", "api.main:app"]
```

### 3.3 Atualizar requirements.txt

**Arquivo: D:\doutora-ia\api\requirements.txt**

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
requests==2.31.0
python-dotenv==1.0.0
cors==1.0.1
gunicorn==21.2.0
```

### 3.4 Fazer Deploy

```bash
# Opção A: Via CLI
cd D:\doutora-ia
railway up

# Opção B: Via GitHub (automático)
# 1. Push para GitHub: git add . && git commit -m "Deploy prep" && git push
# 2. Railway Dashboard → Connect GitHub → Select repository
# 3. Configure branch e pasta (api/)
# 4. Deploy automático ao fazer push

# Verificar status
railway status
railway logs
```

### 3.5 Configurar Variáveis de Ambiente

```bash
railway variables set \
  ENVIRONMENT=production \
  API_KEY=your_secure_key_here \
  OLLAMA_URL=http://ollama:11434 \
  LLM_MODEL_CHAT=llama3.1:8b-instruct \
  CORS_ORIGINS=https://doutora-ia-landing.vercel.app,https://www.doutoraia.com
```

**Ou via Dashboard:**
1. Railway → Seu Project → Settings
2. Environment Variables → Add Variable
3. Copie tudo de `.env.railway`

---

## 🔗 PASSO 4: Restaurar Dados PostgreSQL

### 4.1 Conectar ao Banco Railway

```bash
# Obter connection string
railway variables get DATABASE_URL

# Conectar via psql
psql "postgresql://user:pass@host:5432/doutora"
```

### 4.2 Restaurar Backup (37k questões)

```bash
# Via Railway CLI
railway run psql -U user -d doutora < backup_37k.sql

# Ou via Docker local (forwardar porta)
railway tunnel -p 5432:5432

# Em outro terminal
PGPASSWORD=pass psql -h localhost -U user -d doutora < backup_37k.sql
```

### 4.3 Verificar Dados

```bash
# Conectar ao banco
railway run psql -U user -d doutora

# No psql:
SELECT COUNT(*) FROM questoes; -- Deve retornar ~37000
SELECT COUNT(*) FROM questoes WHERE comentario IS NOT NULL; -- Deve retornar ~13700+
```

---

## ✅ PASSO 5: Testar Endpoints em Produção

### 5.1 Obter URL da API

```bash
railway domains
# ou via Dashboard → Deployments → Open URL
```

**URLs esperadas:**
- `https://api-questoes-prod.railway.app` (questões)
- `https://api-mapas-prod.railway.app` (mapas)

### 5.2 Testar Endpoints

```bash
# Buscar questões
curl -X GET "https://api-questoes-prod.railway.app/questoes/busca?termo=direito"

# Buscar por tópico
curl -X GET "https://api-questoes-prod.railway.app/questoes/topico/civil"

# Buscar mapas
curl -X GET "https://api-mapas-prod.railway.app/mapas/mentais"

# Health check
curl https://api-questoes-prod.railway.app/health
```

### 5.3 Verificar Logs

```bash
railway logs --follow

# Ou via Dashboard → Deployments → Logs
```

---

## 🚨 Possíveis Problemas

### ❌ Erro: "PostgreSQL connection refused"

**Solução:**
```bash
# Verificar DATABASE_URL
railway variables get DATABASE_URL

# Conectar com credentials corretos
psql "$DATABASE_URL"
```

### ❌ Erro: "Port already in use"

**Solução:**
```bash
railway restart
```

### ❌ Erro: "Module not found: api.main"

**Solução:**
- Verificar estrutura de diretórios
- Arquivo `api/main.py` deve existir
- Verificar imports em Dockerfile

### ❌ Timeout ao conectar Ollama

**Solução:**
- Ollama precisa rodar também em Railway ou em host externo
- Para MVP, usar mock responses
- Configurar `OLLAMA_URL=http://ollama-external:11434`

---

## 📊 Monitoramento em Produção

### Verificar Status

```bash
railway status

# Output:
# ✓ Project: doutora-ia-backend
# ✓ API Questões: Deployed (37k records)
# ✓ API Mapas: Deployed (412 mapas)
# ✓ PostgreSQL: Healthy (5.2GB)
```

### Ver Logs em Tempo Real

```bash
railway logs --follow
```

### Métricas

Railway Dashboard → Deployments → Metrics
- CPU Usage
- Memory Usage
- Request Count
- Error Rate

---

## 🎯 Resultado Final

✅ **APIs em Produção**
- API Questões: ~300ms per request
- API Mapas: ~150ms per request
- Database: 37k questões + explicações

✅ **URLs para Vercel**
- `NEXT_PUBLIC_API_QUESTOES=https://api-questoes-prod.railway.app`
- `NEXT_PUBLIC_API_MAPAS=https://api-mapas-prod.railway.app`

✅ **Pronto para Deploy em Vercel**

---

## 🔄 Próximos Passos

1. Anotar URLs do Railway
2. Deploy em Vercel (usar URLs acima)
3. Testar integração completa
4. Configurar domínio customizado (doutoraia.com)
5. Lançamento oficial sexta 17:00

---

## 📚 Referências

- [Railway Docs](https://docs.railway.app)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment)
- [PostgreSQL on Railway](https://docs.railway.app/databases/postgresql)

