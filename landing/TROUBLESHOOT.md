# Troubleshooting - Landing Page não carrega

## Problema: "Não é possível acessar esse site"

### Solução 1: Verificar se o servidor está rodando

1. Abra PowerShell em `D:\doutora-ia\landing`
2. Execute:
```powershell
npm run dev
```

3. Aguarde aparecer algo como:
```
✓ Ready in 3.2s
○ Local: http://localhost:3000
```

4. **NÃO feche** o PowerShell enquanto estiver testando
5. Abra o navegador e acesse o endereço que apareceu

### Solução 2: Limpar tudo e recomeçar

```powershell
# 1. Parar todos os processos Node
taskkill /F /IM node.exe

# 2. Ir para a pasta
cd D:\doutora-ia\landing

# 3. Limpar arquivos temporários
Remove-Item -Path .next -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path node_modules -Recurse -Force -ErrorAction SilentlyContinue

# 4. Reinstalar tudo
npm install

# 5. Rodar
npm run dev
```

### Solução 3: Testar em outra porta

Se a porta 3000 está ocupada, force outra porta:

```powershell
$env:PORT=3005; npm run dev
```

Depois acesse: http://localhost:3005

### Solução 4: Build de produção

Se dev não funcionar, teste o build:

```powershell
npm run build
npm start
```

### Solução 5: Verificar erros

Se aparecer erros vermelhos no terminal, copie e me envie para eu corrigir.

### Solução 6: Usar servidor simples HTTP

Se nada funcionar, vou criar uma versão HTML estática que você pode abrir diretamente no navegador sem precisar de servidor Node.js.

## Checklist de Diagnóstico

- [ ] PowerShell está aberto na pasta correta? (`D:\doutora-ia\landing`)
- [ ] Apareceu "✓ Ready" no terminal?
- [ ] O terminal está mostrando erros vermelhos?
- [ ] Você está acessando o endereço correto que apareceu no terminal?
- [ ] O navegador está bloqueando localhost? (tente outro navegador)
- [ ] Há antivírus bloqueando a porta 3000?

## Teste Rápido

Execute e me diga o resultado:

```powershell
cd D:\doutora-ia\landing
node --version
npm --version
npm run dev
```

Copie toda a saída do terminal e me envie.
