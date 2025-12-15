# Doutora IA - Sistema de Análise Jurídica com IA

Sistema completo de análise jurídica, geração de peças e gestão de leads para advogados, baseado em IA e RAG (Retrieval-Augmented Generation).

## 🎯 Funcionalidades

### Para Usuários
- **Triagem Gratuita**: Análise inicial do caso com tipificação, estratégias e probabilidade
- **Relatório Premium (R$ 7)**: PDF completo com análise detalhada, custos, prazos, checklist e rascunho de petição
- **Conexão com Advogados**: Sistema de leads qualificados

### Para Advogados
- **Pesquisa Jurídica Unificada**: Busca em leis, súmulas, jurisprudência, regulatório e doutrina
- **Gerador de Peças**: Petições iniciais, contestações e recursos em DOCX/PDF
- **Sistema de Leads**: Captação de clientes qualificados com rodízio inteligente
- **Planos Flexíveis**: Pesquisa, Leads, Redação, Pro e Full

## 🏗️ Arquitetura

```
doutora-ia/
├── docker-compose.yml          # Orquestração de serviços
├── api/                        # FastAPI backend
│   ├── main.py                # Endpoints principais
│   ├── models.py              # Models SQLAlchemy
│   ├── schemas.py             # Pydantic schemas
│   ├── rag.py                 # Sistema RAG com Qdrant
│   ├── prompts.py             # Templates de prompts
│   ├── services/              # Serviços auxiliares
│   │   ├── pdf.py            # Geração de PDFs
│   │   ├── citations.py      # Gerenciamento de citações
│   │   ├── payments.py       # Integração Mercado Pago
│   │   ├── queues.py         # Filas de leads
│   │   └── auth.py           # Autenticação
│   └── templates/            # Templates HTML/DOCX
├── ingest/                    # Scripts de ingestão
│   ├── pdf_to_md.py          # Converter PDFs
│   ├── normalize.py          # Normalizar dados
│   └── build_corpus.py       # Construir corpus RAG
├── worker/                    # Worker de background
│   └── worker.py             # Tarefas assíncronas
├── web/                       # Interface web
│   └── public/               # HTML/JS estático
├── migrations/               # SQL migrations
└── data/                     # Dados do corpus
    ├── raw/                  # PDFs originais
    ├── clean/                # Markdown limpo
    └── json/                 # JSON normalizado
```

## 🐳 Serviços Docker

- **vllm**: Llama 3 8B Instruct (OpenAI-compatible API)
- **qdrant**: Banco de vetores para RAG
- **db**: PostgreSQL 16
- **redis**: Fila de tarefas e cache
- **api**: FastAPI (porta 8080)
- **worker**: Processamento em background
- **web**: Interface web (porta 3000)

## 🚀 Quick Start

### 1. Pré-requisitos

- Docker e Docker Compose
- NVIDIA GPU (para vLLM) ou CPU (modo compatível)
- 16GB+ RAM recomendado
- Python 3.11+ (para desenvolvimento local)

### 2. Configuração

```bash
# Clone ou navegue até o diretório
cd doutora-ia

# Copie o arquivo de ambiente
cp .env.example .env

# Edite o .env com suas configurações
# IMPORTANTE: Configure HF_TOKEN para baixar o modelo Llama 3
```

### 3. Configurar `.env`

Edite `D:\doutora-ia\.env` e configure:

```env
# Obrigatório: Token do Hugging Face para baixar Llama 3
HF_TOKEN=seu_token_aqui

# Opcional: Mercado Pago (para pagamentos reais)
MERCADO_PAGO_ACCESS_TOKEN=seu_token_mp
NEXT_PUBLIC_MERCADO_PAGO_PUBLIC_KEY=sua_public_key_mp

# Gerado automaticamente, mas pode customizar
SECRET_KEY=sua_secret_key_segura
VLLM_API_KEY=token-xyz
```

### 4. Iniciar os Serviços

```bash
# Iniciar todos os serviços
docker compose up -d

# Verificar status
docker compose ps

# Ver logs
docker compose logs -f api
```

### 5. Setup de Dados de Amostra

**Windows:**
```cmd
setup_sample_data.bat
```

**Linux/Mac:**
```bash
chmod +x setup_sample_data.sh
./setup_sample_data.sh
```

Ou manualmente:
```bash
cd ingest
python build_corpus.py --sample
```

### 6. Gerar Templates DOCX

```bash
cd api/templates/docs
python create_templates.py
```

### 7. Acessar a Aplicação

- **Web Interface**: http://localhost:3000
- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## 📝 Usar o Sistema

### Triagem de Caso (Usuário)

1. Acesse http://localhost:3000
2. Preencha a descrição do caso (mínimo 50 caracteres)
3. Clique em "Analisar Gratuitamente"
4. Receba análise com tipificação, probabilidade e estratégias
5. Opcionalmente, compre relatório premium (R$ 7)

### Pesquisa Jurídica (Advogado)

1. Acesse http://localhost:3000/advogado.html
2. Use a busca (Ctrl+K)
3. Filtre por tipo, área, tribunal
4. Adicione citações ao carrinho
5. Gere peça com citações selecionadas

## 🔌 Endpoints da API

### Público

```bash
# Analisar caso
curl -X POST http://localhost:8080/analyze_case \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Meu plano de saúde negou um exame urgente...",
    "detalhado": false,
    "user_email": "usuario@email.com"
  }'

# Buscar legislação/jurisprudência
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "PIX fraude responsabilidade banco",
    "tipo": "juris",
    "limit": 10
  }'

# Gerar peça
curl -X POST http://localhost:8080/compose \
  -H "Content-Type: application/json" \
  -d @compose_request.json

# Health check
curl http://localhost:8080/health
```

### Advogados

```bash
# Registrar advogado
curl -X POST http://localhost:8080/lawyers/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "advogado@example.com",
    "name": "Dr. João Silva",
    "oab": "SP123456",
    "phone": "11999999999",
    "cpf": "12345678900",
    "password": "senha123",
    "areas": ["familia", "consumidor"],
    "cities": ["São Paulo"],
    "states": ["SP"],
    "bio": "Advogado especialista em..."
  }'

# Assinar plano
curl -X POST http://localhost:8080/lawyers/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "lawyer_id": 1,
    "plan_id": 4
  }'

# Ver leads disponíveis
curl http://localhost:8080/lawyers/feed?lawyer_id=1
```

## 📊 Dados de Amostra

O sistema vem com corpus de amostra contendo:

- **2 Leis**: CDC Art. 14, CPC Art. 300
- **2 Súmulas**: STJ 385, STJ 309
- **2 Jurisprudências**: Leading cases sobre PIX e Plano de Saúde
- **2 Normas Regulatórias**: ANS Rol, BACEN PIX
- **2 Doutrinas**: Artigos sobre responsabilidade bancária e cobertura de planos

Localização: `D:\doutora-ia\data\json\`

## 🗄️ Banco de Dados

### Acessar PostgreSQL

```bash
docker compose exec db psql -U postgres -d doutora

# Ver planos disponíveis
SELECT * FROM plans;

# Ver casos criados
SELECT id, area, probability, status FROM cases;
```

### Schema Principal

- `users`: Usuários finais
- `lawyers`: Advogados cadastrados
- `plans`: Planos para advogados
- `subscriptions`: Assinaturas ativas
- `cases`: Casos analisados
- `referrals`: Leads enviados a advogados
- `payments`: Pagamentos de relatórios
- `citations_log`: Log de citações usadas
- `cost_table`: Tabela de custos por UF/área
- `events`: Eventos para analytics

## 🤖 Ingestão de Dados Customizados

### 1. Preparar Dados

Crie arquivos JSON em `data/json/` seguindo o schema:

**lei.json:**
```json
[
  {
    "titulo": "Lei 8.078/90 - Art. 14",
    "artigo": "Art. 14",
    "texto": "O fornecedor de serviços responde...",
    "area": "consumidor",
    "orgao": "Congresso Nacional",
    "data": "1990-09-11",
    "vigencia_inicio": "1991-03-11",
    "vigencia_fim": null,
    "fonte_url": "http://..."
  }
]
```

### 2. Ingerir

```bash
cd ingest
python build_corpus.py --ingest ../data/json
```

### 3. Converter PDFs (Opcional)

```bash
# Converter um PDF
python pdf_to_md.py caminho/para/documento.pdf

# Converter pasta inteira
python pdf_to_md.py caminho/para/pasta/
```

## 🧪 Testes

### Teste de Análise de Caso

```bash
curl -X POST http://localhost:8080/analyze_case \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Meu ex-marido está atrasado há 3 meses com a pensão alimentícia dos nossos dois filhos. O valor fixado foi R$ 1.500 por mês. Ele trabalha com carteira assinada e ganha aproximadamente R$ 5.000. Preciso entrar com execução de alimentos.",
    "detalhado": true,
    "user_email": "teste@example.com"
  }' | python -m json.tool
```

### Teste de Busca

```bash
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "pensão alimentícia execução prisão",
    "tipo": "sumula",
    "limit": 5
  }' | python -m json.tool
```

## 🔧 Troubleshooting

### Serviços não sobem

```bash
# Ver logs de erro
docker compose logs

# Recriar containers
docker compose down -v
docker compose up -d --build
```

### vLLM não inicia (GPU)

Se não tiver GPU NVIDIA:
1. Edite `docker-compose.yml`
2. Remova a seção `deploy.resources.reservations.devices`
3. Adicione `--device cpu` nos args do vLLM

Ou use API externa (OpenAI, Anthropic):
- Altere `VLLM_BASE_URL` no `.env`
- Aponte para API externa

### Qdrant vazio

```bash
# Verificar coleções
curl http://localhost:6333/collections

# Re-ingerir dados
cd ingest
python build_corpus.py --sample
```

### API retorna 500

```bash
# Ver logs detalhados
docker compose logs -f api

# Verificar conexões
docker compose exec api curl http://qdrant:6333/health
docker compose exec api curl http://vllm:8000/health
```

## 📦 Deploy em Produção

### Checklist

- [ ] Altere `SECRET_KEY` no `.env`
- [ ] Configure `MERCADO_PAGO_ACCESS_TOKEN` real
- [ ] Configure domínio em `BASE_URL` e `NEXT_PUBLIC_API_URL`
- [ ] Use HTTPS (reverse proxy com nginx/traefik)
- [ ] Configure backup do PostgreSQL
- [ ] Configure backup dos volumes do Qdrant
- [ ] Limite origins no CORS (`main.py`)
- [ ] Configure monitoramento (Sentry, Datadog, etc)
- [ ] Configure rate limiting
- [ ] Use senha forte para PostgreSQL
- [ ] Configure SSL para PostgreSQL

### Variáveis de Produção

```env
# Produção
BASE_URL=https://doutoraia.com.br
NEXT_PUBLIC_API_URL=https://api.doutoraia.com.br
SECRET_KEY=gere_uma_chave_segura_aqui
POSTGRES_PASSWORD=senha_super_segura
```

## 📄 Licença e Compliance

### LGPD

O sistema implementa:
- Opt-out de comunicações
- Direito ao esquecimento (soft delete de usuários)
- Criptografia de senhas (bcrypt)
- Logs de acesso a dados sensíveis

### Disclaimer Legal

**IMPORTANTE**: Este sistema é informativo e NÃO substitui consulta com advogado. Não há garantia de êxito em processos judiciais.

Todos os relatórios e peças incluem disclaimer obrigatório.

## 🆘 Suporte

- **Issues**: https://github.com/seu-usuario/doutora-ia/issues
- **Documentação da API**: http://localhost:8080/docs
- **Email**: suporte@doutoraia.com.br

## 🎉 Checklist de Aceite do MVP

- [x] Containers sobem com `docker compose up`
- [x] `/health` retorna status `healthy`
- [x] `/analyze_case` analisa caso e retorna 8 seções + citações
- [x] `/report` gera PDF com capa, sumário e carimbo de data
- [x] `/search` busca e retorna citações com ranking
- [x] `/compose` gera DOCX com template e citações
- [x] Landing page abre em http://localhost:3000
- [x] Modo advogado abre em http://localhost:3000/advogado.html
- [x] Dados de amostra são ingeridos no Qdrant
- [x] Planos são criados no banco de dados
- [x] Todas as citações têm ID, órgão, data e link
- [x] Disclaimer presente em todos os outputs

## 🚀 Próximos Passos

### MVP+
- [ ] Integração real com Mercado Pago
- [ ] Sistema de autenticação completo (JWT)
- [ ] Dashboard para advogados
- [ ] Analytics e métricas
- [ ] Testes automatizados
- [ ] CI/CD pipeline

### Expansão
- [ ] Mais áreas do direito (trabalhista, previdenciário, etc)
- [ ] Integração com tribunais (PJe, eProc)
- [ ] Chat com IA jurídica
- [ ] Análise de contratos
- [ ] Geração de pareceres
- [ ] White-label para escritórios

---

**Desenvolvido com ❤️ para democratizar o acesso à justiça**
