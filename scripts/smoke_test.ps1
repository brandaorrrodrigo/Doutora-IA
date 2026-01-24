# ============================================
# Doutora IA - Smoke Tests
# ============================================

Write-Host "========================================" -ForegroundColor Green
Write-Host "  DOUTORA IA - Smoke Tests" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

$baseUrl = "http://localhost:8000"
$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [string]$Body = $null
    )
    
    Write-Host "Testando: $Name..." -ForegroundColor Cyan
    
    try {
        if ($Method -eq "POST") {
            if ($Body) {
                $response = Invoke-WebRequest -Uri $Url -Method POST -ContentType "application/json" -Body $Body -UseBasicParsing
            } else {
                $response = Invoke-WebRequest -Uri $Url -Method POST -UseBasicParsing
            }
        } else {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing
        }
        
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✓ PASSOU ($($response.StatusCode))" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ✗ FALHOU (Status: $($response.StatusCode))" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "  ✗ FALHOU (Erro: $($_.Exception.Message))" -ForegroundColor Red
        return $false
    }
}

# Test 1: Health Check
if (Test-Endpoint -Name "Health Check" -Url "$baseUrl/health") {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 2: Search (Alimentos)
$searchBody = @{
    query = "pensão alimentícia"
    limit = 5
} | ConvertTo-Json

if (Test-Endpoint -Name "Search - Alimentos" -Url "$baseUrl/search" -Method POST -Body $searchBody) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 3: Search (PIX)
$searchBody2 = @{
    query = "golpe pix responsabilidade banco"
    limit = 5
} | ConvertTo-Json

if (Test-Endpoint -Name "Search - PIX" -Url "$baseUrl/search" -Method POST -Body $searchBody2) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 4: Search (Plano de Saúde)
$searchBody3 = @{
    query = "negativa de cobertura plano de saúde"
    limit = 5
} | ConvertTo-Json

if (Test-Endpoint -Name "Search - Saúde" -Url "$baseUrl/search" -Method POST -Body $searchBody3) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 5: Analyze Case (Alimentos)
$analyzeBody = @{
    descricao = "Meu ex-marido parou de pagar a pensão alimentícia do nosso filho de 10 anos há 3 meses. Ele trabalha com carteira assinada."
    detalhado = $false
} | ConvertTo-Json

Write-Host "Testando: Analyze Case - Alimentos..." -ForegroundColor Cyan
Write-Host "  (Este teste pode demorar 30s - LLM processando...)" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/analyze_case" -Method POST -ContentType "application/json" -Body $analyzeBody -UseBasicParsing -TimeoutSec 60
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ PASSOU" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ✗ FALHOU" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ FALHOU (Erro: $($_.Exception.Message))" -ForegroundColor Red
    $testsFailed++
}

# Summary
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "RESULTADOS DOS TESTES:" -ForegroundColor Cyan
Write-Host "  Passou: $testsPassed" -ForegroundColor Green
Write-Host "  Falhou: $testsFailed" -ForegroundColor Red
Write-Host "========================================`n" -ForegroundColor Green

if ($testsFailed -eq 0) {
    Write-Host "✓ TODOS OS TESTES PASSARAM!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "✗ ALGUNS TESTES FALHARAM" -ForegroundColor Red
    exit 1
}
