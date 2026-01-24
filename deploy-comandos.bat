@echo off
echo ========================================
echo DEPLOY DOUTORA IA - RAILWAY
echo ========================================
echo.

cd /d "%~dp0"

echo [1/7] Login no Railway...
echo Execute: railway login
echo Pressione ENTER apos fazer login no navegador
pause
railway login
echo.

echo [2/7] Inicializando projeto...
railway init
echo.

echo [3/7] Adicionando PostgreSQL...
railway add
echo Escolha: PostgreSQL
pause
echo.

echo [4/7] Adicionando Redis...
railway add
echo Escolha: Redis
pause
echo.

echo [5/7] Configurando variaveis...
echo.
echo IMPORTANTE: Edite railway-vars.txt e adicione sua OPENAI_API_KEY
echo Depois copie e cole o comando no terminal
echo.
notepad railway-vars.txt
pause
echo.

echo [6/7] Fazendo deploy...
railway up
echo.

echo [7/7] Configurando dominio...
railway domain
echo.

echo ========================================
echo DEPLOY COMPLETO!
echo ========================================
echo.
echo Dashboard: https://railway.app/dashboard
echo.
echo Proximos passos:
echo 1. Testar: railway run curl localhost:8000/health
echo 2. Ver logs: railway logs
echo 3. Abrir dashboard: railway open
echo.
pause
