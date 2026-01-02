@echo off
echo ========================================
echo DIAGNOSTICO OLLAMA - Encontrar instalacoes
echo ========================================
echo.
echo 1. Verificando versoes...
ollama --version
echo.
echo 2. Localizando executavel atual...
where ollama
echo.
echo 3. Procurando ollama.exe no sistema...
dir /s /b "C:\Program Files\Ollama\ollama.exe" 2>nul
dir /s /b "C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe" 2>nul
dir /s /b "C:\Users\%USERNAME%\AppData\Local\Ollama\ollama.exe" 2>nul
echo.
echo 4. Verificando propriedades do executavel atual...
where ollama > temp_path.txt
set /p OLLAMA_PATH=<temp_path.txt
echo Caminho: %OLLAMA_PATH%
echo.
echo Informacoes do arquivo:
dir "%OLLAMA_PATH%"
echo.
echo 5. Verificando PATH do sistema...
echo %PATH% | findstr /I "ollama"
echo.
echo 6. Procurando todas as versoes no disco C:...
echo (Isso pode demorar 30-60 segundos...)
dir /s /b "C:\ollama.exe" 2>nul | findstr /I "ollama.exe"
echo.
del temp_path.txt 2>nul
echo ========================================
echo DIAGNOSTICO COMPLETO
echo ========================================
echo.
pause
