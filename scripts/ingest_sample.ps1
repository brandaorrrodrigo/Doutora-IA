# ============================================
# Doutora IA - Ingest Sample Data
# ============================================

Write-Host "========================================" -ForegroundColor Green
Write-Host "  DOUTORA IA - Ingest Sample Data" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

# Install ingest requirements
Write-Host "[1/3] Instalando dependências de ingestão..." -ForegroundColor Cyan
Set-Location ingest
python -m pip install -r requirements.txt --quiet
Set-Location ..
Write-Host "Dependências instaladas`n" -ForegroundColor Green

# Process samples and upload to Qdrant
Write-Host "[2/3] Processando amostras..." -ForegroundColor Cyan

$collections = @("legis", "sumulas", "temas", "juris", "regulatorio", "doutrina")

foreach ($collection in $collections) {
    Write-Host "Processando coleção: $collection" -ForegroundColor Yellow
    
    $samples = Get-ChildItem "data/samples/$collection/*.json"
    
    if ($samples.Count -eq 0) {
        Write-Host "  AVISO: Nenhuma amostra encontrada em $collection" -ForegroundColor Yellow
        continue
    }
    
    foreach ($sample in $samples) {
        Write-Host "  - $($sample.Name)" -ForegroundColor Gray
    }
    
    # Upload to Qdrant
    $fileList = $samples | ForEach-Object { $_.FullName }
    python ingest/build_corpus.py $collection $fileList
    
    Write-Host "  Coleção $collection processada`n" -ForegroundColor Green
}

# Verify
Write-Host "[3/3] Verificando upload..." -ForegroundColor Cyan
$response = Invoke-WebRequest -Uri "http://localhost:8000/search" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"query": "alimentos", "limit": 3}' `
    -UseBasicParsing

if ($response.StatusCode -eq 200) {
    $results = $response.Content | ConvertFrom-Json
    Write-Host "Busca retornou $($results.Count) resultados`n" -ForegroundColor Green
} else {
    Write-Host "AVISO: Verificação de busca falhou`n" -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "Ingestão de amostras completa!" -ForegroundColor Green
Write-Host "Você pode agora testar a API." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Green
