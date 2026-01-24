# 🚀 GUIA DE DEPLOY - Doutora IA

Deploy completo para produção em **menos de 30 minutos**!

---

## 🎯 OPÇÕES DE DEPLOY

Escolha a melhor opção para você:

### Opção 1: **Railway** (Recomendado - Mais Fácil) ⭐
- ✅ Deploy em 5 minutos
- ✅ Free tier generoso
- ✅ Postgres + Redis inclusos
- ✅ HTTPS automático
- ✅ CI/CD automático

### Opção 2: **Vercel + Supabase** (Serverless)
- ✅ Frontend na Vercel
- ✅ Backend na Vercel Functions
- ✅ Supabase (Postgres)
- ✅ Upstash (Redis)

### Opção 3: **DigitalOcean** (VPS Tradicional)
- ✅ Controle total
- ✅ $6/mês
- ✅ Docker Compose

### Opção 4: **AWS** (Enterprise)
- ✅ Escalável
- ✅ ECS + RDS + ElastiCache
- ✅ Mais complexo

---

## 🚂 OPÇÃO 1: RAILWAY (RECOMENDADO)

### Por que Railway?
- 🎁 $5 grátis/mês (suficiente para MVP)
- ⚡ Deploy em minutos
- 🔒 HTTPS automático
- 📊 Monitoramento incluso
- 🔄 CI/CD automático

### Passo a Passo:

#### 1. Criar conta no Railway
```bash
# Acesse: https://railway.app
# Login com GitHub
```

#### 2. Instalar Railway CLI
```bash
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# Verificar
railway --version
```

#### 3. Preparar projeto
```bash
cd C:\Users\NFC\doutora-ia

# Login no Railway
railway login

# Criar novo projeto
railway init
# Escolha: "Create new project"
# Nome: doutora-ia
```

#### 4. Adicionar serviços

**No Dashboard do Railway (https://railway.app/dashboard):**

1. **Adicionar PostgreSQL:**
   - Click "New" → "Database" → "PostgreSQL"
   - Copiar `DATABASE_URL`

2. **Adicionar Redis:**
   - Click "New" → "Database" → "Redis"
   - Copiar `REDIS_URL`

3. **Adicionar Qdrant:**
   - Click "New" → "Empty Service"
   - Nome: "qdrant"
   - Settings → Deploy:
     - Docker Image: `qdrant/qdrant:latest`
     - Port: 6333

#### 5. Configurar variáveis de ambiente

No Railway Dashboard → Seu Projeto → Variables:

```bash
# Database (Railway gera automaticamente)
DATABASE_URL=postgresql://...

# Redis (Railway gera automaticamente)
REDIS_URL=redis://...

# Parse do DATABASE_URL para formato separado
PG_HOST=containers-us-west-xxx.railway.app
PG_PORT=5432
PG_DB=railway
PG_USER=postgres
PG_PASSWORD=xxx

# Parse do REDIS_URL
REDIS_HOST=containers-us-west-xxx.railway.app
REDIS_PORT=6379
REDIS_PASSWORD=xxx
REDIS_ENABLED=true

# Qdrant
QDRANT_URL=http://qdrant.railway.internal:6333

# LLM - Ollama Local ou OpenAI
# Opção 1: OpenAI (mais fácil em cloud)
LLM_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-xxxxxxxx
LLM_MODEL=gpt-4o-mini

# Opção 2: Ollama (precisa rodar em servidor próprio)
# LLM_BASE_URL=http://seu-servidor-ollama:11434/v1
# LLM_MODEL=llama3:latest

# Email - Resend (grátis até 3000/mês)
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_xxxxxxxx
EMAIL_FROM=noreply@doutora-ia.com
EMAIL_FROM_NAME=Doutora IA

# Security
SECRET_KEY=gere_token_seguro_aqui_64_chars
ADMIN_SECRET_TOKEN=gere_token_admin_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Embeddings
EMBEDDING_MODEL=intfloat/multilingual-e5-large
EMBEDDING_DEVICE=cpu

# Outros
ENV=production
API_HOST=0.0.0.0
API_PORT=8000
```

**Gerar SECRET_KEY seguro:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

#### 6. Criar Dockerfile (se não existir)

```dockerfile
# C:\Users\NFC\doutora-ia\Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY api/ .

# Expose port
EXPOSE 8000

# Run migrations and start
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 7. Criar railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 8. Deploy!

```bash
# Push para GitHub (Railway detecta automaticamente)
git add .
git commit -m "Deploy to Railway"
git push origin main

# Ou deploy direto via CLI
railway up
```

#### 9. Configurar domínio

No Railway Dashboard:
1. Settings → Domains
2. Click "Generate Domain"
3. Seu app estará em: `https://doutora-ia-production.up.railway.app`

**Domínio customizado (opcional):**
1. Settings → Domains → "Custom Domain"
2. Adicionar: `api.doutora-ia.com`
3. Configurar DNS:
   - CNAME: `api` → `seu-app.up.railway.app`

#### 10. Rodar migrations

```bash
# Via Railway CLI
railway run alembic upgrade head

# Ou via Dashboard
# Settings → Variables → Add Variable
# RUN_MIGRATIONS=true
```

#### 11. Seed inicial

```bash
railway run python -c "
from db import init_db, get_db
from seed import seed_database
init_db()
seed_database(next(get_db()))
"
```

---

## ☁️ OPÇÃO 2: VERCEL + SUPABASE

### Setup Rápido:

#### 1. Frontend (se tiver)
```bash
# Deploy frontend na Vercel
vercel --prod
```

#### 2. Backend (Serverless)
```bash
# Criar vercel.json
{
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/main.py"
    }
  ]
}

# Deploy
vercel --prod
```

#### 3. Database - Supabase
```bash
# Acesse: https://supabase.com
# Criar projeto
# Copiar DATABASE_URL
```

#### 4. Redis - Upstash
```bash
# Acesse: https://upstash.com
# Criar Redis database
# Copiar REDIS_URL
```

---

## 🐳 OPÇÃO 3: DIGITALOCEAN (VPS)

### Setup Completo:

#### 1. Criar Droplet
```bash
# DigitalOcean Dashboard
# Create → Droplets
# Ubuntu 22.04
# Basic Plan: $6/mês
# SSH Key: Adicionar sua chave
```

#### 2. Conectar via SSH
```bash
ssh root@seu-ip
```

#### 3. Instalar Docker
```bash
# Atualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install docker-compose -y

# Verificar
docker --version
docker-compose --version
```

#### 4. Clonar projeto
```bash
cd /opt
git clone https://github.com/seu-usuario/doutora-ia.git
cd doutora-ia
```

#### 5. Configurar .env
```bash
cp .env.example .env
nano .env

# Editar variáveis:
# - SECRET_KEY (gerar)
# - ADMIN_SECRET_TOKEN (gerar)
# - OPENAI_API_KEY (se usar OpenAI)
# - RESEND_API_KEY (se usar Resend)
# Etc.
```

#### 6. Subir serviços
```bash
docker-compose up -d

# Ver logs
docker-compose logs -f api
```

#### 7. Configurar Nginx + SSL
```bash
# Instalar Nginx e Certbot
apt install nginx certbot python3-certbot-nginx -y

# Criar config do Nginx
cat > /etc/nginx/sites-available/doutora-ia <<EOF
server {
    listen 80;
    server_name api.doutora-ia.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSockets
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Ativar site
ln -s /etc/nginx/sites-available/doutora-ia /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Configurar SSL (Let's Encrypt)
certbot --nginx -d api.doutora-ia.com
# Seguir instruções
```

#### 8. Configurar auto-start
```bash
# Criar systemd service
cat > /etc/systemd/system/doutora-ia.service <<EOF
[Unit]
Description=Doutora IA
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/doutora-ia
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
EOF

# Habilitar
systemctl enable doutora-ia
systemctl start doutora-ia
```

---

## 📋 CHECKLIST PRÉ-DEPLOY

Antes de colocar no ar, verificar:

### Segurança:
- [ ] SECRET_KEY gerado com 64+ caracteres
- [ ] ADMIN_SECRET_TOKEN forte
- [ ] Database com password forte
- [ ] Redis com password
- [ ] HTTPS configurado (SSL)
- [ ] CORS configurado corretamente
- [ ] Rate limiting ativo

### Database:
- [ ] Migrations rodadas (`alembic upgrade head`)
- [ ] Seed executado (planos, etc)
- [ ] Backup configurado
- [ ] Índices criados

### Email:
- [ ] Resend API key configurada
- [ ] Email sender verificado
- [ ] Templates testados
- [ ] SPF/DKIM configurados

### Cache:
- [ ] Redis rodando
- [ ] REDIS_ENABLED=true
- [ ] Cache stats funcionando

### LLM:
- [ ] OpenAI API key OU Ollama configurado
- [ ] Modelo testado
- [ ] Rate limits do provider conhecidos

### Monitoring:
- [ ] Logs configurados
- [ ] Sentry (opcional)
- [ ] Uptime monitoring (UptimeRobot)

### DNS:
- [ ] Domínio apontando para servidor
- [ ] SSL certificate válido
- [ ] www redirect configurado

---

## 🧪 TESTAR EM PRODUÇÃO

```bash
# 1. Health check
curl https://api.doutora-ia.com/health

# Expected:
# {"status": "healthy", "timestamp": "...", "version": "1.0.0"}

# 2. Register
curl -X POST https://api.doutora-ia.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "test123"
  }'

# 3. Login
curl -X POST https://api.doutora-ia.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'

# Copiar access_token

# 4. Busca (protegida)
curl -X POST https://api.doutora-ia.com/search/advanced \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "acidente de trânsito"
  }'

# 5. Cache stats
curl https://api.doutora-ia.com/cache/stats

# 6. Admin (com token)
curl "https://api.doutora-ia.com/admin/analytics/overview?admin_token=SEU_ADMIN_TOKEN"
```

---

## 📊 MONITORING & MANUTENÇÃO

### 1. Setup Sentry (Error Tracking)
```bash
# Instalar
pip install sentry-sdk[fastapi]

# Em main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxx@sentry.io/xxx",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)
```

### 2. Setup UptimeRobot (Uptime Monitoring)
```bash
# Acesse: https://uptimerobot.com
# Adicionar monitor:
# - Type: HTTP(S)
# - URL: https://api.doutora-ia.com/health
# - Interval: 5 minutes
```

### 3. Logs
```bash
# Railway: Dashboard → Deployments → View Logs

# DigitalOcean:
docker-compose logs -f api --tail=100

# Salvar logs
docker-compose logs api > logs.txt
```

### 4. Backup Database
```bash
# Railway: Dashboard → Database → Backups

# DigitalOcean (cron diário):
cat > /opt/backup-db.sh <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U postgres doutora_ia > /opt/backups/db_$DATE.sql
# Manter apenas últimos 7 dias
find /opt/backups -name "db_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/backup-db.sh

# Adicionar ao cron
crontab -e
# Adicionar linha:
0 2 * * * /opt/backup-db.sh
```

---

## 🚀 SCRIPTS DE DEPLOY RÁPIDO

### Script tudo-em-um (Railway):

```bash
# deploy-railway.sh
#!/bin/bash

echo "🚀 Deploy Doutora IA para Railway"

# 1. Gerar secret keys
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(64))")
export ADMIN_TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

echo "✅ Secret keys geradas"

# 2. Set variables no Railway
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set ADMIN_SECRET_TOKEN="$ADMIN_TOKEN"
railway variables set ENV="production"

echo "✅ Variáveis configuradas"

# 3. Deploy
railway up

echo "✅ Deploy iniciado!"
echo "🔗 Acompanhe em: https://railway.app/dashboard"
```

### Script para atualização:

```bash
# update.sh
#!/bin/bash

echo "🔄 Atualizando Doutora IA..."

# Pull latest
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Run migrations
docker-compose exec -T api alembic upgrade head

echo "✅ Atualização completa!"
```

---

## 🎯 CUSTOS ESTIMADOS

### Railway (Recomendado para começar):
- **Free tier**: $5/mês de crédito
- **Estimativa real**: ~$10-15/mês
  - App: $5
  - Postgres: $5
  - Redis: $2
  - Qdrant: $3

### Vercel + Supabase:
- **Vercel**: Free (até 100GB bandwidth)
- **Supabase**: Free (até 500MB DB)
- **Upstash Redis**: Free (até 10k commands/day)
- **Total**: $0-5/mês

### DigitalOcean:
- **Droplet**: $6/mês (básico)
- **Domain**: $12/ano
- **Total**: ~$7/mês

### AWS (Enterprise):
- **Estimativa**: $50-200/mês (dependendo da escala)

---

## ✅ DEPLOY CHECKLIST FINAL

```
Preparação:
[ ] Código commitado no GitHub
[ ] .env.example atualizado
[ ] Dockerfile criado
[ ] docker-compose.yml configurado
[ ] Requirements.txt completo

Configuração:
[ ] Secret keys geradas
[ ] Database URL configurada
[ ] Redis URL configurada
[ ] Qdrant URL configurada
[ ] Email provider configurado (Resend)
[ ] LLM configurado (OpenAI ou Ollama)

Deploy:
[ ] Serviço escolhido (Railway/Vercel/DO)
[ ] Variáveis de ambiente setadas
[ ] Deploy executado
[ ] Migrations rodadas
[ ] Seed executado

Verificação:
[ ] /health retorna 200
[ ] Auth funcionando
[ ] Search funcionando
[ ] Cache funcionando
[ ] Emails enviando
[ ] Admin acessível
[ ] WebSockets conectando

DNS & SSL:
[ ] Domínio configurado
[ ] SSL ativo (HTTPS)
[ ] www redirect funcionando

Monitoring:
[ ] Logs acessíveis
[ ] Sentry configurado (opcional)
[ ] Uptime monitor ativo
[ ] Backup configurado
```

---

## 🎉 PRONTO!

Sistema no ar em produção! 🚀

**URLs importantes:**
- API: `https://api.doutora-ia.com`
- Health: `https://api.doutora-ia.com/health`
- Docs: `https://api.doutora-ia.com/docs`
- Admin: `https://api.doutora-ia.com/admin/analytics/overview?admin_token=XXX`

**Próximos passos:**
1. Monitorar logs primeiras 24h
2. Configurar alertas
3. Marketing/divulgação
4. Coletar feedback
5. Iterar! 🔄

---

**SISTEMA NO AR! 🎊🎊🎊**
