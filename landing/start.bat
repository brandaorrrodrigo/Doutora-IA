@echo off
echo ========================================
echo Iniciando Doutora IA Landing Page
echo ========================================
echo.

cd /d D:\doutora-ia\landing

echo [1/4] Verificando Node.js...
node --version
if errorlevel 1 (
    echo ERRO: Node.js nao encontrado!
    echo Instale em: https://nodejs.org
    pause
    exit /b 1
)

echo.
echo [2/4] Verificando dependencias...
if not exist "node_modules" (
    echo Instalando dependencias pela primeira vez...
    call npm install
)

echo.
echo [3/4] Limpando cache...
if exist ".next" (
    echo Removendo cache antigo...
    rmdir /s /q .next 2>nul
)

echo.
echo [4/4] Iniciando servidor de desenvolvimento...
echo.
echo ========================================
echo Aguarde a mensagem "Ready" aparecer
echo Depois acesse o endereco que aparecer
echo (geralmente http://localhost:3000)
echo.
echo Pressione Ctrl+C para parar o servidor
echo ========================================
echo.

npm run dev

pause
