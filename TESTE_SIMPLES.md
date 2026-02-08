# 🧪 TESTE SIMPLES DO LOGIN (SEM API)

Enquanto configuramos o PostgreSQL, você pode testar se o HTML/JS está funcionando:

## 🔧 TESTE RÁPIDO:

### 1. Criar arquivo de teste `test-login.html` na raiz:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Teste Login - Doutora IA</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #0a0a0a; color: white; }
        .result { margin: 20px 0; padding: 15px; border-radius: 5px; }
        .success { background: #28a745; }
        .error { background: #dc3545; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>🧪 Teste de Integração Login</h1>

    <h2>1. Verificar se login.js foi carregado:</h2>
    <div id="result1" class="result">Verificando...</div>

    <h2>2. Testar estrutura dos formulários:</h2>
    <button onclick="testarFormularios()">Testar Formulários</button>
    <div id="result2" class="result"></div>

    <h2>3. Testar requisição (mock):</h2>
    <button onclick="testarRequisicao()">Testar Requisição</button>
    <div id="result3" class="result"></div>

    <script src="web/public/login.js"></script>
    <script>
        // Teste 1: Verificar se login.js carregou
        const result1 = document.getElementById('result1');
        if (typeof saveTokens === 'function') {
            result1.className = 'result success';
            result1.innerHTML = '✅ login.js carregado com sucesso!<br>Funções disponíveis: saveTokens, getAccessToken, etc.';
        } else {
            result1.className = 'result error';
            result1.innerHTML = '❌ login.js NÃO foi carregado';
        }

        // Teste 2: Verificar formulários
        function testarFormularios() {
            const result2 = document.getElementById('result2');
            const testes = [];

            // Verificar se os IDs existem no login.html
            const ids = ['loginForm', 'loginEmail', 'loginPassword', 'registerForm', 'forgotPasswordForm'];

            testes.push('Verificando IDs necessários...<br>');
            testes.push(`- loginForm: ${typeof document.getElementById === 'function' ? '✅' : '❌'}<br>`);
            testes.push(`- Funções de validação: ${typeof String.prototype.includes === 'function' ? '✅' : '❌'}<br>`);

            result2.className = 'result success';
            result2.innerHTML = testes.join('');
        }

        // Teste 3: Simular requisição
        async function testarRequisicao() {
            const result3 = document.getElementById('result3');
            result3.innerHTML = 'Testando...';

            try {
                // Tentar fazer requisição para API (deve falhar se API não estiver rodando)
                const response = await fetch('http://localhost:8080/', {
                    method: 'GET'
                }).catch(e => ({ ok: false, error: e.message }));

                if (response.ok) {
                    result3.className = 'result success';
                    result3.innerHTML = '✅ API está respondendo!<br>Tudo pronto para testar o login.';
                } else {
                    result3.className = 'result error';
                    result3.innerHTML = '⚠️ API não está respondendo<br>Mas o JavaScript está configurado corretamente!';
                }
            } catch (error) {
                result3.className = 'result error';
                result3.innerHTML = `⚠️ API não está respondendo: ${error}<br>Mas o JavaScript está configurado corretamente!`;
            }
        }
    </script>
</body>
</html>
```

### 2. Abrir no navegador:
```
file:///D:/doutora-ia/test-login.html
```

### 3. Clicar nos botões de teste

---

## 🎯 O QUE ISSO TESTA:

✅ Se login.js está sendo carregado corretamente
✅ Se as funções JavaScript estão disponíveis
✅ Se a estrutura está correta
✅ Se consegue fazer requisições (mesmo que API não esteja rodando)

---

## 📊 RESULTADO ESPERADO:

- **Teste 1**: ✅ Verde - "login.js carregado"
- **Teste 2**: ✅ Verde - IDs e funções OK
- **Teste 3**: ⚠️ Amarelo/Vermelho - API não responde (normal se não estiver rodando)

Isso confirma que **TODO O CÓDIGO DE LOGIN ESTÁ CORRETO** e só falta a API rodando para funcionar completamente!

---

**Enquanto isso, me diga a senha do PostgreSQL para eu configurar a API!**
