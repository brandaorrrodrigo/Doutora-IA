# 🚀 GUIA RÁPIDO - INICIAR AMBIENTE PARA TESTAR LOGIN

## ⚡ OPÇÃO MAIS RÁPIDA: Docker

### 1️⃣ Iniciar todos os serviços de uma vez:

```bash
# No diretório D:\doutora-ia
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f api

# Aguardar mensagem: "Uvicorn running on http://0.0.0.0:8080"
```

### 2️⃣ Testar se está funcionando:

```bash
# Testar API
curl http://localhost:8080/health

# Testar endpoints de auth
curl http://localhost:8080/debug/imports
```

### 3️⃣ Abrir no navegador:

```
http://localhost:3000/login.html
```

### 4️⃣ Testar login:

1. Clique em "Cadastro"
2. Preencha: nome, email, OAB, telefone, senha
3. Clique em "Criar Conta"
4. Verifique os logs do Docker para ver o email de verificação:
   ```bash
   docker-compose logs api | grep "EMAIL"
   ```

---

## 🔧 OPÇÃO ALTERNATIVA: Sem Docker

Se não tiver Docker, pode usar PostgreSQL local:

### 1️⃣ Instalar PostgreSQL:

**Windows:**
- Baixar: https://www.postgresql.org/download/windows/
- Instalar com pgAdmin
- Anotar a senha do usuário `postgres`

### 2️⃣ Criar banco de dados:

```bash
# Abrir pgAdmin ou usar terminal
createdb doutora_ia

# Ou no psql:
psql -U postgres
CREATE DATABASE doutora_ia;
\q
```

### 3️⃣ Configurar conexão:

Editar `D:\doutora-ia\api\.env`:

```env
# Mudar de:
PG_HOST=db

# Para:
PG_HOST=localhost

# E adicionar:
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/doutora_ia
```

### 4️⃣ Instalar dependências Python:

```bash
cd D:\doutora-ia\api
pip install -r requirements.txt
```

### 5️⃣ Iniciar API:

```bash
cd D:\doutora-ia\api
python main.py
```

### 6️⃣ Iniciar servidor web:

**Opção A: Python HTTP Server**
```bash
cd D:\doutora-ia\web\public
python -m http.server 3000
```

**Opção B: Live Server (VS Code)**
- Instalar extensão "Live Server"
- Abrir `web/public/login.html`
- Clicar com botão direito → "Open with Live Server"

### 7️⃣ Testar:

Abrir: http://localhost:3000/login.html

---

## 🐛 PROBLEMAS COMUNS:

### ❌ "WeasyPrint não encontrado"
**Solução:** Comentei temporariamente no código. Não afeta o login.

### ❌ "Porta 8080 já em uso"
**Solução:**
```bash
# Windows
netstat -ano | findstr "8080"
taskkill /PID [número_do_processo] /F

# Ou mudar porta no código
```

### ❌ "PostgreSQL connection refused"
**Solução:**
```bash
# Verificar se PostgreSQL está rodando
# Windows: Serviços → PostgreSQL → Iniciar

# Ou usar Docker
docker-compose up -d db
```

### ❌ "CORS error no navegador"
**Solução:** A API já está configurada para aceitar localhost:3000

---

## 🧪 TESTE PASSO A PASSO:

### Teste 1: Criar conta
1. Abrir http://localhost:3000/login.html
2. Clicar na aba "Cadastro"
3. Preencher:
   - Nome: João Silva
   - Email: joao@teste.com
   - OAB: OAB/SP 123456
   - Telefone: (11) 99999-9999
   - Senha: senha123
   - Confirmar senha: senha123
4. Aceitar termos
5. Clicar "Criar Conta"
6. ✅ Deve redirecionar para dashboard

### Teste 2: Ver email de verificação
```bash
# Ver logs da API
docker-compose logs api

# Procurar por:
# ╔════════════════════════════════════════════════════════════
# ║ EMAIL (DEBUG MODE - SMTP não configurado)
# ╠════════════════════════════════════════════════════════════
```

### Teste 3: Fazer login
1. Se foi redirecionado, voltar para /login.html
2. Inserir:
   - Email: joao@teste.com
   - Senha: senha123
3. Clicar "Entrar"
4. ✅ Deve redirecionar para dashboard

### Teste 4: Recuperar senha
1. Clicar "Esqueceu sua senha?"
2. Inserir email: joao@teste.com
3. Clicar "Enviar Link"
4. Verificar logs para pegar o link
5. Copiar link e abrir no navegador
6. Definir nova senha
7. ✅ Deve mostrar sucesso

---

## 📊 VERIFICAR SE ESTÁ FUNCIONANDO:

### API Status:
```bash
curl http://localhost:8080/
# Deve retornar JSON com version e status
```

### Auth Endpoints:
```bash
curl http://localhost:8080/debug/imports
# Deve mostrar auth_endpoints: loaded = true
```

### Banco de Dados:
```bash
docker-compose exec db psql -U postgres -d doutora_ia -c "\dt"
# Deve listar tabelas: lawyers, users, cases, etc.
```

---

## 🆘 SE NADA FUNCIONAR:

### Opção de emergência - Testar apenas HTML/JS:

1. Criar arquivo `test.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Teste Login</title>
</head>
<body>
    <h1>Teste de Login</h1>
    <form id="testForm">
        <input type="email" id="email" placeholder="Email" required><br>
        <input type="password" id="password" placeholder="Senha" required><br>
        <button type="submit">Testar</button>
    </form>
    <div id="result"></div>

    <script src="web/public/login.js"></script>
    <script>
        // Verificar se login.js foi carregado
        if (typeof saveTokens === 'function') {
            document.getElementById('result').innerHTML =
                '✅ login.js carregado com sucesso!';
        } else {
            document.getElementById('result').innerHTML =
                '❌ login.js NÃO foi carregado';
        }
    </script>
</body>
</html>
```

2. Abrir `test.html` no navegador
3. Se aparecer "✅ login.js carregado", o JS está funcionando

---

## 🎯 CHECKLIST FINAL:

- [ ] Docker iniciado OU PostgreSQL rodando
- [ ] API respondendo na porta 8080
- [ ] Servidor web na porta 3000
- [ ] Navegador aberto em localhost:3000/login.html
- [ ] Formulários carregando corretamente
- [ ] Console do navegador sem erros (F12)

---

**💡 DICA:** Comece pelo Docker - é muito mais fácil!

```bash
docker-compose up -d
# Aguardar 30 segundos
curl http://localhost:8080/health
# Se retornar JSON, está pronto!
```

Qualquer dúvida, me avise! 🚀
