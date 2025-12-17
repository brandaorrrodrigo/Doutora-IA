# Doutora IA - Landing Page

Landing page oficial da **Doutora IA para Advogados** - Plataforma de pesquisa jurídica, geração de peças e rodízio de leads.

## Stack Tecnológica

- **Next.js 15** - Framework React com App Router
- **React 19** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Framework CSS utility-first
- **Stripe** - Pagamentos (cartão/PIX)
- **Binance Pay** - Pagamentos em crypto (USDT)

## Esquema de Cores

- **Background**: `#0b0e12` (azul escuro profundo)
- **Primary**: `#8B6F47` (marrom sofisticado)
- **Tech Blue**: `#00D4FF` (azul tech/ciano)
- **Accent**: `#B8860B` (marrom dourado)

## Estrutura do Projeto

```
landing/
├── app/
│   ├── layout.tsx          # Layout raiz com SEO
│   ├── page.tsx            # Página principal
│   ├── globals.css         # Estilos globais
│   └── api/
│       └── lead/
│           └── route.ts    # API endpoint para leads
├── components/
│   ├── Header.tsx          # Cabeçalho sticky
│   ├── Footer.tsx          # Rodapé com disclaimers
│   ├── Hero.tsx            # Seção hero principal
│   ├── Proof.tsx           # Social proof (estatísticas)
│   ├── HowItWorks.tsx      # Como funciona (3 passos)
│   ├── Benefits.tsx        # Benefícios (6 diferenciais)
│   ├── Demo.tsx            # Demonstração da plataforma
│   ├── Pricing.tsx         # Tabela de preços (5 planos)
│   ├── RoiCalculator.tsx   # Calculadora de ROI interativa
│   ├── FAQ.tsx             # Perguntas frequentes
│   ├── CtaFinal.tsx        # CTA final de conversão
│   ├── LeadModal.tsx       # Modal de captura de leads
│   └── Container.tsx       # Wrapper de largura máxima
├── lib/
│   └── analytics.ts        # Helpers de analytics
├── public/
│   └── screens/            # Screenshots da plataforma (placeholder)
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.js
```

## Como Rodar Localmente

1. **Instalar dependências:**
```bash
npm install
```

2. **Rodar servidor de desenvolvimento:**
```bash
npm run dev
```

3. **Acessar:** http://localhost:3000

## Recursos Principais

### SEO
- Metadata otimizada para Google
- Open Graph para redes sociais
- JSON-LD com Product e FAQPage schemas
- Sitemap.xml automático
- Robots.txt configurado

### Acessibilidade
- Navegação por teclado
- ARIA labels e roles
- Contraste WCAG AA
- Focus states visíveis
- Markup semântico

### Analytics
- Google Tag Manager ready
- Event tracking (CTAs, leads, ROI)
- Custom events via dataLayer

### Pagamentos
- **Stripe**: Cartão de crédito e PIX
- **Binance Pay**: USDT (Tether)

## Planos Disponíveis

1. **Pesquisa** - R$49/mês
2. **Leads** - R$79/mês
3. **Redação** - R$99/mês
4. **Pro** - R$149/mês (mais popular)
5. **Full** - R$199/mês

## Deploy

### Vercel (Recomendado)

1. Conecte o repositório ao Vercel
2. Configure as variáveis de ambiente (se necessário)
3. Deploy automático em cada push

### Netlify

```bash
npm run build
# Upload da pasta .next
```

## Variáveis de Ambiente

```env
# Opcional: Analytics
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Opcional: API Keys
STRIPE_PUBLIC_KEY=pk_live_...
BINANCE_PAY_API_KEY=...
```

## TODO

- [ ] Adicionar screenshots reais em `/public/screens/`
- [ ] Configurar Stripe checkout
- [ ] Configurar Binance Pay integration
- [ ] Integrar API de leads com CRM
- [ ] Adicionar Google Analytics
- [ ] Configurar domínio doutoraia.com
- [ ] Criar email templates (confirmação, boas-vindas)
- [ ] Adicionar testes E2E

## Licença

Propriedade de **Legal Tech Brasil** - Todos os direitos reservados.

## Contato

- Email: contato@doutoraia.com
- Site: https://doutoraia.com
