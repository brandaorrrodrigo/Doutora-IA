#!/bin/bash

# ============================================
# DEPLOY AUTOMÁTICO - RAILWAY
# Doutora IA - Production Ready
# ============================================

set -e  # Exit on error

echo "🚀 DEPLOY DOUTORA IA - RAILWAY"
echo "======================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar Railway CLI
echo -e "${BLUE}[1/6]${NC} Verificando Railway CLI..."
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Railway CLI não encontrado. Instalando...${NC}"

    # Detectar OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://railway.app/install.sh | sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install railway
    else
        echo "Instale Railway CLI: https://docs.railway.app/develop/cli"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Railway CLI OK${NC}"
echo ""

# 2. Login
echo -e "${BLUE}[2/6]${NC} Login no Railway..."
railway whoami &> /dev/null || railway login
echo -e "${GREEN}✓ Login OK${NC}"
echo ""

# 3. Gerar secret keys
echo -e "${BLUE}[3/6]${NC} Gerando secret keys..."
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(64))")
ADMIN_TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
echo -e "${GREEN}✓ Keys geradas${NC}"
echo ""

# 4. Configurar variáveis
echo -e "${BLUE}[4/6]${NC} Configurando variáveis de ambiente..."

# Perguntar OpenAI key
read -p "OpenAI API Key (ou Enter para pular): " OPENAI_KEY
if [ -z "$OPENAI_KEY" ]; then
    OPENAI_KEY="sk-placeholder"
fi

# Perguntar Resend key
read -p "Resend API Key (ou Enter para usar console mode): " RESEND_KEY
if [ -z "$RESEND_KEY" ]; then
    EMAIL_PROVIDER="console"
    RESEND_KEY=""
else
    EMAIL_PROVIDER="resend"
fi

# Set variables
railway variables set \
    SECRET_KEY="$SECRET_KEY" \
    ADMIN_SECRET_TOKEN="$ADMIN_TOKEN" \
    ENV="production" \
    OPENAI_API_KEY="$OPENAI_KEY" \
    LLM_BASE_URL="https://api.openai.com/v1" \
    LLM_MODEL="gpt-4o-mini" \
    EMAIL_PROVIDER="$EMAIL_PROVIDER" \
    RESEND_API_KEY="$RESEND_KEY" \
    EMAIL_FROM="noreply@doutora-ia.com" \
    REDIS_ENABLED="true" \
    EMBEDDING_DEVICE="cpu" \
    API_PORT="8000"

echo -e "${GREEN}✓ Variáveis configuradas${NC}"
echo ""

# 5. Deploy
echo -e "${BLUE}[5/6]${NC} Fazendo deploy..."
railway up

echo -e "${GREEN}✓ Deploy iniciado!${NC}"
echo ""

# 6. Informações finais
echo -e "${BLUE}[6/6]${NC} Obtendo informações do deploy..."
sleep 5

RAILWAY_URL=$(railway domain 2>/dev/null || echo "Configurar no dashboard")

echo ""
echo "======================================"
echo -e "${GREEN}✅ DEPLOY COMPLETO!${NC}"
echo "======================================"
echo ""
echo "📋 Informações importantes:"
echo ""
echo "🔗 URL: $RAILWAY_URL"
echo "🔑 Admin Token: $ADMIN_TOKEN"
echo "🎛️  Dashboard: https://railway.app/dashboard"
echo ""
echo "📝 Próximos passos:"
echo "1. Acesse Railway Dashboard"
echo "2. Adicione PostgreSQL: New → Database → PostgreSQL"
echo "3. Adicione Redis: New → Database → Redis"
echo "4. Configure custom domain (opcional)"
echo "5. Teste: curl $RAILWAY_URL/health"
echo ""
echo "======================================"
echo ""

# Salvar informações
cat > deploy-info.txt <<EOF
DEPLOY INFORMATION - $(date)
====================================

Railway URL: $RAILWAY_URL
Admin Token: $ADMIN_TOKEN
Dashboard: https://railway.app/dashboard

Next Steps:
1. Add PostgreSQL database
2. Add Redis database
3. Run migrations: railway run alembic upgrade head
4. Test: curl $RAILWAY_URL/health

====================================
EOF

echo "💾 Informações salvas em: deploy-info.txt"
echo ""
