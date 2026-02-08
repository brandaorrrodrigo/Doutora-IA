@echo off
echo ====================================
echo DOUTORA IA - EXECUTAR LOCAL
echo ====================================
echo.

echo [1/3] Verificando containers Docker...
docker ps | findstr doutora_postgres
docker ps | findstr doutora_qdrant
docker ps | findstr doutora_redis

echo.
echo [2/3] Configurando ambiente...
cd api
set DATABASE_URL=postgresql://doutora_user:doutora_pass@localhost:5432/doutora
set QDRANT_HOST=localhost
set QDRANT_PORT=6333
set REDIS_URL=redis://localhost:6379
set SECRET_KEY=dev_secret_key_local
set VLLM_BASE_URL=http://localhost:8000/v1
set VLLM_API_KEY=token-xyz

echo.
echo [3/3] Iniciando API na porta 8080...
echo Acesse: http://localhost:8080/docs
echo.
venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8080
