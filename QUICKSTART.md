# ⚡ Quick Start - Doutora IA

Comece em 5 minutos!

## 1️⃣ Configure o Ambiente

```bash
# No Windows, navegue até a pasta
cd D:\doutora-ia

# Copie o .env
copy .env.example .env

# Edite o .env e adicione seu token do Hugging Face
# HF_TOKEN=seu_token_aqui
```

**Como obter HF_TOKEN:**
1. Acesse https://huggingface.co/settings/tokens
2. Crie um token com permissão de leitura
3. Copie e cole no `.env`

## 2️⃣ Inicie os Serviços

```bash
docker compose up -d
```

⏱️ Aguarde 2-3 minutos (primeiro download do modelo Llama 3 pode levar mais tempo)

## 3️⃣ Carregue Dados de Amostra

**Windows:**
```cmd
setup_sample_data.bat
```

**Linux/Mac:**
```bash
chmod +x setup_sample_data.sh
./setup_sample_data.sh
```

## 4️⃣ Gere Templates DOCX

```bash
cd api\templates\docs
python create_templates.py
cd ..\..\..
```

## 5️⃣ Verifique

```bash
# Health check
curl http://localhost:8080/health

# Deve retornar: {"status":"healthy",...}
```

## 6️⃣ Acesse!

- **Landing Page**: http://localhost:3000
- **Modo Advogado**: http://localhost:3000/advogado.html
- **API Docs**: http://localhost:8080/docs
- **Qdrant**: http://localhost:6333/dashboard

## 🧪 Teste Rápido

### Via Interface Web
1. Abra http://localhost:3000
2. Digite uma descrição: "Meu plano de saúde negou um exame urgente que meu médico pediu"
3. Clique em "Analisar Gratuitamente"
4. Veja a análise com probabilidade e estratégias

### Via API (curl)
```bash
curl -X POST http://localhost:8080/analyze_case \
  -H "Content-Type: application/json" \
  -d "{\"descricao\":\"Meu plano de saude negou cirurgia urgente\",\"detalhado\":false}"
```

## ❓ Problemas?

### Serviços não sobem
```bash
docker compose logs
```

### GPU não disponível
Edite `docker-compose.yml`, remova seção `deploy.resources` do serviço `vllm`

### Qdrant vazio
```bash
cd ingest
python build_corpus.py --sample
```

### Mais ajuda
Consulte `README.md` completo

---

**Pronto! O sistema está rodando** 🎉
