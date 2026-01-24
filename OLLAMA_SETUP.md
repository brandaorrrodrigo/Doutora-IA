# OLLAMA SETUP - Doutora IA

Guia rápido para usar **Ollama** (100% local, grátis, privado) no lugar do OpenAI.

---

## ✅ JÁ ESTÁ CONFIGURADO!

O arquivo `api/.env` já está configurado para usar **Ollama**:

```bash
LLM_BASE_URL=http://host.docker.internal:11434/v1
OPENAI_API_KEY=ollama
LLM_MODEL=llama3:latest
```

---

## 🚀 COMO TESTAR

### 1. Garantir que Ollama está rodando

```bash
# Ver modelos disponíveis
ollama list

# Deve mostrar:
# llama3:latest      (4.7 GB)
# gpt-oss:20b       (13 GB)
# deepseek-r1:8b    (5.2 GB)
```

**Ollama roda automaticamente em background**, mas se precisar iniciar manualmente:

```bash
# Windows
ollama serve

# Deixar rodando
```

---

### 2. Testar Ollama diretamente

```bash
# Teste simples
ollama run llama3:latest "Olá, você é um assistente jurídico. Explique o que é LGPD em 2 frases."

# Se funcionar, Ollama está OK!
```

---

### 3. Iniciar Doutora IA

```bash
cd C:\Users\NFC\doutora-ia

# Iniciar serviços
docker-compose up -d

# Ver logs
docker-compose logs -f api
```

---

### 4. Testar Análise com Ollama

```bash
# Fazer análise de caso
curl -X POST http://localhost:8000/analyze_case \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Cliente sofreu acidente de trânsito e teve lesões graves. O outro motorista estava embriagado. Deseja processar por danos morais e materiais.",
    "detalhado": false
  }'

# Você verá nos logs:
# "Cache MISS - Calling LLM ($$): Cliente sofreu acidente..."
# E a resposta virá do OLLAMA (não OpenAI)!
```

---

## 🔄 TROCAR DE MODELO

Quer testar com um modelo diferente? É só editar `.env`:

```bash
# Usar GPT-OSS (20B - melhor qualidade, mais lento)
LLM_MODEL=gpt-oss:20b

# Usar DeepSeek R1 (8B - excelente para raciocínio)
LLM_MODEL=deepseek-r1:8b

# Depois reiniciar
docker-compose restart api
```

---

## 📊 COMPARAÇÃO DE MODELOS

### Llama 3 (4.7 GB) - PADRÃO
- ✅ **Velocidade**: Rápido (5-10s por análise)
- ✅ **Qualidade**: Boa
- ✅ **Memória**: 8 GB RAM suficiente
- 👍 **Recomendado para**: Desenvolvimento, testes rápidos

### GPT-OSS 20B (13 GB)
- ⚠️ **Velocidade**: Lento (20-40s por análise)
- ✅ **Qualidade**: Excelente
- ⚠️ **Memória**: 16+ GB RAM recomendado
- 👍 **Recomendado para**: Análises complexas, produção

### DeepSeek R1 8B (5.2 GB)
- ✅ **Velocidade**: Médio (10-15s por análise)
- ✅ **Qualidade**: Muito boa (especializado em raciocínio)
- ✅ **Memória**: 10 GB RAM suficiente
- 👍 **Recomendado para**: Análises jurídicas detalhadas

---

## 💰 ECONOMIA COM OLLAMA

### Custos com OpenAI:
- 1000 análises/dia
- ~2000 tokens por análise
- gpt-4o-mini: $0.150 por 1M tokens input
- **Custo: ~$600/mês** 💸

### Custos com Ollama:
- ∞ análises/dia
- 0 tokens pagos
- **Custo: R$ 0/mês** ✅

**Economia: 100%!** 🎉

---

## ⚡ PERFORMANCE

### Cache ainda funciona!

O cache Redis **economiza processamento** mesmo com Ollama local:

- **Sem cache**: Toda análise = 5-10s de processamento Ollama
- **Com cache**: Análises repetidas = < 50ms (do Redis)

**Cache é ainda MAIS importante com Ollama** porque economiza processamento local!

```bash
# Ver stats de cache
curl http://localhost:8000/cache/stats

# Response:
{
  "cache": {
    "hit_rate": "73.5%",
    "llm_calls_saved": 1523,
    "message": "Saved 1523 local LLM calls"
  }
}
```

---

## 🐛 TROUBLESHOOTING

### Erro: "Connection refused localhost:11434"

**Causa**: Ollama não está rodando ou Docker não consegue acessar host

**Solução 1** - Verificar Ollama:
```bash
ollama list  # Se der erro, Ollama está off

# Iniciar Ollama
ollama serve
```

**Solução 2** - Usar IP do host (se host.docker.internal não funcionar):
```bash
# Descobrir IP do host
ipconfig

# Exemplo: 192.168.1.100
# Editar api/.env:
LLM_BASE_URL=http://192.168.1.100:11434/v1
```

---

### Erro: "Model not found"

**Causa**: Modelo não está baixado

**Solução**:
```bash
# Baixar modelo
ollama pull llama3:latest

# Ou o modelo que você quer usar
ollama pull deepseek-r1:8b
```

---

### Ollama está lento

**Causa**: Modelo muito grande ou CPU fraco

**Soluções**:
- Usar modelo menor: `llama3:latest` (4.7 GB) em vez de `gpt-oss:20b` (13 GB)
- Aumentar cache hit rate para reduzir chamadas ao Ollama
- Usar GPU se disponível (Ollama detecta automaticamente)

---

### Como verificar se está usando Ollama (não OpenAI)

```bash
# Ver logs da API
docker-compose logs -f api

# Fazer análise
curl -X POST http://localhost:8000/analyze_case ...

# Nos logs você verá:
# ✅ Se estiver usando Ollama: requests para localhost:11434
# ❌ Se estiver usando OpenAI: requests para api.openai.com

# Ou verificar terminal onde ollama está rodando
# Você verá logs de requests chegando
```

---

## 🎯 MODO HÍBRIDO (Avançado)

Quer usar **Ollama para dev** e **OpenAI para produção**?

### Configurar por ambiente:

```python
# api/main.py - Adicionar lógica:

import os

ENV = os.getenv("ENV", "development")

if ENV == "production":
    # Produção: OpenAI (melhor qualidade, custo)
    llm_base_url = "https://api.openai.com/v1"
    llm_model = "gpt-4o-mini"
    llm_api_key = os.getenv("OPENAI_API_KEY")
else:
    # Dev: Ollama (grátis, local)
    llm_base_url = "http://host.docker.internal:11434/v1"
    llm_model = "llama3:latest"
    llm_api_key = "ollama"

llm_client = OpenAI(base_url=llm_base_url, api_key=llm_api_key)
```

Ou simplesmente trocar `.env` ao fazer deploy! 🚀

---

## ✅ RESUMO

**Configuração atual:**
- ✅ Ollama instalado
- ✅ 3 modelos disponíveis (llama3, gpt-oss, deepseek-r1)
- ✅ `.env` configurado para usar `llama3:latest`
- ✅ Cache Redis habilitado (economiza processamento)
- ✅ 100% grátis, 100% privado, 100% local

**Para testar:**
```bash
# 1. Garantir Ollama rodando
ollama list

# 2. Iniciar Doutora IA
cd C:\Users\NFC\doutora-ia
docker-compose up -d

# 3. Testar análise
curl -X POST http://localhost:8000/analyze_case -H "Content-Type: application/json" -d '{"descricao": "Caso de teste", "detalhado": false}'

# 4. Profit! 🎉
```

**Quer voltar para OpenAI?**
```bash
# Editar api/.env:
LLM_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sua_key_aqui
LLM_MODEL=gpt-4o-mini

# Reiniciar
docker-compose restart api
```

---

**Sistema 100% flexível! Use Ollama grátis ou OpenAI quando precisar!** 🚀
