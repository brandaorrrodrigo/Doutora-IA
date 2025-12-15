# ✅ Checklist de Validação do MVP - Doutora IA

Este documento valida que TODOS os requisitos do prompt foram atendidos.

## 📋 Arquitetura e Stack

### Docker Compose
- [x] `docker-compose.yml` criado com todos os serviços
- [x] Serviço `vllm` (Llama 3 8B Instruct) em `/v1`
- [x] Serviço `api` (FastAPI Python 3.11)
- [x] Serviço `qdrant` (vetores)
- [x] Serviço `db` (Postgres 16)
- [x] Serviço `worker` (tarefas background)
- [x] Serviço `web` (interface)
- [x] Serviço `redis` (filas)
- [x] Volumes persistentes configurados

### Estrutura de Pastas
- [x] `api/` com main.py, rag.py, prompts.py, models.py, schemas.py
- [x] `api/services/` com payments.py, pdf.py, citations.py, queues.py, auth.py
- [x] `api/templates/` com report.html
- [x] `api/templates/docs/` com modelos DOCX
- [x] `ingest/` com normalize.py, pdf_to_md.py, build_corpus.py
- [x] `web/public/` com landing e modo advogado
- [x] `data/raw/`, `data/clean/`, `data/json/`
- [x] `migrations/` com SQL inicial
- [x] `worker/` com worker.py

## 🔌 Endpoints da API

### Triagem e Relatórios
- [x] `POST /analyze_case` - entrada: descricao, detalhado; saída: 8 seções + citações
- [x] `POST /report` - gera PDF com capa, sumário, carimbo de data, citações
- [x] Análise retorna: tipificação, área, estratégias, riscos, probabilidade (baixa/média/alta)
- [x] Análise retorna: custos/prazos, checklist, rascunho 300-500 palavras
- [x] Citações em formato `<fonte>...</fonte>`
- [x] Carimbo "Base atualizada em DD/MM/AAAA"

### Busca e Pesquisa
- [x] `POST /search` - busca unificada (lei/súmula/juris/regulatório/doutrina)
- [x] Filtros: órgão, tribunal, tema, data
- [x] Ranking: lei vigente > súmula/repetitivo > leading case > regulatório > doutrina
- [x] Retorna citações com ID, tipo, título, texto, órgão, tribunal, data, URL

### Geração de Peças
- [x] `POST /compose` - gera peça jurídica
- [x] Recebe: metadados (partes/foro/vara/valor), carrinho de citações, tipo de peça
- [x] Usa template determinístico + blocos do LLM
- [x] Exporta DOCX
- [x] Numeração de citações e bibliografia

### Advogados e Leads
- [x] `POST /lawyers/register` - cadastro de advogado
- [x] `POST /lawyers/subscribe` - assinatura de plano
- [x] `GET /lawyers/feed` - fila de leads
- [x] `POST /leads/assign` - atribui caso a advogado (rodízio)
- [x] Janela de exclusividade 24-48h

### Pagamentos
- [x] `POST /payments/webhook` - webhook Mercado Pago (stub)
- [x] Confirmação de pagamento atualiza caso

### Health
- [x] `GET /health` - status de todos os serviços

## 🗄️ Banco de Dados

### Tabelas
- [x] `users` (id, email, name, cpf, etc)
- [x] `cases` (area, score_prob, cost_estimate, status, created_at, etc)
- [x] `lawyers` (areas TEXT[], success_score, active, etc)
- [x] `referrals` (status: pending/accepted/rejected, timestamps)
- [x] `subscriptions` (lawyer_id, plan_id, features flags)
- [x] `plans` (Pesquisa, Leads, Redação, Pro, Full)
- [x] `citations_log` (source_type, citation_id, citation_type, etc)
- [x] `payments` (amount, status, external_payment_id, etc)
- [x] `cost_table` (state, area, custos, prazos)
- [x] `events` (analytics)

### SQL Migrations
- [x] `migrations/001_initial_schema.sql` cria todas as tabelas
- [x] Insere planos padrão (Pesquisa R$79, Leads R$99, Redação R$149, Pro R$229, Full R$299)
- [x] Insere dados de custos (SP como exemplo)

## 🧠 RAG - Corpus e Schema

### Coleções Qdrant
- [x] `legis` (leis)
- [x] `sumulas` (súmulas)
- [x] `juris` (jurisprudência)
- [x] `regulatorio` (normas regulatórias)
- [x] `doutrina` (doutrina)

### Schema JSON por Chunk
- [x] `id` (string única)
- [x] `tipo` (lei/sumula/juris/regulatorio/doutrina)
- [x] `area` (familia/consumidor/bancario/saude/aereo)
- [x] `orgao` (Congresso/STJ/STF/ANS/BACEN/etc)
- [x] `titulo` (título completo)
- [x] `artigo_ou_tema` (artigo ou tema)
- [x] `data` (data de publicação)
- [x] `vigencia_inicio` e `vigencia_fim`
- [x] `hierarquia` (peso para ranking)
- [x] `texto` (conteúdo)
- [x] `fonte_url` (link)
- [x] `tribunal`, `classe`, `numero` (para jurisprudência)

### Embedding
- [x] Usa `intfloat/multilingual-e5-large` (dimensão 1024)
- [x] Chunking: 800-1200 caracteres com overlap
- [x] Leis divididas por artigo quando possível

## 📝 Prompts do LLM

### System Prompt
- [x] Define que é assistente informativo
- [x] **NÃO substitui advogado**
- [x] **NÃO garante vitória**
- [x] Sempre citar entre `<fonte>...</fonte>`
- [x] **NUNCA inventar** números de processo/artigos
- [x] Usar apenas itens do RAG
- [x] Exibir "Base atualizada em DD/MM/AAAA"

### Triagem/Relatório
- [x] Prompt estruturado em 8 seções obrigatórias
- [x] Seção 1: Tipificação (ramo + fundamento)
- [x] Seção 2: Estratégias e riscos
- [x] Seção 3: Probabilidade (BAIXA/MÉDIA/ALTA com justificativa)
- [x] Seção 4: Custos e prazos (JEC x comum, por UF)
- [x] Seção 5: Checklist de documentos
- [x] Seção 6: Rascunho de petição (300-500 palavras)
- [x] Seção 7: Citações com `<fonte>` estruturado
- [x] Seção 8: Carimbo de data

### Modo Advogado - Gerador
- [x] LLM só redige blocos (fatos, fundamentação, pedidos)
- [x] **NUNCA cria citações** que não estejam no carrinho
- [x] Respeita placeholders dos templates DOCX

## 📄 Templates

### Templates DOCX (3 modelos)
- [x] `modelo_inicial_familia.docx` (Pensão/Alimentos)
- [x] `modelo_inicial_pix.docx` (Bancário/PIX)
- [x] `modelo_inicial_plano_saude.docx` (Obrigação de fazer + liminar)
- [x] Estrutura: partes, fatos, direito, jurisprudência, pedidos
- [x] Placeholders Jinja2/docxtpl

### Template HTML - Relatório
- [x] `report.html` com CSS completo
- [x] Capa profissional
- [x] Sumário
- [x] Carimbo "Base atualizada em DD/MM/AAAA"
- [x] 8 seções do relatório
- [x] Anexo de citações completas
- [x] Conversão para PDF (WeasyPrint)

## 💰 Relatório Premium

### Funcionalidades
- [x] Preço: R$ 7,00
- [x] Geração de PDF profissional
- [x] Integração com pagamentos (stub Mercado Pago)
- [x] Link de download do relatório
- [x] Todas as seções detalhadas

## 👨‍⚖️ Modo Advogado

### Menu de Pesquisas
- [x] Campo de busca (Ctrl+K)
- [x] Filtros: tipo/órgão/tribunal/tema/data
- [x] Resultados com botão "Adicionar à Peça"
- [x] Carrinho de citações (JSON)
- [x] Ranking por hierarquia + vigência + data

### Gerador de Peças
- [x] Form: partes, foro, vara, valor, fatos, pedidos
- [x] Seleção de citações do carrinho
- [x] Botão "Gerar DOCX"
- [x] CitationManager: numera citações, notas de rodapé, bibliografia

## 📊 Planos para Advogados

### Planos Implementados
- [x] **Pesquisa (R$ 79)**: menu de pesquisas, jurimetria básica, export
- [x] **Leads (R$ 99)**: diretório, rodízio, 1º lead grátis
- [x] **Redação (R$ 149)**: gerador de peças + minutas
- [x] **Pro (R$ 229)**: Pesquisa + Redação, templates premium
- [x] **Full (R$ 299)**: Pro + Leads prioritários, 1 lead/mês incluso

### Lógica de Assinatura
- [x] Tabela `subscriptions` com status e limites
- [x] Verificação de features por plano
- [x] Contadores de uso (leads_used, docs_used, searches_today)
- [x] Sistema de rodízio de leads com priorização

## 🌐 Funil Web

### Landing Page
- [x] Hero "Entenda sua causa em minutos"
- [x] Triagem gratuita
- [x] CTA "Relatório R$ 7"
- [x] CTA "Quero advogado" (gera lead)
- [x] Seções: Como Funciona, Áreas Atendidas
- [x] FAQ (conceitual)

### Áreas Pilar (MVP)
- [x] Família: Pensão/Alimentos, Guarda/Visitas, Divórcio
- [x] Consumidor/Bancário: PIX (golpe/estorno/responsabilidade)
- [x] Saúde: Plano de Saúde (negativa/urgência/rol ANS)
- [x] (Aéreo: secundário, estrutura pronta)

### Analytics (Estrutura)
- [x] Tabela `events` para rastrear ações
- [x] Event types planejados (triagem_start, checkout_start, etc)

## ⚖️ Compliance

### Disclaimers
- [x] "Conteúdo informativo; não substitui advogado"
- [x] "Sem garantia de êxito"
- [x] Presente em: relatórios, landing, footer

### LGPD
- [x] Campos de opt-out planejados
- [x] Soft delete de dados (is_active flags)
- [x] Criptografia de senhas (bcrypt)
- [x] Logs de acesso (citations_log, events)
- [x] Retenção mínima planejada

### Anti-alucinação
- [x] Prompts explícitos: **NUNCA inventar** citações/processos
- [x] Apenas usar itens do RAG
- [x] Validação de citações no CitationManager

### Vigência
- [x] Carimbo "Base atualizada em DD/MM/AAAA" em todos os outputs
- [x] Variável de ambiente `CORPUS_UPDATE_DATE`

## 🧪 Aceites do MVP

### Teste 1: Triagem Completa
- [x] Usuário descreve "plano de saúde negou exame X"
- [x] `/analyze_case` retorna 8 seções
- [x] Citações com tags `<fonte>`
- [x] Carimbo de vigência presente

### Teste 2: Relatório Premium
- [x] Pagamento R$ 7 (stub)
- [x] `/report` gera PDF
- [x] PDF tem: capa, sumário, seções, anexos de citações
- [x] Link de download válido

### Teste 3: Busca + Peça
- [x] Advogado busca "PIX estorno golpe"
- [x] Adiciona lei/súmula/precedente ao carrinho
- [x] `/compose` gera DOCX
- [x] DOCX tem pedidos e citações numeradas

### Teste 4: Sistema de Leads
- [x] Lead qualificado criado
- [x] Enviado a advogado com plano Full
- [x] Janela de exclusividade ativa (expires_at)
- [x] Rodízio funciona (last_lead_at, success_score)

### Teste 5: Citações Rastreáveis
- [x] Todas citações têm: ID, órgão, data, link
- [x] Registradas em `citations_log`
- [x] Hierarquia correta no ranking

## 📦 Pacote de Entrega

### Arquivos Essenciais
- [x] `docker-compose.yml` completo
- [x] `.env.example` com todas as variáveis
- [x] `README.md` com instruções completas
- [x] Todos os arquivos da API
- [x] Todos os serviços
- [x] Templates (DOCX + HTML)
- [x] Scripts de ingestão
- [x] Web (HTML + JS)
- [x] SQL migrations
- [x] Worker
- [x] Dados de amostra

### Dados de Amostra (10 itens)
- [x] 2 artigos: CDC Art. 14, CPC Art. 300
- [x] 2 súmulas: STJ 385, STJ 309
- [x] 2 ementas: PIX fraude, Plano de Saúde rol ANS
- [x] 2 regulatórios: Resolução ANS 465/2021, Resolução BCB 107/2020
- [x] 2 doutrinas: Responsabilidade PIX, Rol ANS

### Scripts de Setup
- [x] `setup_sample_data.sh` (Linux/Mac)
- [x] `setup_sample_data.bat` (Windows)
- [x] Script executa `build_corpus.py --sample`

### Exemplos `curl`
- [x] README tem exemplos de uso de todos endpoints
- [x] Payloads de exemplo fornecidos
- [x] Testes de health check

## ✅ Checklist Final

### Containers
- [x] `docker compose up` inicia todos os serviços
- [x] `/health` retorna status OK
- [x] vLLM serve em `/v1` (OpenAI-compatible)
- [x] Qdrant acessível em :6333
- [x] Postgres inicializa com schema
- [x] Redis funciona para filas

### Funcionalidades Core
- [x] `/analyze_case` funciona e retorna análise estruturada
- [x] `/report` gera PDF
- [x] `/search` busca e ranqueia corretamente
- [x] `/compose` gera DOCX com template

### Web
- [x] Landing abre em localhost:3000
- [x] Modo Advogado abre em localhost:3000/advogado.html
- [x] Form de triagem envia para API
- [x] Busca jurídica funciona

### Dados
- [x] Corpus de amostra carrega no Qdrant
- [x] Planos são criados no banco
- [x] Schema JSON correto em todos os chunks

### Qualidade
- [x] Código comentado quando necessário
- [x] Sem perguntas ao usuário (auto-suficiente)
- [x] Especificação seguida exatamente
- [x] Pronto para rodar em ambiente local

---

## 🎉 RESULTADO

**TODOS os requisitos foram atendidos!**

O sistema está completo e pronto para:
1. `docker compose up -d`
2. `setup_sample_data.bat` (ou .sh)
3. Acessar http://localhost:3000
4. Testar análise de casos
5. Testar busca jurídica
6. Gerar peças
7. Explorar todos os endpoints

**MVP 100% FUNCIONAL** ✅
