# GUIA CI/CD - Doutora IA

Pipeline completo de CI/CD com GitHub Actions para testes automatizados, builds e deployments.

---

## 🎯 Workflows Configurados

### 1. **Test** (`.github/workflows/test.yml`)

Roda em **push** e **pull requests** para `main` e `develop`.

**Etapas:**
- ✅ Checkout do código
- ✅ Setup Python 3.11
- ✅ Instalar dependências
- ✅ Linter (flake8)
- ✅ Testes com pytest
- ✅ Cobertura de código (>= 70%)
- ✅ Security scan (Bandit, Safety)
- ✅ Type checking (mypy)
- ✅ Upload resultados para Codecov

**Serviços:**
- PostgreSQL 16 (para testes de integração)
- Qdrant (para testes de RAG)

### 2. **Docker Build** (`.github/workflows/docker.yml`)

Roda em **push** para `main` e em **tags** (releases).

**Etapas:**
- ✅ Build de imagens Docker (API + Web App)
- ✅ Push para GitHub Container Registry
- ✅ Multi-arch builds (amd64, arm64)
- ✅ Security scan com Trivy
- ✅ Cache otimizado

**Imagens geradas:**
```
ghcr.io/<owner>/doutora-ia:main
ghcr.io/<owner>/doutora-ia:v1.0.0
ghcr.io/<owner>/doutora-ia:sha-abc1234
```

### 3. **Deploy** (`.github/workflows/deploy.yml`)

Roda em **tags** `v*` ou **manual dispatch**.

**Etapas:**
- ✅ Deploy via SSH para servidor
- ✅ Pull de código atualizado
- ✅ Atualização de imagens Docker
- ✅ Migrations de banco de dados
- ✅ Restart com zero downtime
- ✅ Smoke tests pós-deploy
- ✅ Rollback automático em caso de falha
- ✅ Notificações (Slack)
- ✅ GitHub Release automático

---

## 🚀 Como Usar

### Executar Testes Localmente

```bash
# Rodar todos os testes
./scripts/run_tests.sh

# Rodar testes no Docker (ambiente idêntico ao CI)
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Trigger Manual de Deploy

1. Vá para **Actions** no GitHub
2. Selecione **Deploy to Production**
3. Clique em **Run workflow**
4. Escolha o environment (staging/production)
5. Clique em **Run workflow**

### Criar Release (Deploy Automático)

```bash
# Criar tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push da tag (triggera deploy automático)
git push origin v1.0.0
```

---

## 🔧 Configuração de Secrets

### GitHub Repository Secrets

Configurar em: **Settings** → **Secrets and variables** → **Actions**

#### Required Secrets:

```bash
# OpenAI API (para testes)
OPENAI_API_KEY=sk-...

# Deployment (SSH)
SSH_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----...
SERVER_HOST=doutora-ia.com
SERVER_USER=deploy
DEPLOY_PATH=/var/www/doutora-ia

# Production URLs
PRODUCTION_API_URL=https://api.doutora-ia.com

# Notifications (opcional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

#### Optional Secrets:

```bash
# Codecov
CODECOV_TOKEN=...

# Docker Registry
DOCKER_USERNAME=...
DOCKER_PASSWORD=...
```

---

## 📊 Status Badges

Adicione ao README.md:

```markdown
![Tests](https://github.com/<owner>/doutora-ia/actions/workflows/test.yml/badge.svg)
![Docker Build](https://github.com/<owner>/doutora-ia/actions/workflows/docker.yml/badge.svg)
![Coverage](https://codecov.io/gh/<owner>/doutora-ia/branch/main/graph/badge.svg)
```

---

## 🔒 Segurança

### Code Scanning

- **Bandit**: Scan de vulnerabilidades em Python
- **Safety**: Check de dependências vulneráveis
- **Trivy**: Scan de imagens Docker
- **CodeQL** (opcional): Análise de código GitHub

### Branch Protection

Configurar em: **Settings** → **Branches** → **Branch protection rules**

Para branch `main`:
- ✅ Require pull request before merging
- ✅ Require status checks to pass (Tests, Docker Build)
- ✅ Require conversation resolution before merging
- ✅ Require signed commits (recomendado)

---

## 📈 Monitoramento

### Logs de CI/CD

```bash
# Ver logs de workflow específico
gh run view <run-id>

# Ver logs em tempo real
gh run watch
```

### Métricas

- **Build Time**: Objetivo < 5 minutos
- **Test Time**: Objetivo < 2 minutos
- **Deploy Time**: Objetivo < 3 minutos
- **Success Rate**: Objetivo > 95%

---

## 🐛 Troubleshooting

### Testes Falhando no CI mas Passando Localmente

1. **Verificar environment variables**:
   ```yaml
   env:
     DEBUG: true
   ```

2. **Rodar em container igual ao CI**:
   ```bash
   docker run -it --rm python:3.11 bash
   # Dentro do container:
   cd /app
   pip install -r requirements.txt
   pytest
   ```

3. **Verificar diferenças de timezone/locale**:
   ```python
   import os
   os.environ['TZ'] = 'UTC'
   ```

### Docker Build Muito Lento

1. **Usar cache layers**:
   ```dockerfile
   # Copiar requirements primeiro (cache)
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   # Copiar código depois
   COPY . .
   ```

2. **Build multi-stage**:
   ```dockerfile
   # Stage 1: Build
   FROM python:3.11 as builder
   # ...

   # Stage 2: Runtime
   FROM python:3.11-slim
   COPY --from=builder /app /app
   ```

### Deploy Failing

1. **Verificar SSH connection**:
   ```bash
   ssh deploy@doutora-ia.com 'echo "Connection OK"'
   ```

2. **Verificar permissões**:
   ```bash
   # No servidor
   ls -la /var/www/doutora-ia
   whoami
   ```

3. **Verificar logs do servidor**:
   ```bash
   ssh deploy@doutora-ia.com 'docker-compose logs --tail=100'
   ```

### Rollback Manual

```bash
# SSH no servidor
ssh deploy@doutora-ia.com

# Ir para diretório de deploy
cd /var/www/doutora-ia

# Ver tags disponíveis
git tag -l

# Fazer checkout de versão anterior
git checkout v1.0.0

# Restart dos containers
docker-compose down
docker-compose up -d

# Verificar health
curl http://localhost:8000/health
```

---

## 🔄 Fluxo de Trabalho Recomendado

### Feature Development

```bash
# 1. Criar branch de feature
git checkout -b feature/nova-funcionalidade

# 2. Desenvolver e testar localmente
./scripts/run_tests.sh

# 3. Commit e push
git add .
git commit -m "feat: adiciona nova funcionalidade"
git push origin feature/nova-funcionalidade

# 4. Criar Pull Request
gh pr create --title "Nova Funcionalidade" --body "Descrição..."

# 5. CI roda automaticamente
# - Testes
# - Linter
# - Security scan

# 6. Merge após aprovação
gh pr merge --merge
```

### Hotfix (Urgente)

```bash
# 1. Criar branch de hotfix
git checkout -b hotfix/correcao-critica main

# 2. Fazer correção
# ...

# 3. Commit e push
git commit -am "fix: corrige bug crítico"
git push origin hotfix/correcao-critica

# 4. Merge direto para main (se aprovado)
gh pr create --base main --title "Hotfix: Bug Crítico"
gh pr merge --merge

# 5. Deploy imediato
git tag -a v1.0.1 -m "Hotfix release"
git push origin v1.0.1
```

### Release

```bash
# 1. Atualizar CHANGELOG.md
# 2. Atualizar versão em package.json, pyproject.toml, etc.

# 3. Commit
git commit -am "chore: release v1.1.0"

# 4. Tag
git tag -a v1.1.0 -m "Release v1.1.0"

# 5. Push (triggera deploy automático)
git push origin main
git push origin v1.1.0

# 6. CI/CD faz automaticamente:
# - Build de imagens Docker
# - Deploy para production
# - Smoke tests
# - GitHub Release
# - Notificações
```

---

## 📋 Checklist Pre-Deploy

Antes de fazer deploy para production:

- [ ] Todos os testes passando
- [ ] Cobertura >= 70%
- [ ] Security scan limpo
- [ ] Changelog atualizado
- [ ] Documentação atualizada
- [ ] Database migrations testadas
- [ ] Environment variables configuradas
- [ ] Backup de banco de dados feito
- [ ] Comunicação com stakeholders
- [ ] Plano de rollback definido

---

## 🎯 Métricas de Qualidade

### CI/CD Health Metrics

```yaml
# Exemplo de dashboard metrics
- Build Success Rate: 98%
- Average Build Time: 3m 45s
- Average Test Time: 1m 30s
- Deploy Success Rate: 100%
- Mean Time to Recovery: 5 minutes
```

### Deployment Frequency

- **Development**: Várias vezes ao dia
- **Staging**: 1-2x por dia
- **Production**: 1-2x por semana (ou mais com CD)

---

## 🔗 Integraçõ

es

### Opcional - Integrar com Serviços Externos:

1. **Sentry** (Error tracking):
   ```yaml
   - name: Create Sentry release
     uses: getsentry/action-release@v1
     with:
       environment: production
   ```

2. **DataDog** (Monitoring):
   ```yaml
   - name: Send metrics to DataDog
     run: |
       curl -X POST "https://api.datadoghq.com/api/v1/events" \
         -H "DD-API-KEY: ${{ secrets.DATADOG_API_KEY }}" \
         -d '{"title":"Deployment","text":"Deployed v${{ github.ref_name }}"}'
   ```

3. **PagerDuty** (Incidents):
   ```yaml
   - name: Notify PagerDuty
     if: failure()
     uses: PagerDuty/pagerduty-change-events-action@v1
   ```

---

**Pipeline CI/CD completo e pronto para produção!** 🎉

Testes automatizados, builds otimizados, deploy com zero downtime e rollback automático.
