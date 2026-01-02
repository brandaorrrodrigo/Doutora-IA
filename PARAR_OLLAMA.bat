@echo off
echo ========================================
echo PARAR OLLAMA - Preparar para atualizacao
echo ========================================
echo.
echo IMPORTANTE: Execute como ADMINISTRADOR!
echo (Clique direito -> Executar como Administrador)
echo.
pause
echo.
echo Parando todos os processos Ollama...
taskkill /F /IM "ollama.exe" 2>nul
taskkill /F /IM "ollama app.exe" 2>nul
taskkill /F /IM "ollama_llama_server.exe" 2>nul
echo.
echo Aguardando processos finalizarem...
timeout /t 3
echo.
echo Verificando se ainda tem processos rodando...
tasklist | findstr /I "ollama"
echo.
echo Se nao aparecer nada acima = Ollama parado com sucesso!
echo Se ainda aparecer processos = Precisa reiniciar PC
echo.
echo Agora execute: INSTALAR_OLLAMA.bat (como Admin)
echo.
pause
