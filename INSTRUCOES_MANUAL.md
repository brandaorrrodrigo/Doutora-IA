# 🔧 ATUALIZAÇÃO MANUAL DO OLLAMA - PASSO A PASSO

## Situação:
- Download do ZIP funcionou (1.9 GB)
- Extração funcionou
- MAS o arquivo `ollama.exe` não foi substituído (travado ou permissões)

---

## ✅ SOLUÇÃO MANUAL (5 minutos):

### 1️⃣ BAIXAR ZIP NOVAMENTE (ou usar o que já baixou)

Se ainda tem o arquivo:
```
C:\Users\NFC\AppData\Local\Temp\ollama-new.zip
```

Se não tem, baixe novamente:
```
https://github.com/ollama/ollama/releases/download/v0.13.5/ollama-windows-amd64.zip
```

Salve em: `C:\Users\NFC\Downloads\ollama-windows-amd64.zip`

---

### 2️⃣ EXTRAIR ZIP

1. Ir em Downloads
2. Clicar direito em `ollama-windows-amd64.zip`
3. "Extrair Tudo..."
4. Extrair para: `C:\Users\NFC\Downloads\ollama-new\`

---

### 3️⃣ PARAR OLLAMA COMPLETAMENTE

Abrir PowerShell **COMO ADMINISTRADOR** e executar:

```powershell
# Parar todos os processos
Get-Process | Where-Object {$_.ProcessName -like "*ollama*"} | Stop-Process -Force

# Aguardar
Start-Sleep -Seconds 3

# Verificar se parou tudo
Get-Process | Where-Object {$_.ProcessName -like "*ollama*"}
```

**Se não aparecer nada = sucesso!**

---

### 4️⃣ RENOMEAR ARQUIVO ANTIGO

No PowerShell (ainda como Admin):

```powershell
# Ir para pasta Ollama
cd "C:\Users\NFC\AppData\Local\Programs\Ollama"

# Renomear antigo
Rename-Item "ollama.exe" "ollama_ANTIGO_0.4.7.exe" -Force

# Verificar
dir
```

**Deve mostrar `ollama_ANTIGO_0.4.7.exe` e NÃO deve ter `ollama.exe`**

---

### 5️⃣ COPIAR NOVO EXECUTÁVEL

Ainda no PowerShell:

```powershell
# Copiar novo executável
Copy-Item "C:\Users\NFC\Downloads\ollama-new\ollama.exe" "C:\Users\NFC\AppData\Local\Programs\Ollama\ollama.exe" -Force

# Copiar DLLs e libraries (se houver)
Copy-Item "C:\Users\NFC\Downloads\ollama-new\lib\*" "C:\Users\NFC\AppData\Local\Programs\Ollama\lib\" -Recurse -Force -ErrorAction SilentlyContinue

# Verificar
dir
```

**Deve mostrar `ollama.exe` com data de HOJE**

---

### 6️⃣ TESTAR VERSÃO

```powershell
.\ollama.exe --version
```

**Deve mostrar:**
```
ollama version is 0.13.5
```

✅ **SE MOSTRAR 0.13.5 = SUCESSO!**

---

### 7️⃣ TESTAR GPU

Abrir NOVO PowerShell (não admin) e executar:

```powershell
# Definir variáveis GPU
$env:OLLAMA_GPU_LAYERS = "999"
$env:OLLAMA_NUM_GPU = "1"
$env:CUDA_VISIBLE_DEVICES = "0"

# Testar geração
ollama run llama3.1 "teste rápido de GPU"
```

**Enquanto roda, em OUTRA janela PowerShell:**
```powershell
nvidia-smi
```

**GPU deve mostrar 80-95% de uso!** ✅

---

## 🎉 RESULTADO ESPERADO:

### ANTES:
- Server: 0.4.7
- GPU: 1-5% (ociosa)
- Velocidade: 5 tokens/s

### DEPOIS:
- Server: 0.13.5 ✅
- GPU: 80-95% (trabalhando!) ✅
- Velocidade: 50-150 tokens/s ✅

---

## ⚠️ SE DER ERRO:

### "Access Denied" ao renomear/copiar:
- Fechar TODAS as janelas CMD/PowerShell
- Abrir Task Manager (Ctrl+Shift+Esc)
- Matar processo "Ollama" se aparecer
- Tentar novamente

### "File in use":
- Reiniciar PC (última opção)
- Executar passos 3-6 novamente

---

## 📞 PRECISA DE AJUDA?

Cole aqui:
1. Qual passo deu erro
2. Mensagem de erro completa
3. Output do comando que falhou

Vou te ajudar! 🚀
