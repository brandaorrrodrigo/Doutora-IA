# Doutora IA - Frontend (Next.js 14)

Frontend completo da plataforma Doutora IA construído com Next.js 14, TypeScript, Tailwind CSS e shadcn/ui.

## Tecnologias

- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui** (componentes)
- **TanStack Query** (data fetching)
- **Axios** (HTTP client)
- **React Hook Form** (formulários)
- **Zod** (validação)

## Estrutura

```
web-app/
├── app/                      # App Router (Next.js 14)
│   ├── page.tsx             # Landing page
│   ├── analise/             # Análise de caso
│   ├── dashboard/           # Dashboard usuário
│   ├── advogado/            # Dashboards advogado
│   │   ├── leads/
│   │   ├── pesquisa/
│   │   └── gerador/
│   ├── auth/                # Login e Register
│   └── legal/               # Privacidade e Termos
├── components/
│   └── ui/                  # Componentes shadcn/ui
├── services/
│   └── api.ts               # Cliente API
├── lib/
│   └── utils.ts             # Utilitários
└── types/
    └── index.ts             # TypeScript types
```

## Instalação

```bash
# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
# Edite .env.local e configure NEXT_PUBLIC_API_URL

# Rodar em desenvolvimento
npm run dev

# Build para produção
npm run build
npm start
```

## Variáveis de Ambiente

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Páginas Implementadas

### Públicas
- `/` - Landing page (hero da balança)
- `/analise` - Análise gratuita de caso
- `/auth/login` - Login
- `/auth/register` - Cadastro
- `/legal/privacidade` - Política de Privacidade
- `/legal/termos` - Termos de Uso

### Autenticadas
- `/dashboard` - Dashboard do usuário
- `/advogado/leads` - Feed de leads (advogados)
- `/advogado/pesquisa` - Pesquisa jurídica
- `/advogado/gerador` - Gerador de peças

## Componentes UI

Componentes baseados em shadcn/ui:
- `Button` - Botões com variantes
- `Card` - Cards para conteúdo
- `Input` - Inputs de formulário
- `Label` - Labels de formulário
- `Textarea` - Textarea

## Serviços API

Todos os métodos da API estão em `services/api.ts`:

```typescript
apiClient.search()          // Busca jurídica
apiClient.analyzeCase()     // Análise de caso
apiClient.generateReport()  // Gerar relatório PDF
apiClient.login()           // Login
apiClient.register()        // Cadastro
// ... e outros
```

## Autenticação

O sistema usa JWT armazenado em `localStorage`:
- Token salvo após login
- Interceptor Axios adiciona token automaticamente
- Redirect para /auth/login se não autenticado

## Deploy

### Vercel (Recomendado)
```bash
npm install -g vercel
vercel
```

### Docker
```bash
docker build -t doutora-ia-web .
docker run -p 3000:3000 doutora-ia-web
```

## Próximos Passos

- [ ] Adicionar página de visualização de relatório
- [ ] Implementar carrinho de citações
- [ ] Dashboard com gráficos
- [ ] Notificações em tempo real
- [ ] Modo dark
- [ ] PWA

## Licença

MIT
