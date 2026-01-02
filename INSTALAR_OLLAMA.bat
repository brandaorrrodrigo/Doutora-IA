@echo off
echo ========================================
echo INSTALADOR OLLAMA - ATIVAR GPU
echo ========================================
echo.
echo 1. O instalador vai abrir em alguns segundos
echo 2. Clique em "Sim" se pedir permissoes de administrador
echo 3. Siga o assistente: Next -> Next -> Finish
echo 4. Aguarde instalacao completar
echo.
pause
echo.
echo Executando instalador...
start "" "%USERPROFILE%\Downloads\OllamaSetup.exe"
echo.
echo Aguarde a instalacao completar e pressione qualquer tecla...
pause
echo.
echo Verificando versao instalada...
timeout /t 3
ollama --version
echo.
echo Se mostrar versao 0.13.x ou superior, instalacao foi bem-sucedida!
echo.
pause
