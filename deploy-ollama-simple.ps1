# DEPLOY DOUTORA IA COM OLLAMA

Write-Host ""
Write-Host "DEPLOY DOUTORA IA + OLLAMA" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANTE: Ollama no Railway requer 2-4GB RAM (~20-35 USD/mes)" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Deseja continuar com Ollama? (s/N)"
if ($confirm -ne 's' -and $confirm -ne 'S') {
    Write-Host "Deploy cancelado." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "[1/4] Configurando Railway..." -ForegroundColor Cyan

# Backup e config
if (Test-Path "railway.json") {
    Copy-Item "railway.json" "railway.json.backup"
}
Copy-Item "railway-ollama.json" "railway.json" -Force

Write-Host "OK!" -ForegroundColor Green
Write-Host ""

Write-Host "[2/4] Configurando variaveis..." -ForegroundColor Cyan

railway variables set SECRET_KEY="MA9jR3vlo0wAa-Hus9fhPl7lui99WIsGhZKCP313v9FqavWHXmFR1oIYT2gkHfCLhE0eq0z8A-vLZRIhd-BglQ" ADMIN_SECRET_TOKEN="5OgfMnvIe82EcF9fd-UxhSv5osTyHkVUQ4ANCCb8QN8" ENV="production" OPENAI_API_KEY="ollama" LLM_BASE_URL="http://localhost:11434/v1" LLM_MODEL="qwen2:0.5b" EMAIL_PROVIDER="console" EMAIL_FROM="noreply@doutora-ia.com" REDIS_ENABLED="true" EMBEDDING_DEVICE="cpu" API_PORT="8000" WEASYPRINT_CMD="weasyprint" WORKERS="1"

Write-Host "OK!" -ForegroundColor Green
Write-Host ""

Write-Host "[3/4] Fazendo deploy..." -ForegroundColor Cyan
Write-Host "Isso pode levar 5-10 minutos..." -ForegroundColor Yellow
Write-Host ""

railway up

Write-Host ""
Write-Host "Deploy iniciado!" -ForegroundColor Green
Write-Host ""

Write-Host "[4/4] Obtendo URL..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

railway domain

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "DEPLOY COMPLETO!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "1. Aguardar build (5-10 min)" -ForegroundColor White
Write-Host "2. Ver logs: railway logs -f" -ForegroundColor White
Write-Host "3. Testar: curl [URL]/health" -ForegroundColor White
Write-Host ""
