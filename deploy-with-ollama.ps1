# ============================================
# DEPLOY DOUTORA IA COM OLLAMA
# Self-hosted LLM - Totalmente Grátis!
# ============================================

Write-Host ""
Write-Host "🚀 DEPLOY DOUTORA IA + OLLAMA" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  IMPORTANTE - Leia antes de continuar:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ollama no Railway requer mais recursos:" -ForegroundColor Yellow
Write-Host "  • Mínimo: 2GB RAM (~`$20/mês)" -ForegroundColor Yellow
Write-Host "  • Recomendado: 4GB RAM (~`$35/mês)" -ForegroundColor Yellow
Write-Host "  • Modelo usado: qwen2:0.5b (308MB - rápido)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Comparação:" -ForegroundColor White
Write-Host "  • Ollama no Railway: `$20-35/mês" -ForegroundColor White
Write-Host "  • OpenAI API: `$5-15/mês (com cache)" -ForegroundColor White
Write-Host "  • Groq API: GRÁTIS!" -ForegroundColor Green
Write-Host ""

$confirm = Read-Host "Deseja continuar com Ollama? (s/N)"
if ($confirm -ne 's' -and $confirm -ne 'S') {
    Write-Host ""
    Write-Host "❌ Deploy cancelado." -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternativas:" -ForegroundColor Cyan
    Write-Host "1. Groq (grátis): https://console.groq.com/keys" -ForegroundColor White
    Write-Host "2. OpenAI (pago): https://platform.openai.com/api-keys" -ForegroundColor White
    Write-Host ""
    exit
}

Write-Host ""
Write-Host "[1/4] Configurando Railway para usar Dockerfile.ollama..." -ForegroundColor Cyan

# Backup railway.json original
if (Test-Path "railway.json") {
    Copy-Item "railway.json" "railway.json.backup"
}

# Usar config Ollama
Copy-Item "railway-ollama.json" "railway.json" -Force

Write-Host "✅ Configuração atualizada!" -ForegroundColor Green
Write-Host ""

Write-Host "[2/4] Configurando variáveis de ambiente..." -ForegroundColor Cyan

railway variables set `
  SECRET_KEY="MA9jR3vlo0wAa-Hus9fhPl7lui99WIsGhZKCP313v9FqavWHXmFR1oIYT2gkHfCLhE0eq0z8A-vLZRIhd-BglQ" `
  ADMIN_SECRET_TOKEN="5OgfMnvIe82EcF9fd-UxhSv5osTyHkVUQ4ANCCb8QN8" `
  ENV="production" `
  OPENAI_API_KEY="ollama" `
  LLM_BASE_URL="http://localhost:11434/v1" `
  LLM_MODEL="qwen2:0.5b" `
  EMAIL_PROVIDER="console" `
  EMAIL_FROM="noreply@doutora-ia.com" `
  REDIS_ENABLED="true" `
  EMBEDDING_DEVICE="cpu" `
  API_PORT="8000" `
  WEASYPRINT_CMD="weasyprint" `
  WORKERS="1"

Write-Host "✅ Variáveis configuradas!" -ForegroundColor Green
Write-Host ""

Write-Host "[3/4] Fazendo deploy..." -ForegroundColor Cyan
Write-Host "⏳ Isso pode levar 5-10 minutos na primeira vez..." -ForegroundColor Yellow
Write-Host "   (Download do modelo Ollama)" -ForegroundColor Yellow
Write-Host ""

railway up

Write-Host ""
Write-Host "✅ Deploy iniciado!" -ForegroundColor Green
Write-Host ""

Write-Host "[4/4] Obtendo informações..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

$url = railway domain

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "✅ DEPLOY COMPLETO!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Informações:" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 URL: $url" -ForegroundColor White
Write-Host "🤖 LLM: Ollama (qwen2:0.5b)" -ForegroundColor White
Write-Host "💾 Totalmente self-hosted!" -ForegroundColor White
Write-Host ""
Write-Host "📝 Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Aguardar build completar (5-10 min)" -ForegroundColor White
Write-Host "2. Ver logs: railway logs -f" -ForegroundColor White
Write-Host "3. Testar: curl $url/health" -ForegroundColor White
Write-Host "4. Ver docs: $url/docs" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Notas importantes:" -ForegroundColor Yellow
Write-Host "• Primeira inicialização é lenta (download do modelo)" -ForegroundColor Yellow
Write-Host "• Respostas mais lentas que OpenAI/Groq" -ForegroundColor Yellow
Write-Host "• Monitore uso de RAM no Railway dashboard" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Para trocar para modelo maior depois:" -ForegroundColor Cyan
Write-Host "   railway variables set LLM_MODEL='llama3:latest'" -ForegroundColor White
Write-Host "   (requer 4-8GB RAM)" -ForegroundColor White
Write-Host ""

# Salvar info
@"
DEPLOY COM OLLAMA - $(Get-Date)
====================================

URL: $url
LLM: Ollama qwen2:0.5b
Admin Token: 5OgfMnvIe82EcF9fd-UxhSv5osTyHkVUQ4ANCCb8QN8

Modelos disponíveis:
- qwen2:0.5b (308MB, rápido, 2GB RAM)
- qwen2:1.5b (934MB, balanceado, 3GB RAM)
- llama3:latest (4.7GB, melhor qualidade, 8GB RAM)

Trocar modelo:
railway variables set LLM_MODEL="nome_do_modelo"
railway restart

Comandos úteis:
railway logs -f
railway open
railway restart

====================================
"@ | Out-File -FilePath "deploy-ollama-info.txt" -Encoding UTF8

Write-Host "💾 Informações salvas em: deploy-ollama-info.txt" -ForegroundColor Cyan
Write-Host ""
