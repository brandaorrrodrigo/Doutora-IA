# ============================================
# DOUTORA IA - TEST RUNNER (PowerShell)
# ============================================

$ErrorActionPreference = "Stop"

# Get project root
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "================================" -ForegroundColor Cyan
Write-Host "DOUTORA IA - Running Tests" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "api\pytest.ini")) {
    Write-Host "Error: Must run from project root" -ForegroundColor Red
    exit 1
}

# Install test dependencies
Write-Host "1/4 Installing test dependencies..." -ForegroundColor Yellow
Set-Location api
pip install -q -r requirements-test.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Run linting (optional)
if (Get-Command flake8 -ErrorAction SilentlyContinue) {
    Write-Host "2/4 Running linter..." -ForegroundColor Yellow
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    Write-Host "✓ Linting complete" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "2/4 Skipping linter (flake8 not installed)" -ForegroundColor Yellow
    Write-Host ""
}

# Run tests
Write-Host "3/4 Running test suite..." -ForegroundColor Yellow
$TestArgs = @(
    "tests/",
    "--verbose",
    "--cov=.",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--junit-xml=test-results.xml"
)

# Add any additional arguments passed to script
$TestArgs += $args

pytest @TestArgs

$TestExitCode = $LASTEXITCODE

if ($TestExitCode -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Some tests failed" -ForegroundColor Red
}
Write-Host ""

# Generate coverage report
Write-Host "4/4 Generating coverage report..." -ForegroundColor Yellow
if (Test-Path "htmlcov\index.html") {
    Write-Host "✓ Coverage report generated: api\htmlcov\index.html" -ForegroundColor Green

    # Try to open in browser
    try {
        Start-Process "htmlcov\index.html"
    } catch {
        # Silently fail if browser can't open
    }
}
Write-Host ""

Write-Host "================================" -ForegroundColor Cyan
if ($TestExitCode -eq 0) {
    Write-Host "TEST SUITE PASSED ✓" -ForegroundColor Green
} else {
    Write-Host "TEST SUITE FAILED ✗" -ForegroundColor Red
}
Write-Host "================================" -ForegroundColor Cyan

exit $TestExitCode
