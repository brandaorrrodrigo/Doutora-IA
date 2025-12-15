# 🚀 QUICK START - FASE 2 + FASE 3

Guia rápido para ativar as funcionalidades de Integração com Tribunais (Fase 2) e Marketplace de Leads (Fase 3).

## ✅ PRÉ-REQUISITOS

- Docker e Docker Compose instalados
- Sistema MVP (Fase 1) funcionando
- Acesso ao banco de dados PostgreSQL

---

## 📋 PASSO A PASSO (5 MINUTOS)

### 1️⃣ Executar Migration do Banco de Dados

**No Windows:**
```batch
scripts\migrate_fase2_fase3.bat
```

**No Linux/Mac:**
```bash
bash scripts/migrate_fase2_fase3.sh
```

**Ou manualmente:**
```bash
# Conectar ao container do banco
docker compose exec db psql -U postgres -d doutora

# Executar migration
\i /docker-entrypoint-initdb.d/002_fase2_fase3_tables.sql

# Verificar tabelas criadas
\dt

# Sair
\q
```

### 2️⃣ Configurar Variáveis de Ambiente

Edite o arquivo `.env` e adicione:

```env
# Twilio (WhatsApp + SMS)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
TWILIO_PHONE_NUMBER=+15551234567

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASS=sua_senha_app_do_gmail
FROM_EMAIL=noreply@doutoraia.com.br
```

**📝 Notas:**
- Para Twilio: Crie conta gratuita em https://www.twilio.com/try-twilio
- Para Gmail SMTP: Use "Senhas de app" (não a senha normal)
- WhatsApp Sandbox: Use o número fornecido pelo Twilio

### 3️⃣ Instalar Novas Dependências

```bash
docker compose exec api pip install twilio cryptography
```

Ou reconstrua o container:
```bash
docker compose build api
docker compose up -d api
```

### 4️⃣ Reiniciar API

```bash
docker compose restart api
```

Verifique os logs:
```bash
docker compose logs -f api
```

Você deve ver:
```
✓ Endpoints Fase 2 + 3 integrados com sucesso
```

---

## 🧪 TESTAR FUNCIONALIDADES

### Teste 1: Health Check
```bash
curl http://localhost:8080/health
```

### Teste 2: Listar Leads Disponíveis
```bash
curl "http://localhost:8080/marketplace/leads?lawyer_id=1"
```

### Teste 3: Consultar Processo (Mock)
```bash
curl -X POST http://localhost:8080/tribunais/consultar-processo \
  -H "Content-Type: application/json" \
  -d '{
    "numero_processo": "1234567-89.2024.8.26.0100",
    "tribunal": "tjsp"
  }'
```

### Teste 4: Busca Unificada de Jurisprudência
```bash
curl "http://localhost:8080/tribunais/jurisprudencia-unificada?query=PIX+fraude&tribunais=stj,stf&limit=5"
```

### Teste 5: Gerar Perfil Público de Advogado
```bash
curl -X POST "http://localhost:8080/advogados/1/gerar-perfil"
```

---

## 🌐 ACESSAR INTERFACE WEB

### Marketplace de Leads (para advogados)
```
http://localhost:3000/leads.html
```

### Perfil Público de Advogado (exemplo)
```
http://localhost:3000/advogados/sp/sao-paulo/familia/dr-joao-silva
```

---

## 📊 POPULAR BANCO COM DADOS DE TESTE

Execute o script SQL de teste (opcional):

```bash
docker compose exec -T db psql -U postgres -d doutora << 'EOF'
-- Criar advogado de teste
INSERT INTO lawyers (email, name, oab, phone, areas, cities, states, is_active, is_verified)
VALUES (
  'joao.silva@example.com',
  'João Silva',
  'OAB/SP 123456',
  '+5511999999999',
  ARRAY['familia', 'consumidor'],
  ARRAY['São Paulo'],
  ARRAY['SP'],
  TRUE,
  TRUE
) ON CONFLICT DO NOTHING;

-- Criar caso de teste
INSERT INTO cases (description, area, sub_area, status, report_paid)
VALUES (
  'Problema com cobrança indevida no cartão de crédito',
  'consumidor',
  'bancario',
  'analyzed',
  TRUE
) RETURNING id;

-- Ver dados criados
SELECT * FROM lawyers;
SELECT * FROM cases;
EOF
```

---

## 🔍 VERIFICAR INSTALAÇÃO

Use a documentação interativa do FastAPI:

```
http://localhost:8080/docs
```

Verifique se os novos endpoints aparecem:
- **Tribunais:** `/tribunais/*`
- **Marketplace:** `/marketplace/*`
- **Perfil Público:** `/advogados/*`
- **Avaliações:** `/avaliacoes/*`
- **Agendamentos:** `/agendamento/*`

---

## ❌ TROUBLESHOOTING

### Erro: "Table already exists"
```bash
# Normal se você já executou a migration antes
# Ignore ou delete as tabelas e execute novamente
```

### Erro: "Module endpoints_fase2_fase3 not found"
```bash
# Verifique se o arquivo existe
ls -la api/endpoints_fase2_fase3.py

# Reinicie o container
docker compose restart api
```

### Erro: "Twilio credentials are required"
```bash
# Configure as variáveis de ambiente no .env
# Ou use modo mock (comentar linhas de verificação no código)
```

### API não inicia
```bash
# Ver logs detalhados
docker compose logs api

# Reconstruir container
docker compose down
docker compose build api
docker compose up -d
```

---

## 🎯 PRÓXIMOS PASSOS

Após a instalação básica funcionar:

1. **Configurar Certificado Digital A3** (para protocolamento real)
   - Obter certificado ICP-Brasil
   - Configurar variáveis `CERT_PATH` e `CERT_PASSWORD`

2. **Integração Real com Tribunais**
   - Configurar credenciais PJe/eProc
   - Testar consulta de processos reais

3. **Ativar Notificações**
   - Configurar número WhatsApp Business
   - Testar envio de alertas de prazo

4. **SEO e Perfis Públicos**
   - Configurar domínio real
   - Gerar perfis para advogados cadastrados
   - Submeter sitemap ao Google

5. **Dashboard do Advogado**
   - Implementar painel completo
   - Métricas e analytics

---

## 📚 DOCUMENTAÇÃO COMPLETA

Para detalhes técnicos e fluxos completos, consulte:
- `INTEGRACAO_FASE2_FASE3.md` - Guia técnico completo
- `RESUMO_FASE2_FASE3.md` - Resumo executivo

---

## 🆘 SUPORTE

Em caso de dúvidas ou problemas:
1. Verifique os logs: `docker compose logs -f api`
2. Consulte a documentação: `http://localhost:8080/docs`
3. Revise as variáveis de ambiente no `.env`

---

**Sistema pronto para testar! 🎉**
