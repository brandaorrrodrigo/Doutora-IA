# ============================================
# SCRIPT DE DEPLOY - DOUTORA IA
# ============================================

Write-Host "🚀 Configurando variáveis de ambiente..." -ForegroundColor Cyan

# IMPORTANTE: Substitua SUA_OPENAI_KEY_AQUI pela sua chave real!
$OPENAI_KEY = "SUA_OPENAI_KEY_AQUI"

# Configurar todas as variáveis
railway variables set `
  SECRET_KEY="MA9jR3vlo0wAa-Hus9fhPl7lui99WIsGhZKCP313v9FqavWHXmFR1oIYT2gkHfCLhE0eq0z8A-vLZRIhd-BglQ" `
  ADMIN_SECRET_TOKEN="5OgfMnvIe82EcF9fd-UxhSv5osTyHkVUQ4ANCCb8QN8" `
  ENV="production" `
  OPENAI_API_KEY="$OPENAI_KEY" `
  LLM_BASE_URL="https://api.openai.com/v1" `
  LLM_MODEL="gpt-4o-mini" `
  EMAIL_PROVIDER="console" `
  EMAIL_FROM="noreply@doutora-ia.com" `
  REDIS_ENABLED="true" `
  EMBEDDING_DEVICE="cpu" `
  API_PORT="8000" `
  WEASYPRINT_CMD="weasyprint"

Write-Host "✅ Variáveis configuradas!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Fazendo deploy..." -ForegroundColor Cyan

# Deploy
railway up

Write-Host ""
Write-Host "✅ Deploy concluído!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Obtendo URL do projeto..." -ForegroundColor Cyan

# Pegar URL
railway domain

Write-Host ""
Write-Host "🎉 PRONTO! Seu sistema está no ar!" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Testar: curl https://[URL]/health"
Write-Host "2. Ver docs: https://[URL]/docs"
Write-Host "3. Ver logs: railway logs"
Write-Host ""
