@echo off
echo ========================================
echo ATUALIZACAO MANUAL DO OLLAMA
echo ========================================
echo.
echo Este script vai:
echo 1. Baixar o executavel Ollama mais recente
echo 2. Fazer backup da versao antiga
echo 3. Substituir pelo novo
echo.
echo IMPORTANTE: Execute como ADMINISTRADOR!
echo.
pause
echo.
echo Verificando Admin...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Precisa rodar como Admin!
    pause
    exit /b 1
)
echo OK! Admin confirmado.
echo.
echo Parando Ollama...
taskkill /F /IM "ollama.exe" 2>nul
taskkill /F /IM "ollama app.exe" 2>nul
timeout /t 2
echo.
echo Fazendo backup da versao antiga...
copy "C:\Users\NFC\AppData\Local\Programs\Ollama\ollama.exe" "C:\Users\NFC\AppData\Local\Programs\Ollama\ollama.exe.backup" /Y
echo Backup criado: ollama.exe.backup
echo.
echo Baixando versao mais recente...
echo (Isso pode demorar 2-5 minutos - arquivo ~1GB)
echo.
curl -L "https://github.com/ollama/ollama/releases/download/v0.5.4/ollama-windows-amd64.exe" -o "%TEMP%\ollama-new.exe"
echo.
if exist "%TEMP%\ollama-new.exe" (
    echo Download concluido!
    echo.
    echo Substituindo executavel...
    copy "%TEMP%\ollama-new.exe" "C:\Users\NFC\AppData\Local\Programs\Ollama\ollama.exe" /Y
    echo.
    echo Limpando arquivo temporario...
    del "%TEMP%\ollama-new.exe"
    echo.
    echo ========================================
    echo ATUALIZACAO CONCLUIDA!
    echo ========================================
    echo.
    echo Verificando versao...
    "C:\Users\NFC\AppData\Local\Programs\Ollama\ollama.exe" --version
    echo.
    echo Se mostrar v0.5.x = SUCESSO!
    echo.
) else (
    echo.
    echo ERRO: Download falhou!
    echo Tente baixar manualmente de:
    echo https://github.com/ollama/ollama/releases/latest
    echo.
)
echo.
pause
