#!/bin/bash
# Script para executar migration da Fase 2 + Fase 3
# Execute: bash scripts/migrate_fase2_fase3.sh

set -e

echo "🚀 Iniciando migração Fase 2 + Fase 3..."
echo ""

# Verificar se Docker está rodando
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Verificar se o container do banco está rodando
if ! docker ps | grep -q "postgres"; then
    echo "⚠️  Container PostgreSQL não encontrado. Iniciando containers..."
    docker compose up -d db
    echo "⏳ Aguardando PostgreSQL inicializar (10 segundos)..."
    sleep 10
fi

# Executar migration
echo "📊 Executando migration 002_fase2_fase3_tables.sql..."
docker compose exec -T db psql -U postgres -d doutora < migrations/002_fase2_fase3_tables.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration executada com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "   1. Configure as variáveis de ambiente no .env (Twilio, SMTP)"
    echo "   2. Instale as novas dependências: docker compose exec api pip install -r requirements.txt"
    echo "   3. Reinicie a API: docker compose restart api"
    echo "   4. Teste os endpoints em http://localhost:8080/docs"
    echo ""
else
    echo ""
    echo "❌ Erro ao executar migration. Verifique os logs acima."
    exit 1
fi
