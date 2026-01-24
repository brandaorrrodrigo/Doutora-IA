# Doutora IA - Script de Desenvolvimento Local (Windows)
# Execute: .\scripts\start_dev.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  DOUTORA IA - Ambiente de Desenvolvimento" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Verificar Docker
Write-Host "`nVerificando Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Docker nao esta rodando!" -ForegroundColor Red
    Write-Host "Por favor, inicie o Docker Desktop e tente novamente." -ForegroundColor Red
    exit 1
}
Write-Host "Docker OK!" -ForegroundColor Green

# Subir servicos basicos (PostgreSQL, Qdrant, Redis)
Write-Host "`nSubindo servicos basicos (db, qdrant, redis)..." -ForegroundColor Yellow
docker-compose up -d db qdrant redis

# Aguardar PostgreSQL
Write-Host "`nAguardando PostgreSQL ficar pronto..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
while ($attempt -lt $maxAttempts) {
    $result = docker exec doutora-db pg_isready -U postgres 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PostgreSQL pronto!" -ForegroundColor Green
        break
    }
    $attempt++
    Start-Sleep -Seconds 1
}
if ($attempt -eq $maxAttempts) {
    Write-Host "ERRO: PostgreSQL nao iniciou a tempo" -ForegroundColor Red
    exit 1
}

# Aguardar Qdrant
Write-Host "`nAguardando Qdrant ficar pronto..." -ForegroundColor Yellow
$attempt = 0
while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:6333/health" -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "Qdrant pronto!" -ForegroundColor Green
            break
        }
    } catch {
        $attempt++
        Start-Sleep -Seconds 1
    }
}

# Ingerir dados de sample
Write-Host "`nIngerindo dados de sample no Qdrant..." -ForegroundColor Yellow
python scripts/ingest_full_corpus.py --samples

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "  Ambiente pronto!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host "`nPara iniciar a API:" -ForegroundColor Cyan
Write-Host "  cd api" -ForegroundColor White
Write-Host "  python -m uvicorn main:app --reload --port 8080" -ForegroundColor White
Write-Host "`nAcesse:" -ForegroundColor Cyan
Write-Host "  API:     http://localhost:8080" -ForegroundColor White
Write-Host "  Docs:    http://localhost:8080/docs" -ForegroundColor White
Write-Host "  Qdrant:  http://localhost:6333/dashboard" -ForegroundColor White
