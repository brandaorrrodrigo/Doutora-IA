# Setup e Instalação - Doutora IA Landing Page

## Esquema de Cores Aplicado

Conforme solicitado, a landing page utiliza **tons de marrom** (elegante, profissional) combinados com **cores tech** (moderno, inovador):

### Paleta de Cores

```css
--background: #0b0e12        /* Azul escuro profundo (fundo) */
--foreground: #f4f4f5        /* Branco suave (texto) */
--primary: #8B6F47           /* Marrom médio sofisticado (CTAs, destaques) */
--primary-dark: #6B5335      /* Marrom escuro (hover states) */
--tech-blue: #00D4FF         /* Azul ciano tech (elementos tecnológicos) */
--tech-blue-dark: #0099CC    /* Azul tech escuro (hover) */
--accent: #B8860B            /* Marrom dourado (detalhes especiais) */
--accent-dark: #98700A       /* Dourado escuro (hover) */
```

### Onde as cores são usadas:

- **Marrom (#8B6F47)**: Botões principais, títulos destacados, ícones de benefícios
- **Azul Tech (#00D4FF)**: Checkmarks, estatísticas, elementos de tecnologia, gradientes
- **Marrom Dourado (#B8860B)**: Acentos especiais, badges, destaques premium
- **Gradientes**: Combinações de marrom + tech blue para efeitos visuais modernos

## Instalação Rápida

### 1. Instalar dependências

```bash
cd D:/doutora-ia/landing
npm install
```

### 2. Rodar em desenvolvimento

```bash
npm run dev
```

Acesse: http://localhost:3000

### 3. Build para produção

```bash
npm run build
npm start
```

## Estrutura Criada

✅ **13 Componentes React**:
- Header (navegação sticky)
- Hero (seção principal com CTAs)
- Proof (estatísticas sociais)
- HowItWorks (3 passos)
- Benefits (6 diferenciais)
- Demo (demonstrações)
- Pricing (5 planos com modais de pagamento)
- RoiCalculator (calculadora interativa)
- FAQ (perguntas frequentes com JSON-LD)
- CtaFinal (conversão final)
- LeadModal (captura de leads com LGPD)
- Footer (rodapé legal)
- Container (wrapper utilitário)

✅ **Páginas e APIs**:
- app/page.tsx (página principal)
- app/layout.tsx (SEO + metadata)
- app/api/lead/route.ts (endpoint de leads)

✅ **Configurações**:
- tailwind.config.ts (cores personalizadas)
- next.config.js (Next.js 15)
- tsconfig.json (TypeScript strict)
- package.json (dependências)

✅ **Documentação**:
- README.md (guia completo)
- SETUP.md (este arquivo)

## Funcionalidades Implementadas

### SEO e Performance
- Metadata completa (title, description, OG tags)
- JSON-LD schemas (Product + FAQPage)
- Sitemap automático via Next.js
- Font optimization
- Image optimization ready

### Acessibilidade
- ARIA labels e roles
- Navegação por teclado
- Focus states visíveis
- Reduced motion support
- Contraste WCAG AA

### Analytics
- Event tracking via dataLayer
- Eventos: CTA clicks, lead submits, ROI calculations, plan selections
- Google Tag Manager ready

### Integrações Preparadas
- **Stripe**: Estrutura para cartão/PIX (modais prontos)
- **Binance Pay**: Estrutura para USDT (modais prontos)
- API de leads com validação

## Próximos Passos

### 1. Configurar Cores no Tailwind

As cores já estão configuradas! Você pode usá-las em qualquer componente:

```tsx
<div className="bg-primary">Marrom</div>
<div className="bg-tech-blue">Tech Blue</div>
<div className="bg-accent">Dourado</div>
<div className="text-primary-dark">Marrom Escuro</div>
```

### 2. Adicionar Screenshots

Crie as imagens em `/public/screens/`:
- pesquisa.png (1200x800px)
- gerador.png (1200x800px)
- rodizio.png (1200x800px)
- painel.png (1200x800px)

### 3. Integrar Stripe

```bash
npm install @stripe/stripe-js stripe
```

Atualizar modal de pagamento em `components/Pricing.tsx`

### 4. Integrar Binance Pay

Adicionar SDK da Binance Pay e implementar checkout

### 5. Deploy Vercel

```bash
vercel
```

Ou conectar repositório GitHub no painel Vercel

### 6. Configurar Domínio

No Vercel:
1. Settings → Domains
2. Adicionar doutoraia.com
3. Configurar CNAME na Hostinger

## Troubleshooting

### Erro de cores não aplicadas

Execute:
```bash
npm run build
```

E reinicie o dev server

### TypeScript errors

```bash
npm run type-check
```

### Tailwind não reconhece classes

Verifique que `tailwind.config.ts` tem os paths corretos nos `content`

## Suporte

Dúvidas sobre a implementação:
- Revise README.md
- Consulte documentação Next.js 15
- Verifique componentes individuais

---

**Landing page criada com Next.js 15 + React 19 + TypeScript + Tailwind CSS**

Esquema de cores: Marrom sofisticado + Tech Blue moderno 🎨
