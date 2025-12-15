# ✅ CHECKLIST DE INTEGRAÇÃO - FASE 2 + FASE 3

Use este checklist para garantir que a integração foi realizada corretamente.

---

## 📦 FASE 1: ARQUIVOS E CÓDIGO

### Arquivos Criados
- [x] `api/services/tribunals.py` - Integração com tribunais
- [x] `api/services/alerts.py` - Sistema de alertas
- [x] `api/services/marketplace.py` - Marketplace de leads
- [x] `api/services/lawyer_profile.py` - Perfis públicos
- [x] `api/endpoints_fase2_fase3.py` - Novos endpoints
- [x] `migrations/002_fase2_fase3_tables.sql` - Migration do banco
- [x] `web/public/leads.html` - Interface de leads
- [x] `web/public/leads.js` - JavaScript do marketplace
- [x] `INTEGRACAO_FASE2_FASE3.md` - Documentação técnica
- [x] `RESUMO_FASE2_FASE3.md` - Resumo executivo
- [x] `QUICK_START_FASE2_FASE3.md` - Guia rápido
- [x] `scripts/migrate_fase2_fase3.sh` - Script de migration (Linux/Mac)
- [x] `scripts/migrate_fase2_fase3.bat` - Script de migration (Windows)

### Arquivos Modificados
- [x] `api/main.py` - Router integrado
- [x] `api/requirements.txt` - Dependências adicionadas
- [x] `.env.example` - Variáveis de ambiente adicionadas

---

## 📋 FASE 2: BANCO DE DADOS

### Migration Executada
- [ ] Migration `002_fase2_fase3_tables.sql` executada com sucesso
- [ ] 10 novas tabelas criadas:
  - [ ] `processos`
  - [ ] `movimentacoes`
  - [ ] `prazos`
  - [ ] `publicacoes_dje`
  - [ ] `avaliacoes`
  - [ ] `agendamentos`
  - [ ] `parceiros`
  - [ ] `leads_parceria`
  - [ ] `blog_posts`
  - [ ] `notificacoes`

### Verificar Tabelas
```sql
-- Conectar ao banco
docker compose exec db psql -U postgres -d doutora

-- Listar todas as tabelas
\dt

-- Verificar colunas adicionadas em lawyers
\d lawyers

-- Verificar colunas adicionadas em cases
\d cases

-- Verificar view criada
\dv dashboard_advogado
```

### Campos Adicionados
- [ ] `lawyers.slug` - URL amigável
- [ ] `lawyers.perfil_url` - Link do perfil
- [ ] `lawyers.rating` - Avaliação média
- [ ] `lawyers.total_ratings` - Total de avaliações
- [ ] `cases.origem` - Origem do lead
- [ ] `cases.parceiro_id` - ID do parceiro

### Triggers e Views
- [ ] Trigger `trigger_atualizar_rating` criado
- [ ] View `dashboard_advogado` criada

---

## 🔧 FASE 3: DEPENDÊNCIAS E CONFIGURAÇÃO

### Dependências Instaladas
- [ ] `twilio==8.11.0` instalado
- [ ] `cryptography==41.0.7` instalado

**Verificar:**
```bash
docker compose exec api pip list | grep twilio
docker compose exec api pip list | grep cryptography
```

### Variáveis de Ambiente Configuradas

**Obrigatórias para produção:**
- [ ] `TWILIO_ACCOUNT_SID` configurado
- [ ] `TWILIO_AUTH_TOKEN` configurado
- [ ] `TWILIO_WHATSAPP_NUMBER` configurado
- [ ] `TWILIO_PHONE_NUMBER` configurado
- [ ] `SMTP_HOST` configurado
- [ ] `SMTP_PORT` configurado
- [ ] `SMTP_USER` configurado
- [ ] `SMTP_PASS` configurado
- [ ] `FROM_EMAIL` configurado

**Opcionais:**
- [ ] `CERT_PATH` (certificado digital A3)
- [ ] `CERT_PASSWORD` (senha do certificado)

---

## 🚀 FASE 4: API E ENDPOINTS

### API Iniciada Corretamente
- [ ] Container `api` rodando sem erros
- [ ] Mensagem "✓ Endpoints Fase 2 + 3 integrados com sucesso" nos logs
- [ ] Nenhum erro de importação

**Verificar logs:**
```bash
docker compose logs api | tail -50
```

### Endpoints Disponíveis

**Tribunais:**
- [ ] `POST /tribunais/consultar-processo`
- [ ] `POST /tribunais/protocolar-peticao`
- [ ] `GET /tribunais/diario-oficial`
- [ ] `GET /tribunais/jurisprudencia-unificada`

**Marketplace:**
- [ ] `GET /marketplace/leads`
- [ ] `POST /marketplace/leads/acao`
- [ ] `GET /marketplace/estatisticas`

**Perfil Público:**
- [ ] `GET /advogados/{estado}/{cidade}/{area}/{nome}`
- [ ] `POST /advogados/{lawyer_id}/gerar-perfil`

**Avaliações:**
- [ ] `POST /avaliacoes/criar`
- [ ] `GET /avaliacoes/advogado/{lawyer_id}`

**Agendamentos:**
- [ ] `POST /agendamento/criar`

**Parcerias:**
- [ ] `POST /parcerias/sindicato/lead`

**Verificar documentação:**
```
http://localhost:8080/docs
```

---

## 🧪 FASE 5: TESTES FUNCIONAIS

### Teste 1: Health Check
```bash
curl http://localhost:8080/health
```
**Esperado:** `{"status": "healthy", ...}`
- [ ] ✅ Passou

### Teste 2: Marketplace - Listar Leads
```bash
curl "http://localhost:8080/marketplace/leads?lawyer_id=1"
```
**Esperado:** Lista de leads (pode estar vazia)
- [ ] ✅ Passou

### Teste 3: Consultar Processo
```bash
curl -X POST http://localhost:8080/tribunais/consultar-processo \
  -H "Content-Type: application/json" \
  -d '{"numero_processo":"1234567-89.2024.8.26.0100","tribunal":"tjsp"}'
```
**Esperado:** Dados do processo (ou erro 404 se não existir)
- [ ] ✅ Passou

### Teste 4: Jurisprudência Unificada
```bash
curl "http://localhost:8080/tribunais/jurisprudencia-unificada?query=fraude&tribunais=stj&limit=3"
```
**Esperado:** Lista de jurisprudências
- [ ] ✅ Passou

### Teste 5: Gerar Perfil de Advogado
```bash
curl -X POST "http://localhost:8080/advogados/1/gerar-perfil"
```
**Esperado:** Perfil HTML gerado
- [ ] ✅ Passou

### Teste 6: Estatísticas do Marketplace
```bash
curl "http://localhost:8080/marketplace/estatisticas?lawyer_id=1"
```
**Esperado:** Métricas do advogado
- [ ] ✅ Passou

---

## 🌐 FASE 6: INTERFACE WEB

### Páginas Funcionando
- [ ] `http://localhost:3000/leads.html` carrega sem erros
- [ ] JavaScript carrega leads da API
- [ ] Filtros funcionam
- [ ] Botões "Aceitar" e "Rejeitar" funcionam
- [ ] Modal de detalhes abre corretamente

### Console do Navegador
- [ ] Sem erros de JavaScript
- [ ] Requisições para `/marketplace/leads` bem-sucedidas
- [ ] Auto-refresh a cada 30 segundos funciona

---

## 📊 FASE 7: DADOS DE TESTE (OPCIONAL)

### Popular com Dados Fictícios
- [ ] Advogado de teste criado
- [ ] Caso de teste criado (pago)
- [ ] Lead aparece no marketplace
- [ ] Dashboard mostra estatísticas

**Script de teste:**
```sql
-- Executar via psql
INSERT INTO lawyers (email, name, oab, phone, areas, cities, states, is_active)
VALUES ('teste@example.com', 'Dr. Teste', 'OAB/SP 999999', '+5511999999999',
        ARRAY['familia'], ARRAY['São Paulo'], ARRAY['SP'], TRUE);

INSERT INTO cases (description, area, status, report_paid)
VALUES ('Caso de teste', 'familia', 'analyzed', TRUE);
```

---

## 🔍 FASE 8: VALIDAÇÃO FINAL

### Funcionalidades Críticas
- [ ] Sistema aceita novo caso
- [ ] Pagamento marca caso como `report_paid`
- [ ] Lead é criado automaticamente após pagamento
- [ ] Advogado recebe notificação (se Twilio configurado)
- [ ] Advogado pode aceitar lead
- [ ] Advogado pode rejeitar lead
- [ ] Lead rejeitado vai para outro advogado

### Performance
- [ ] API responde em < 2 segundos
- [ ] Busca de jurisprudência retorna em < 5 segundos
- [ ] Dashboard carrega em < 3 segundos

### Segurança
- [ ] Dados sensíveis não aparecem em logs
- [ ] Certificado digital (se configurado) carrega corretamente
- [ ] Validação de dados funciona
- [ ] Rate limiting aplicado (se configurado)

---

## 🎯 FASE 9: PRODUÇÃO (PRÉ-DEPLOY)

### Antes de Ir para Produção
- [ ] Todas as variáveis de ambiente configuradas
- [ ] Certificados SSL configurados
- [ ] Domínio configurado
- [ ] Backup do banco configurado
- [ ] Logs centralizados
- [ ] Monitoramento ativo
- [ ] Alertas configurados
- [ ] Documentação atualizada
- [ ] Testes end-to-end passando
- [ ] Performance testada com carga

### Integrações Reais
- [ ] Twilio: Conta real configurada (não sandbox)
- [ ] SMTP: Email real enviando
- [ ] Certificado Digital A3: Instalado e funcionando
- [ ] PJe: Credenciais reais configuradas
- [ ] Mercado Pago: Webhooks configurados

---

## ❌ TROUBLESHOOTING

### Problema: Migration falha
**Solução:**
```bash
# Verificar se tabelas já existem
docker compose exec db psql -U postgres -d doutora -c "\dt"

# Dropar tabelas se necessário e refazer
docker compose exec db psql -U postgres -d doutora -c "DROP TABLE IF EXISTS processos CASCADE;"
```

### Problema: Endpoints não aparecem no /docs
**Solução:**
```bash
# Verificar se arquivo existe
ls -la api/endpoints_fase2_fase3.py

# Verificar logs de importação
docker compose logs api | grep "Fase 2"

# Reiniciar API
docker compose restart api
```

### Problema: "Module 'endpoints_fase2_fase3' not found"
**Solução:**
```bash
# Verificar estrutura de diretórios
docker compose exec api ls -la /app/

# Copiar arquivo se necessário
docker compose cp api/endpoints_fase2_fase3.py api:/app/

# Reiniciar
docker compose restart api
```

### Problema: Twilio/SMTP não enviam
**Solução:**
- Verificar credenciais no `.env`
- Testar credenciais manualmente
- Verificar firewall/portas
- Usar modo mock para desenvolvimento

---

## 📈 MÉTRICAS DE SUCESSO

Após integração completa, você deve ter:

✅ **10 novas tabelas** no banco
✅ **15+ novos endpoints** na API
✅ **3000+ linhas de código** novo
✅ **Sistema de alertas** multi-canal
✅ **Marketplace** funcionando
✅ **Perfis públicos** com SEO
✅ **Integração tribunais** (mock ou real)
✅ **Dashboard** consolidado

---

## 🎉 CONCLUSÃO

Se todos os itens acima estiverem marcados, a integração Fase 2 + Fase 3 está **completa e funcionando**!

**Próximo:** Começar a testar com usuários reais e coletar feedback.

---

**Data da última atualização:** 2025-12-09
**Versão do sistema:** 2.0 (MVP + Fase 2 + Fase 3)
