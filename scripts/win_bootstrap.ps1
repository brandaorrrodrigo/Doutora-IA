# ============================================
# Doutora IA - Bootstrap Script for Windows
# ============================================

Write-Host "========================================" -ForegroundColor Green
Write-Host "  DOUTORA IA - Bootstrap MVP" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

# Check Docker
Write-Host "[1/8] Verificando Docker..." -ForegroundColor Cyan
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: Docker não encontrado. Instale Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "Docker OK`n" -ForegroundColor Green

# Check Python
Write-Host "[2/8] Verificando Python..." -ForegroundColor Cyan
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: Python não encontrado. Instale Python 3.11+." -ForegroundColor Red
    exit 1
}
Write-Host "Python OK`n" -ForegroundColor Green

# Create .env from example
Write-Host "[3/8] Configurando .env..." -ForegroundColor Cyan
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env criado. EDITE O ARQUIVO COM SUA API KEY!`n" -ForegroundColor Yellow
} else {
    Write-Host ".env já existe`n" -ForegroundColor Green
}

# Start Docker Compose
Write-Host "[4/8] Iniciando containers Docker..." -ForegroundColor Cyan
docker-compose up -d --build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao iniciar Docker Compose." -ForegroundColor Red
    exit 1
}
Write-Host "Containers iniciados`n" -ForegroundColor Green

# Wait for services
Write-Host "[5/8] Aguardando serviços ficarem prontos..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# Run database migrations/seed
Write-Host "[6/8] Inicializando banco de dados..." -ForegroundColor Cyan
docker-compose exec -T api python -c "from db import init_db; init_db()" 2>$null
Start-Sleep -Seconds 5

# Seed data
Write-Host "[7/8] Criando dados iniciais..." -ForegroundColor Cyan
$response = Invoke-WebRequest -Uri "http://localhost:8000/seed" -Method POST -UseBasicParsing -ErrorAction SilentlyContinue
if ($response.StatusCode -eq 200) {
    Write-Host "Seed executado com sucesso`n" -ForegroundColor Green
} else {
    Write-Host "AVISO: Seed pode não ter executado corretamente`n" -ForegroundColor Yellow
}

# Instructions
Write-Host "[8/8] Bootstrap completo!`n" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Execute: .\scripts\ingest_sample.ps1" -ForegroundColor White
Write-Host "   (Para popular o Qdrant com dados de amostra)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Execute: .\scripts\smoke_test.ps1" -ForegroundColor White
Write-Host "   (Para testar todos os endpoints)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Acesse: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   (Swagger UI da API)" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Abra web/index.html no navegador" -ForegroundColor White
Write-Host "   (Landing page)" -ForegroundColor Gray
Write-Host "========================================`n" -ForegroundColor Green
