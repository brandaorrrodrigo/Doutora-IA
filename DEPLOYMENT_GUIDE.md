# GUIA DE DEPLOYMENT - Doutora IA

Guia completo para deploy em produção com Nginx, SSL, Docker e monitoramento.

---

## 🎯 Visão Geral

Este guia cobre o deployment completo da Doutora IA em produção:
- ✅ Configuração de servidor
- ✅ SSL/TLS com Let's Encrypt
- ✅ Nginx como reverse proxy
- ✅ Docker Compose para orquestração
- ✅ Backups automatizados
- ✅ Monitoramento e logs
- ✅ CI/CD com GitHub Actions

---

## 📋 Pré-requisitos

### Servidor

- **OS**: Ubuntu 22.04 LTS (recomendado) ou Debian 12
- **RAM**: Mínimo 4GB (recomendado 8GB)
- **CPU**: 2 cores (recomendado 4 cores)
- **Disco**: 50GB SSD
- **Rede**: IP público estático

### Domínio

- Domínio registrado (ex: `doutora-ia.com`)
- DNS configurado apontando para o servidor:
  ```
  A     doutora-ia.com        → IP_DO_SERVIDOR
  A     www.doutora-ia.com    → IP_DO_SERVIDOR
  A     api.doutora-ia.com    → IP_DO_SERVIDOR
  ```

### Contas e Keys

- OpenAI API Key
- Mercado Pago Access Token (opcional)
- GitHub account (para CI/CD)

---

## 🚀 Deployment Automático

### Opção 1: Script Completo

```bash
# 1. Conectar no servidor
ssh root@SEU_SERVIDOR

# 2. Baixar e executar script de deployment
curl -fsSL https://raw.githubusercontent.com/your-org/doutora-ia/main/scripts/deploy_production.sh | bash
```

O script irá:
1. Verificar pré-requisitos
2. Clonar/atualizar repositório
3. Configurar environment variables
4. Obter certificados SSL
5. Build de imagens Docker
6. Setup de banco de dados
7. Iniciar todos os serviços

---

## 🔧 Deployment Manual

### 1. Preparar Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y \
    curl \
    git \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx

# Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clonar Repositório

```bash
# Criar diretório
sudo mkdir -p /var/www/doutora-ia
sudo chown $USER:$USER /var/www/doutora-ia

# Clonar
cd /var/www/doutora-ia
git clone https://github.com/your-org/doutora-ia.git .
```

### 3. Configurar Environment

```bash
# Copiar .env template
cp .env.example .env

# Editar com credenciais reais
nano .env
```

**Variáveis Obrigatórias:**

```bash
# API
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini

# Database
PG_PASSWORD=SENHA_FORTE_AQUI
PG_DB=doutora_ia
PG_USER=postgres

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256

# Payments (opcional)
MERCADO_PAGO_ACCESS_TOKEN=APP-...
BINANCE_PAY_API_KEY=...
STRIPE_SECRET_KEY=sk_live_...

# Domain
API_HOST=https://doutora-ia.com
NEXT_PUBLIC_API_URL=https://api.doutora-ia.com
```

### 4. SSL Certificates

```bash
# Criar diretórios
mkdir -p certbot/conf certbot/www

# Subir Nginx temporariamente
docker-compose -f docker-compose.prod.yml up -d nginx

# Obter certificado
sudo docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@doutora-ia.com \
    --agree-tos \
    --no-eff-email \
    -d doutora-ia.com \
    -d www.doutora-ia.com \
    -d api.doutora-ia.com
```

### 5. Build e Deploy

```bash
# Build imagens
docker-compose -f docker-compose.prod.yml build

# Subir database
docker-compose -f docker-compose.prod.yml up -d db qdrant

# Aguardar database estar pronto
sleep 10

# Rodar migrations
docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# Seed (opcional)
docker-compose -f docker-compose.prod.yml run --rm api python -m scripts.seed_database

# Subir todos os serviços
docker-compose -f docker-compose.prod.yml up -d

# Verificar health
curl https://api.doutora-ia.com/health
```

---

## 📊 Monitoramento

### Logs

```bash
# Ver logs de todos os serviços
docker-compose -f docker-compose.prod.yml logs -f

# Logs específicos
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f nginx

# Logs do Nginx (diretamente)
tail -f logs/nginx/api-access.log
tail -f logs/nginx/api-error.log
```

### Health Checks

```bash
# API health
curl https://api.doutora-ia.com/health

# Database
docker-compose -f docker-compose.prod.yml exec db pg_isready

# Qdrant
curl http://localhost:6333/health
```

### Métricas

```bash
# Uso de recursos
docker stats

# Disk usage
docker system df
df -h

# Memory
free -h

# CPU
top
```

---

## 🔄 Backups

### Manual

```bash
# Rodar backup
./scripts/backup.sh
```

### Automático (Cron)

```bash
# Editar crontab
crontab -e

# Adicionar backup diário às 3am
0 3 * * * /var/www/doutora-ia/scripts/backup.sh >> /var/log/doutora-ia-backup.log 2>&1
```

### Restore

```bash
# Parar serviços
docker-compose -f docker-compose.prod.yml down

# Restaurar database
gunzip < /var/backups/doutora-ia/postgres_TIMESTAMP.sql.gz | \
    docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres

# Restaurar Qdrant
tar -xzf /var/backups/doutora-ia/qdrant_TIMESTAMP.tar.gz
docker cp qdrant_temp $(docker-compose ps -q qdrant):/qdrant/snapshots/

# Restaurar arquivos estáticos
tar -xzf /var/backups/doutora-ia/static_TIMESTAMP.tar.gz

# Reiniciar
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔄 Atualizações

### Update sem Downtime

```bash
cd /var/www/doutora-ia

# Fazer backup primeiro
./scripts/backup.sh

# Pull do código
git pull origin main

# Build novas imagens
docker-compose -f docker-compose.prod.yml build

# Update serviços (rolling update)
docker-compose -f docker-compose.prod.yml up -d --no-deps --build api
docker-compose -f docker-compose.prod.yml up -d --no-deps --build web-app

# Verificar health
sleep 10
curl -f https://api.doutora-ia.com/health || echo "FALHOU!"
```

### Rollback

```bash
# Ver commits
git log --oneline

# Voltar para versão anterior
git reset --hard HEAD~1  # ou COMMIT_HASH

# Rebuild e restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🔒 Segurança

### Firewall (UFW)

```bash
# Instalar e configurar
sudo apt install ufw

# Permitir SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Ativar
sudo ufw enable
```

### Fail2Ban (Proteção DDoS)

```bash
# Instalar
sudo apt install fail2ban

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl restart fail2ban
```

### Secrets Rotation

```bash
# Gerar novo SECRET_KEY
openssl rand -hex 32

# Atualizar .env
nano .env

# Restart API
docker-compose -f docker-compose.prod.yml restart api
```

---

## 📈 Otimização de Performance

### 1. Database

```sql
-- Vacuum e analyze periódicos
docker-compose exec db psql -U postgres -d doutora_ia -c "VACUUM ANALYZE;"

-- Reindex
docker-compose exec db psql -U postgres -d doutora_ia -c "REINDEX DATABASE doutora_ia;"
```

### 2. Nginx Cache

Adicionar em `nginx/doutora-ia.conf`:

```nginx
# Cache configuration
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m inactive=60m;

location /search {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    add_header X-Cache-Status $upstream_cache_status;
    # ...
}
```

### 3. Database Connection Pooling

Ajustar em `.env`:

```bash
PG_POOL_SIZE=20
PG_MAX_OVERFLOW=10
```

---

## 🚨 Troubleshooting

### Serviço não inicia

```bash
# Ver logs
docker-compose -f docker-compose.prod.yml logs api

# Verificar portas
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3000

# Verificar resources
docker stats
```

### SSL não funciona

```bash
# Verificar certificados
sudo ls -la /etc/letsencrypt/live/doutora-ia.com/

# Testar SSL
curl -vI https://doutora-ia.com

# Renovar manualmente
sudo certbot renew --force-renewal
```

### Database connection error

```bash
# Verificar database está rodando
docker-compose ps

# Testar conexão
docker-compose exec api python -c "from db import engine; print(engine.connect())"

# Verificar credenciais
docker-compose exec db psql -U postgres -c "SELECT 1;"
```

### Out of memory

```bash
# Ver uso
free -h
docker stats

# Limpar containers antigos
docker system prune -a

# Ajustar swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## ✅ Checklist Pré-Deploy

- [ ] DNS configurado e propagado
- [ ] Servidor provisionado e atualizado
- [ ] Docker e Docker Compose instalados
- [ ] .env configurado com credenciais reais
- [ ] SSL certificates obtidos
- [ ] Firewall configurado
- [ ] Backup automatizado configurado
- [ ] Monitoring configurado
- [ ] Health checks funcionando
- [ ] Testes smoke passando
- [ ] Documentação atualizada
- [ ] Equipe notificada

---

## 📞 Suporte

Em caso de problemas:

1. Verificar logs: `docker-compose logs -f`
2. Verificar health checks
3. Consultar troubleshooting acima
4. Abrir issue no GitHub
5. Contatar equipe de DevOps

---

**Deployment production-ready completo!** 🎉

Sistema robusto, seguro, monitorado e com backups automatizados.
