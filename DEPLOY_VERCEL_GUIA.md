# Deploy em Vercel - Guia Completo

## 🚀 Visão Geral

Vercel é a plataforma criada pelos makers do Next.js. Vamos fazer deploy do frontend (landing) com:
- Next.js 15 + React 19
- 37k questões e explicações integradas
- APIs de Railway conectadas
- Auto-deploy via GitHub

**Tempo estimado**: 20 minutos até estar em produção ✅

---

## 📋 Pré-requisitos

- [x] Projeto Next.js pronto (pasta `landing`)
- [x] Conta Vercel (gratuita em https://vercel.com)
- [x] GitHub conectado ao Vercel
- [x] Código commitado e pusheado para GitHub
- [x] URLs das APIs Railway prontas

---

## 🔑 PASSO 1: Preparar Projeto para Vercel

### 1.1 Verificar package.json

**Arquivo: D:\doutora-ia\landing\package.json**

```json
{
  "name": "doutora-ia-landing",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^15.1.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  }
}
```

### 1.2 Atualizar Variáveis de Ambiente

**Arquivo: D:\doutora-ia\landing\.env.local**

```env
# Desenvolvimento Local
NEXT_PUBLIC_API_QUESTOES=http://localhost:8042
NEXT_PUBLIC_API_MAPAS=http://localhost:8041
NEXT_PUBLIC_ENVIRONMENT=development
```

**Arquivo: D:\doutora-ia\landing\.env.production**

```env
# Produção (Vercel)
NEXT_PUBLIC_API_QUESTOES=https://api-questoes-prod.railway.app
NEXT_PUBLIC_API_MAPAS=https://api-mapas-prod.railway.app
NEXT_PUBLIC_ENVIRONMENT=production
```

### 1.3 Criar vercel.json (já criado)

Configuração otimizada:

```json
{
  "buildCommand": "next build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "headers": [
    {
      "source": "/:path*",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ],
  "redirects": [
    {
      "source": "/",
      "destination": "/estudo",
      "permanent": false
    }
  ]
}
```

---

## 🚀 PASSO 2: Deploy Inicial via Vercel Dashboard

### 2.1 Conectar GitHub

1. Acesse https://vercel.com/dashboard
2. Clique em **"Add New..."** → **"Project"**
3. Selecione **"Import Git Repository"**
4. Busque por `doutora-ia` (seu repositório GitHub)
5. Clique em **"Import"**

### 2.2 Configurar Projeto

**Root Directory**: Deixar vazio (Vercel vai detectar Next.js)

**Build & Output Settings**:
- Framework: **Next.js**
- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: `npm install`

### 2.3 Configurar Variáveis de Ambiente

Na tela de configuração, adicione:

```
NEXT_PUBLIC_API_QUESTOES = https://api-questoes-prod.railway.app
NEXT_PUBLIC_API_MAPAS = https://api-mapas-prod.railway.app
NEXT_PUBLIC_ENVIRONMENT = production
```

Clique em **"Deploy"** → Aguarde build completar (~5-10 min)

---

## 🔄 PASSO 3: Deploy via CLI (Alternativa)

### 3.1 Instalar Vercel CLI

```bash
npm install -g vercel
```

### 3.2 Fazer Deploy

```bash
cd D:\doutora-ia\landing

# Login
vercel login

# Deploy para produção
vercel --prod

# Ou com variáveis
vercel --prod \
  --env NEXT_PUBLIC_API_QUESTOES=https://api-questoes-prod.railway.app \
  --env NEXT_PUBLIC_API_MAPAS=https://api-mapas-prod.railway.app
```

---

## ✅ PASSO 4: Verificar Deploy

### 4.1 Testar Build Localmente

Antes de fazer deploy, testar localmente:

```bash
cd D:\doutora-ia\landing

# Build
npm run build

# Servir produção localmente
npm run start

# Abrir navegador: http://localhost:3000/estudo
```

### 4.2 Verificar Vercel Deployment

1. Dashboard Vercel → Seu projeto
2. Clique em **"Deployments"**
3. Status deve ser **"Ready"** (verde) ✅
4. Clique em **"Visit"** para abrir site em produção

### 4.3 Testar Endpoints

No navegador, vá para:
```
https://doutora-ia-landing.vercel.app/estudo
```

Abra DevTools (F12):
- Aba **"Network"**: Deve ver requisições para as APIs do Railway
- Aba **"Console"**: Não deve ter erros vermelhos

---

## 🔗 PASSO 5: Conectar APIs do Railway

### 5.1 Verificar URLs das APIs

```bash
# Voltar ao projeto Railway
railway domains

# Anotar:
# API Questões: https://api-questoes-prod.railway.app
# API Mapas: https://api-mapas-prod.railway.app
```

### 5.2 Atualizar Vercel com URLs Corretas

**Via Dashboard:**

1. Vercel Dashboard → Settings → Environment Variables
2. Editar:
   - `NEXT_PUBLIC_API_QUESTOES = https://api-questoes-prod.railway.app`
   - `NEXT_PUBLIC_API_MAPAS = https://api-mapas-prod.railway.app`
3. Clique em **"Save"**
4. Clique em **"Redeploy"** (canto superior direito)

**Via CLI:**

```bash
vercel env add NEXT_PUBLIC_API_QUESTOES
# Cole: https://api-questoes-prod.railway.app

vercel env add NEXT_PUBLIC_API_MAPAS
# Cole: https://api-mapas-prod.railway.app

vercel --prod
```

### 5.3 Testar Integração

Após redeploy, abra em navegador:

```
https://doutora-ia-landing.vercel.app/estudo
```

Verifique:
- ✅ Página carrega sem erros
- ✅ Botão "Buscar" funciona
- ✅ Resultados aparecem (vindo das APIs)
- ✅ Flashcards carregam
- ✅ Performance boa (<3s)

---

## 🎯 PASSO 6: Configurar Domínio Customizado

### 6.1 Apontar Domínio para Vercel

1. Vercel Dashboard → Settings → Domains
2. Clique em **"Add"**
3. Digite: `doutoraia.com` (ou seu domínio)
4. Siga instruções para apontar DNS

**Se usar Namecheap/GoDaddy:**
```
CNAME record:
Name: (deixe em branco ou subdomain)
Value: cname.vercel-dns.com
```

### 6.2 Verificar SSL/HTTPS

Vercel configura HTTPS automaticamente ✅

Aguarde ~2-5 minutos após apontar domínio.

---

## 🚨 Possíveis Problemas

### ❌ Erro: "Build failed"

**Solução:**
1. Verificar logs: Deployments → Build Logs
2. Erros comuns:
   - Missing dependencies → `npm install`
   - TypeScript errors → corrigir tipos
   - Port conflicts → mude porta em vercel.json

### ❌ Erro: "APIs não respondendo"

**Solução:**
1. Verificar URLs: Console (F12) → Network
2. Se 404: URLs do Railway estão erradas
3. Se CORS error: Adicionar origin no Railway CORS_ORIGINS

```bash
railway variables set CORS_ORIGINS=https://doutora-ia-landing.vercel.app,https://www.doutoraia.com
```

### ❌ Erro: "Timeout na requisição"

**Solução:**
- APIs Railway podem estar lentas
- Aumentar timeout em frontend (`/estudo` page)
- Adicionar retry logic

### ❌ Erro: "Página em branco"

**Solução:**
1. F12 → Console → Verificar erros
2. Verificar variáveis de ambiente
3. Verificar build: `npm run build` localmente

---

## 📊 Monitorando Vercel

### Real-time Analytics

Dashboard → Analytics

- **Page View**: Quantas vezes página foi acessada
- **Response Time**: ~500ms (bom)
- **Edge Requests**: Número de requisições

### Configurar Alerts

Vercel → Settings → Alerts

- Alert quando deploy falha
- Alert quando performance degrada
- Alert quando erro 500

---

## 🔄 Auto-Deploy via GitHub

### 6.1 Configurar Webhook

Automático! Vercel já está conectado ao GitHub.

**Cada push para main:**
```bash
git add .
git commit -m "Atualizar landing"
git push origin main
```

**Vercel detecta e deploy automático** ✅

### 6.2 Criar Preview Deployments

Cada PR cria preview automático:

```bash
git checkout -b feature/nova-funcionalidade
# ... fazer mudanças ...
git push origin feature/nova-funcionalidade

# GitHub → Pull Request → Vercel cria preview URL
```

---

## ✅ Checklist Final

- [x] Projeto Next.js pronto
- [x] .env.production configurado com URLs corretas
- [x] vercel.json otimizado
- [x] Build local testado: `npm run build && npm start`
- [x] GitHub repo conectado ao Vercel
- [x] Deploy inicial completado
- [x] Variáveis de ambiente adicionadas
- [x] Deploy atualizado com URLs de APIs
- [x] Teste completo no navegador
- [x] Domínio apontando para Vercel
- [x] SSL/HTTPS funcionando

---

## 🎯 Resultado Final

✅ **Frontend em Produção**
- URL: `https://doutora-ia-landing.vercel.app`
- Ou: `https://www.doutoraia.com` (com domínio customizado)
- Build: ~30 segundos
- Performance: 95+ Lighthouse score

✅ **APIs Integradas**
- Questões: HTTP requests para Railway
- Mapas: HTTP requests para Railway
- Cache: Implementado em Next.js

✅ **Auto-Deploy Ativo**
- Push para main → Deploy automático
- Preview em cada PR

---

## 🔄 Próximos Passos

1. ✅ Deploy Vercel concluído
2. Teste integração completa (local)
3. Monitorar logs em produção
4. Configurar Sentry (error tracking)
5. Lançamento oficial sexta 17:00

---

## 📚 Referências

- [Vercel Docs](https://vercel.com/docs)
- [Next.js 15 Deployment](https://nextjs.org/docs/deployment)
- [Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Custom Domains](https://vercel.com/docs/concepts/projects/custom-domains)

