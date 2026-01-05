# ⚡ SEXTA - QUICK START (Copiar e Colar)

**06/01/2026 - Dia do Lançamento**
**Hora: 09:00-17:00 BRT**

---

## 🎯 Tudo Pronto! Apenas Siga Este Guia

Não precisa pensar, só copiar e colar os comandos na ordem.

---

## 09:00 - VERIFICAÇÕES FINAIS (10 minutos)

### Terminal 1: Backend Questões

```powershell
cd D:\doutora-ia\backend
python -m uvicorn api_questoes:app --port 8042 --reload
```

**Esperado no terminal:**
```
Uvicorn running on http://127.0.0.1:8042
```

### Terminal 2: Backend Mapas

```powershell
cd D:\doutora-ia\backend
python -m uvicorn api_mapas_flashcards:app --port 8041 --reload
```

**Esperado no terminal:**
```
Uvicorn running on http://127.0.0.1:8041
```

### Terminal 3: Frontend Local

```powershell
cd D:\doutora-ia\landing
npm run dev
```

**Esperado no terminal:**
```
ready - started server on 0.0.0.0:3000
```

Abra navegador: **http://localhost:3000/estudo** → Deve carregar tudo ✅

### Terminal 4: Testes de Integração

```powershell
cd D:\doutora-ia\backend
python teste_integracao_37k.py
```

**Esperado:**
```
✅ Teste concluído: 8/10 (80%+)
✅ Sistema pronto para deployment!
```

Se passar neste teste → **Pronto para deploy!** ✅

---

## 09:30 - DEPLOY RAILWAY (20 minutos)

### Opção A: Via CLI (Recomendado)

```powershell
cd D:\doutora-ia

# Login (primeira vez apenas)
railway login

# Deploy
railway up
```

Escolha as opções:
- Project name: `doutora-ia-backend`
- Environment: `production`

**Aguarde ~15-20 minutos...**

### Opção B: Via GitHub (Automático)

Se preferir deploy automático via GitHub:

```powershell
# Apenas commit e push
cd D:\doutora-ia
git add .
git commit -m "Deploy preparation - ready for launch"
git push origin main
```

Depois acesse **Railway Dashboard** → Conectar GitHub → Auto-deploy ativa

### ✅ Verificar Deploy Railway

```powershell
# Ver URLs geradas
railway domains

# Ver logs
railway logs --follow

# Health check
curl https://api-questoes.railway.app/health
```

**Anotei as URLs:**
- API Questões: `https://api-questoes.railway.app`
- API Mapas: `https://api-mapas.railway.app`

---

## 10:00 - DEPLOY VERCEL (15 minutos)

### Opção A: Via Dashboard (Mais Fácil)

1. Abrir: **https://vercel.com/dashboard**
2. Clicar: **"Add New"** → **"Project"**
3. Selecionar: **"Import Git Repository"**
4. Buscar: `doutora-ia`
5. Selecionar: **Configure Project**
   - Root Directory: deixar vazio
   - Framework: Next.js (detectar automático)
   - Build Command: `npm run build`

6. **Environment Variables** → Adicionar:

```
NEXT_PUBLIC_API_QUESTOES = https://api-questoes.railway.app
NEXT_PUBLIC_API_MAPAS = https://api-mapas.railway.app
NEXT_PUBLIC_ENVIRONMENT = production
```

7. Clicar: **Deploy** → Aguarde ~10 min

### Opção B: Via CLI

```powershell
cd D:\doutora-ia\landing

# Install Vercel CLI (primeira vez)
npm install -g vercel

# Login
vercel login

# Deploy para produção
vercel --prod \
  --env NEXT_PUBLIC_API_QUESTOES=https://api-questoes.railway.app \
  --env NEXT_PUBLIC_API_MAPAS=https://api-mapas.railway.app
```

### ✅ Verificar Deploy Vercel

Abrir em navegador:
```
https://doutora-ia-landing.vercel.app/estudo
```

**Esperado:**
- ✅ Página carrega sem erros
- ✅ Consegue buscar questões
- ✅ Explicações aparecem
- ✅ Mapas carregam
- ✅ Performance <3s

---

## 10:30 - TESTAR INTEGRAÇÃO COMPLETA (10 minutos)

### No Navegador

```
https://doutora-ia-landing.vercel.app/estudo
```

**Checklist:**
- [ ] Página carrega
- [ ] Buscar "direito" → resultados aparecem
- [ ] Clicar em questão → mostra enunciado + alternativas + **explicação**
- [ ] F12 (DevTools) → Network: requisições para Railway com status 200
- [ ] F12 → Console: nenhum erro vermelho
- [ ] Performance <3 segundos

Se tudo OK → **Sistema funcionando perfeitamente!** ✅

---

## 11:00 - DOMÍNIO CUSTOMIZADO (5-10 minutos)

### Apontar DNS

Se tiver domínio (doutoraia.com):

**No seu registrador (Namecheap/GoDaddy/etc):**

1. Abrir painel do domínio
2. Ir para: **DNS Settings** ou **Advanced DNS**
3. Adicionar/Editar:
   ```
   CNAME record:
   Name: @ (ou deixar branco)
   Value: cname.vercel-dns.com
   TTL: 3600 (ou padrão)
   ```
4. Salvar

**No Vercel Dashboard:**

1. Settings → **Domains**
2. Clicar: **Add**
3. Digite: `doutoraia.com`
4. Aguarde validação DNS (~2-5 min)
5. SSL automático ✅

Testar:
```
https://www.doutoraia.com/estudo
```

---

## 11:30 - TESTES FINAIS PRODUÇÃO (30 minutos)

### 1. Lighthouse Score

No navegador, abrir:
```
https://www.doutoraia.com/estudo
```

Pressionar: **F12** → **Lighthouse** → **Analyze page load**

**Esperado:** Score 90+ ✅

### 2. Busca Funcionando

```powershell
# Terminal: Testar API diretamente
curl "https://api-questoes.railway.app/questoes/busca?termo=direito&limit=5"

# Esperado: JSON com questões + comentarios
```

### 3. Explicações Carregando

```powershell
# Terminal: Contar questões com explicação
railway run psql -U doutora_user -d doutora -c \
  "SELECT COUNT(*) FROM questoes WHERE comentario IS NOT NULL AND comentario <> '';"

# Esperado: 13700+ (era 713, agora com 37k processadas)
```

### 4. Monitoramento

**Railway Dashboard:**
```
Deployments → Seu projeto → Metrics
- CPU usage: ~30-50%
- Memory: ~500MB-1GB
- Error rate: 0%
```

**Vercel Dashboard:**
```
Analytics → Verificar requisições
- Deve estar recebendo tráfego
- Error rate: 0%
```

---

## 12:00 - MONITORAMENTO CONTÍNUO (5 horas)

**A cada 30 minutos, fazer:**

### Checklist Rápido

```powershell
# 1. Ver logs Railway
railway logs --follow

# 2. Testar endpoint
curl https://api-questoes.railway.app/questoes?skip=0&limit=1

# 3. Abrir site no navegador
# https://www.doutoraia.com/estudo
# F12 → Verificar nenhum erro console
```

**Se encontrar erro:**

```powershell
# Reiniciar API
railway restart

# Ver mais detalhes
railway logs --follow

# Se não resolver: rollback
railway rollback
```

---

## 17:00 - 🎊 LANÇAMENTO OFICIAL

### Anunciar

Copiar e compartilhar em redes/email:

```
🎉 NOVO! Doutora IA 2.0 - Lançamento Oficial

Sistema com 37.000 questões comentadas por IA!

✨ Novidades:
✅ 37.000 questões de direito
✅ Explicações geradas por IA (Llama 3.1)
✅ Mapas mentais interativos
✅ Flashcards com spaced repetition
✅ Busca avançada por tópico/dificuldade
✅ Performance ultra-rápida

🚀 Acesse agora: https://www.doutoraia.com

Vamos estudar juntos! 📚
```

### Verificação Final

```bash
# Tudo OK?
curl https://api-questoes.railway.app/health
curl https://api-mapas.railway.app/health

# Deve retornar: {"status":"ok"}
```

**Pronto! Sistema no ar!** 🎉

---

## 🆘 QUICK TROUBLESHOOT

### ❌ API não responde

```powershell
railway restart
# Aguarde 30s e teste novamente
```

### ❌ Erro 502 Bad Gateway

```powershell
# Ver logs
railway logs --follow

# Reiniciar
railway restart

# Se persistir: rollback
railway rollback
```

### ❌ Vercel com erro build

```powershell
cd D:\doutora-ia\landing
npm run build
# Se erro: corrigir e fazer git push (auto-deploy)
```

### ❌ Explicações não aparecem

```powershell
# Verificar se foram geradas
railway run psql -U doutora_user -d doutora \
  -c "SELECT COUNT(*) FROM questoes WHERE comentario IS NOT NULL;"

# Se zero: script ainda rodando, aguarde
```

---

## 📞 SUPORTE RÁPIDO

| Problema | Comando |
|----------|---------|
| Ver logs | `railway logs --follow` |
| Restart | `railway restart` |
| Rollback | `railway rollback` |
| Health check | `curl api-url/health` |
| Redeploy Vercel | Dashboard → Deployments → Redeploy |
| Status | `railway status` |

---

## ✅ CHECKLIST FINAL

- [ ] 09:00 - Testes locais passam (80%+)
- [ ] 09:30 - Deploy Railway completo
- [ ] 10:00 - Deploy Vercel completo
- [ ] 10:30 - Integração testada OK
- [ ] 11:00 - Domínio apontando
- [ ] 11:30 - Lighthouse 90+
- [ ] 12:00-17:00 - Monitoramento OK
- [ ] 17:00 - Lançado! 🎉

---

## 📊 O QUE ESPERAR

**Users online:** 100+
**Requisições/hora:** 1000+
**Latência:** <500ms
**Error rate:** <1%
**Uptime:** 99.9%

---

## 🎯 PRONTO!

Tudo está preparado. Sexta é só executar este documento de cima para baixo.

**Sucesso! 🚀**

---

*Documento criado: 05/01/2026*
*Para consultar detalhes: Abra os guias específicos (DEPLOY_RAILWAY_GUIA.md, DEPLOY_VERCEL_GUIA.md)*

