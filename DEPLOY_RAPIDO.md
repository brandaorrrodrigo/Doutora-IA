# 🚀 DEPLOY RÁPIDO - DOUTORA IA

## Passo a Passo (5 minutos)

### 1. Login no Railway
Abra um terminal e execute:
```bash
cd C:\Users\NFC\doutora-ia
railway login
```
→ Vai abrir o navegador para você fazer login

### 2. Inicializar Projeto
```bash
railway init
```
→ Escolha: "Create new project"
→ Nome: doutora-ia

### 3. Adicionar PostgreSQL
```bash
railway add
```
→ Escolha: PostgreSQL

### 4. Adicionar Redis
```bash
railway add
```
→ Escolha: Redis

### 5. Configurar Variáveis de Ambiente

Copie e cole este comando (já com valores gerados):

```bash
railway variables set \
  SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')" \
  ADMIN_SECRET_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" \
  ENV="production" \
  OPENAI_API_KEY="sua_chave_aqui" \
  LLM_BASE_URL="https://api.openai.com/v1" \
  LLM_MODEL="gpt-4o-mini" \
  EMAIL_PROVIDER="console" \
  EMAIL_FROM="noreply@doutora-ia.com" \
  REDIS_ENABLED="true" \
  EMBEDDING_DEVICE="cpu" \
  API_PORT="8000" \
  WEASYPRINT_CMD="weasyprint"
```

**IMPORTANTE**: Substitua `sua_chave_aqui` pela sua OpenAI API key!

Se quiser usar email real (opcional):
```bash
railway variables set \
  EMAIL_PROVIDER="resend" \
  RESEND_API_KEY="sua_chave_resend"
```

### 6. Deploy!
```bash
railway up
```

### 7. Configurar Domínio
```bash
railway domain
```
→ Vai gerar uma URL pública

### 8. Testar
```bash
curl $(railway domain)/health
```

## Comandos Úteis

```bash
# Ver logs em tempo real
railway logs

# Ver variáveis configuradas
railway variables

# Abrir dashboard
railway open

# Executar migrações
railway run alembic upgrade head

# Ver status
railway status
```

## Checklist Pós-Deploy

- [ ] Testar `/health` endpoint
- [ ] Testar `/docs` (Swagger)
- [ ] Criar primeiro usuário admin
- [ ] Testar análise de caso
- [ ] Verificar logs

## URLs Importantes

- **Dashboard Railway**: https://railway.app/dashboard
- **Docs API**: [SUA_URL]/docs
- **Health Check**: [SUA_URL]/health

## Custo Estimado

- **Hobby Plan**: $5/mês (500GB transfer, 500GB storage)
- **PostgreSQL**: Incluído
- **Redis**: Incluído

## Problemas Comuns

### Build falha?
```bash
# Ver logs detalhados
railway logs --deployment
```

### Variáveis não carregadas?
```bash
# Listar variáveis
railway variables

# Adicionar variável individual
railway variables set NOME_VAR="valor"
```

### Migrações não rodaram?
```bash
railway run alembic upgrade head
```

## Próximos Passos

1. **Configurar Custom Domain** (opcional)
   ```bash
   railway domain add seudominio.com
   ```

2. **Configurar Monitoramento**
   - Adicionar Sentry para errors
   - Configurar UptimeRobot para uptime

3. **Backup Automático**
   - Railway faz backup automático do PostgreSQL
   - Configurar backup externo se necessário

---

**Pronto!** Seu sistema estará no ar em produção! 🎉
