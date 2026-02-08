@echo off
echo ========================================
echo  DOUTORA IA - INICIANDO API LOCAL
echo ========================================
echo.

cd /d D:\doutora-ia\api

echo [1/3] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo [2/3] Configurando variaveis de ambiente...
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/doutora_ia
set QDRANT_HOST=localhost
set SECRET_KEY=dev_secret_key_local_test
set PYTHONUNBUFFERED=1

echo.
echo [3/3] Iniciando API FastAPI...
echo API rodando em: http://localhost:8080
echo Pressione CTRL+C para parar
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
