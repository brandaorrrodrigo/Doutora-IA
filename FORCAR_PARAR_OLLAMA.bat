@echo off
echo ========================================
echo FORCAR PARADA DO OLLAMA - ADMIN REQUIRED
echo ========================================
echo.
echo Verificando se rodando como Admin...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERRO: Nao esta rodando como Administrador!
    echo.
    echo Por favor:
    echo 1. Feche esta janela
    echo 2. Clique DIREITO neste arquivo
    echo 3. Escolha "Executar como Administrador"
    echo.
    pause
    exit /b 1
)
echo OK! Rodando como Admin!
echo.
echo Matando todos os processos Ollama...
echo.
taskkill /F /IM "ollama.exe" 2>nul
taskkill /F /IM "ollama app.exe" 2>nul
taskkill /F /IM "ollama_llama_server.exe" 2>nul
echo.
echo Matando processo especifico PID 690152...
taskkill /F /PID 690152 2>nul
echo.
echo Procurando servicos Ollama...
sc query | findstr /I "ollama"
echo.
echo Parando servico se existir...
sc stop OllamaService 2>nul
net stop "Ollama Service" 2>nul
echo.
timeout /t 3
echo.
echo Verificando se parou TUDO...
tasklist | findstr /I "ollama"
echo.
if %errorlevel% equ 0 (
    echo ATENCAO: Ainda tem processos Ollama rodando!
    echo Vai tentar matar tudo de novo...
    wmic process where "name like '%%ollama%%'" delete 2>nul
    timeout /t 2
    tasklist | findstr /I "ollama"
) else (
    echo.
    echo ========================================
    echo SUCESSO! Todos os processos Ollama parados!
    echo ========================================
)
echo.
echo Agora execute: INSTALAR_OLLAMA.bat (como Admin)
echo.
pause
