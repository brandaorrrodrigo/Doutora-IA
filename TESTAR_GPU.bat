@echo off
echo ========================================
echo TESTE DE GPU - RTX 3090
echo ========================================
echo.
echo Verificando versao do Ollama...
ollama --version
echo.
echo Se server e client estao na mesma versao 0.13.x = OK!
echo Se server ainda 0.4.7 = instalacao falhou
echo.
pause
echo.
echo Configurando variaveis de ambiente para GPU...
set OLLAMA_GPU_LAYERS=999
set OLLAMA_NUM_GPU=1
set CUDA_VISIBLE_DEVICES=0
echo Variaveis configuradas!
echo.
echo Iniciando teste de geracao...
echo (Isso vai demorar 10-30 segundos)
echo.
echo Abra outra janela CMD e execute: nvidia-smi
echo Deve mostrar GPU em 80-95%% de uso!
echo.
pause
echo.
ollama run llama3.1 "teste rapido de performance com GPU"
echo.
echo ========================================
echo TESTE CONCLUIDO!
echo ========================================
echo.
echo Se GPU estava em 80-95%% = SUCESSO! GPU ativada!
echo Se GPU estava em 1-5%% = Problema, verificar guia
echo.
pause
