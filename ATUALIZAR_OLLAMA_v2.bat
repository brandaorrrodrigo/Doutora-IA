@echo off
echo ========================================
echo ATUALIZACAO MANUAL OLLAMA v0.13.5
echo ========================================
echo.
echo Versao atual: 0.4.7
echo Versao nova:  0.13.5 (com suporte GPU melhorado)
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
echo Parando todos os processos Ollama...
taskkill /F /IM "ollama.exe" 2>nul
taskkill /F /IM "ollama app.exe" 2>nul
taskkill /F /IM "ollama_llama_server.exe" 2>nul
timeout /t 3
echo.
echo Fazendo backup da versao antiga...
if exist "C:\Users\NFC\AppData\Local\Programs\Ollama\ollama.exe" (
    copy "C:\Users\NFC\AppData\Local\Programs\Ollama\ollama.exe" "C:\Users\NFC\AppData\Local\Programs\Ollama\ollama_OLD_0.4.7.exe" /Y
    echo Backup criado: ollama_OLD_0.4.7.exe
)
echo.
echo Baixando Ollama v0.13.5 para Windows x64...
echo URL: https://github.com/ollama/ollama/releases/download/v0.13.5/ollama-windows-amd64.zip
echo Tamanho: ~300-500 MB
echo (Aguarde 1-3 minutos...)
echo.
curl -L "https://github.com/ollama/ollama/releases/download/v0.13.5/ollama-windows-amd64.zip" -o "%TEMP%\ollama-new.zip"
echo.
if exist "%TEMP%\ollama-new.zip" (
    echo Download concluido!
    echo.
    echo Extraindo arquivo...
    powershell -Command "Expand-Archive -Path '%TEMP%\ollama-new.zip' -DestinationPath '%TEMP%\ollama-extracted' -Force"
    echo.
    echo Substituindo executavel...
    if exist "%TEMP%\ollama-extracted\ollama.exe" (
        copy "%TEMP%\ollama-extracted\ollama.exe" "C:\Users\NFC\AppData\Local\Programs\Ollama\ollama.exe" /Y
        echo.
        echo Copiando arquivos adicionais se existirem...
        xcopy "%TEMP%\ollama-extracted\*.*" "C:\Users\NFC\AppData\Local\Programs\Ollama\" /Y /Q 2>nul
        echo.
        echo Limpando arquivos temporarios...
        del "%TEMP%\ollama-new.zip" 2>nul
        rd /s /q "%TEMP%\ollama-extracted" 2>nul
        echo.
        echo ========================================
        echo ATUALIZACAO CONCLUIDA!
        echo ========================================
        echo.
        echo Verificando versao...
        timeout /t 2
        "C:\Users\NFC\AppData\Local\Programs\Ollama\ollama.exe" --version
        echo.
        echo Se mostrar v0.13.x = SUCESSO! GPU ready!
        echo.
    ) else (
        echo ERRO: Arquivo nao encontrado apos extracao!
        echo Verifique manualmente em %TEMP%\ollama-extracted\
    )
) else (
    echo.
    echo ERRO: Download falhou!
    echo.
    echo Tente baixar manualmente:
    echo https://github.com/ollama/ollama/releases/download/v0.13.5/ollama-windows-amd64.zip
    echo.
    echo Depois extraia e copie ollama.exe para:
    echo C:\Users\NFC\AppData\Local\Programs\Ollama\
    echo.
)
echo.
pause
