@echo off
REM Script para executar migration da Fase 2 + Fase 3 no Windows
REM Execute: scripts\migrate_fase2_fase3.bat

echo ========================================
echo  Migracao Fase 2 + Fase 3 - Doutora IA
echo ========================================
echo.

REM Verificar se Docker está rodando
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Docker nao esta rodando. Por favor, inicie o Docker primeiro.
    pause
    exit /b 1
)

REM Verificar se o container do banco está rodando
docker ps | findstr "postgres" >nul
if errorlevel 1 (
    echo [AVISO] Container PostgreSQL nao encontrado. Iniciando containers...
    docker compose up -d db
    echo [INFO] Aguardando PostgreSQL inicializar ^(10 segundos^)...
    timeout /t 10 /nobreak >nul
)

REM Executar migration
echo [INFO] Executando migration 002_fase2_fase3_tables.sql...
docker compose exec -T db psql -U postgres -d doutora < migrations\002_fase2_fase3_tables.sql

if errorlevel 1 (
    echo.
    echo [ERRO] Erro ao executar migration. Verifique os logs acima.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Migration executada com sucesso!
echo ========================================
echo.
echo Proximos passos:
echo   1. Configure as variaveis de ambiente no .env ^(Twilio, SMTP^)
echo   2. Instale as novas dependencias:
echo      docker compose exec api pip install -r requirements.txt
echo   3. Reinicie a API:
echo      docker compose restart api
echo   4. Teste os endpoints em http://localhost:8080/docs
echo.
pause
