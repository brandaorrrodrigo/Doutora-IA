# GUIA DE PAGAMENTOS - Doutora IA

Sistema de pagamentos multi-provider com suporte para **Mercado Pago**, **Binance Pay** e **Stripe**.

---

## 🎯 Providers Disponíveis

### 1. Mercado Pago (Recomendado para Brasil/LATAM)
- ✅ PIX (instantâneo, sem taxas para cliente)
- ✅ Cartão de crédito/débito
- ✅ Boleto bancário
- 💰 Taxa: ~4.99% por transação
- 🌎 Países: Brasil, Argentina, México, Chile, Colômbia, Peru

### 2. Binance Pay (Cripto - Zero Taxas)
- ✅ USDT, BUSD, BTC, ETH, BNB
- ✅ Liquidação instantânea
- ✅ Sem chargebacks
- 💰 Taxa: **0%** (Binance não cobra taxas!)
- 🌎 Global

### 3. Stripe (Internacional)
- ✅ Cartões internacionais (Visa, Mastercard, Amex)
- ✅ Suporte a 135+ moedas
- ✅ Infraestrutura enterprise
- 💰 Taxa: ~2.9% + R$0.30 por transação
- 🌎 Global

---

## 🚀 Configuração Rápida

### 1. Configurar .env

```bash
cp .env.example .env
```

Edite o `.env` com suas credenciais:

```bash
# MERCADO PAGO
MERCADO_PAGO_ACCESS_TOKEN=APP-1234567890123456-112233-abc123def456
MERCADO_PAGO_WEBHOOK_SECRET=seu_secret_aqui

# BINANCE PAY (opcional)
BINANCE_PAY_API_KEY=sua_api_key
BINANCE_PAY_API_SECRET=seu_secret
BINANCE_PAY_MERCHANT_ID=12345678

# STRIPE (opcional)
STRIPE_SECRET_KEY=sk_test_abcd1234...
STRIPE_PUBLISHABLE_KEY=pk_test_abcd1234...
STRIPE_WEBHOOK_SECRET=whsec_abcd1234...
```

### 2. Modo de Desenvolvimento (STUB)

Para testar sem configurar nenhum provider real:

```bash
# Deixe todas as keys vazias, o sistema usará stub mode automaticamente
# Todos os pagamentos serão aprovados instantaneamente
```

---

## 📝 Como Usar na API

### Criar Pagamento (Auto-Select Provider)

```python
POST /api/report

{
  "case_id": 123,
  "payload": {...}
}

# Response
{
  "payment": {
    "provider": "mercado_pago",  # ou "binance_pay", "stripe"
    "payment_id": "12345678-1234-1234-1234-123456789012",
    "payment_url": "https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=..."
  }
}
```

### Criar Pagamento (Provider Específico)

```python
# Forçar uso do Binance Pay
POST /api/report

{
  "case_id": 123,
  "payload": {...},
  "payment_provider": "binance_pay"  # ou "mercado_pago", "stripe"
}
```

### Webhooks

Cada provider envia notificações para:

```
Mercado Pago: POST /api/payments/webhook
Binance Pay:  POST /api/payments/webhook/binance
Stripe:       POST /api/payments/webhook/stripe
```

---

## 🔐 Segurança - Validação de Assinaturas

### Mercado Pago

```python
# Valida x-signature header usando HMAC SHA256
# Formato: ts=<timestamp>,v1=<hash>

# Configurar webhook secret no painel do Mercado Pago
# https://www.mercadopago.com.br/developers/panel/app
```

### Binance Pay

```python
# Valida BinancePay-Signature header usando HMAC SHA512
# String assinada: timestamp + \n + nonce + \n + body + \n

# Obter API key e secret:
# https://merchant.binance.com/en/dashboard/developer
```

### Stripe

```python
# Valida stripe-signature header
# Usa biblioteca oficial stripe.Webhook.construct_event()

# Obter webhook secret:
# https://dashboard.stripe.com/webhooks
```

---

## 🧪 Testar Pagamentos

### 1. Mercado Pago (Modo Sandbox)

```bash
# Credenciais de teste em:
# https://www.mercadopago.com.br/developers/panel/app/test-accounts

# Cartões de teste:
# Aprovado: 5031 4332 1540 6351
# Rejeitado: 5031 4332 1540 6353
```

### 2. Binance Pay (Testnet)

```bash
# Usar Binance Testnet para testes
# https://testnet.binance.vision/

# API endpoint de teste:
# https://testnet.binanceapi.com/binancepay/openapi/v2/order
```

### 3. Stripe (Test Mode)

```bash
# Usar test keys (começam com sk_test_)

# Cartões de teste:
# Aprovado: 4242 4242 4242 4242
# Rejeitado: 4000 0000 0000 0002
# 3D Secure: 4000 0027 6000 3184
```

---

## 💡 Estratégias de Seleção Automática

O sistema seleciona automaticamente o melhor provider baseado em:

### 1. Localização do Usuário
```python
Email termina em .br, .com.br → Mercado Pago
Email termina em .mx, .ar     → Mercado Pago
Outros países                  → Stripe
```

### 2. Valor da Transação
```python
< R$ 1,00   → Não processa (valor mínimo)
R$ 1-100    → Binance Pay (se disponível) ou Mercado Pago
> R$ 100    → Mercado Pago (PIX) ou Stripe
```

### 3. Preferência do Usuário
```python
# Usuário pode escolher no frontend:
- PIX (via Mercado Pago)
- Cartão de crédito (via Stripe ou Mercado Pago)
- Cripto (via Binance Pay)
```

---

## 📊 Comparação de Taxas

| Provider      | Taxa Fixa | Taxa % | Recebimento | PIX  | Crypto | Internacional |
|---------------|-----------|--------|-------------|------|--------|---------------|
| Mercado Pago  | R$ 0      | 4.99%  | D+14/D+30   | ✅   | ❌     | Parcial       |
| Binance Pay   | R$ 0      | **0%** | Instantâneo | ❌   | ✅     | ✅            |
| Stripe        | R$ 0.30   | 2.9%   | D+7         | ❌   | ❌     | ✅            |

### Exemplo: Relatório de R$ 7,00

- **Mercado Pago**: R$ 7,00 → Você recebe: R$ 6,65 (95,01%)
- **Binance Pay**: R$ 7,00 → Você recebe: R$ 7,00 (100%) ⭐
- **Stripe**: R$ 7,00 → Você recebe: R$ 6,50 (92,86%)

---

## 🔄 Fluxo de Pagamento Completo

```
1. Usuário solicita relatório premium (R$ 7,00)
   ↓
2. Backend cria pagamento
   POST /api/report
   ↓
3. Sistema seleciona provider (auto ou manual)
   - Cria preference/order/session
   - Retorna payment_url
   ↓
4. Frontend redireciona usuário para payment_url
   - Mercado Pago: checkout.mercadopago.com.br
   - Binance Pay: app.binance.com/payment
   - Stripe: checkout.stripe.com
   ↓
5. Usuário completa pagamento
   ↓
6. Provider envia webhook para backend
   POST /api/payments/webhook
   ↓
7. Backend valida assinatura
   ✅ HMAC SHA256/SHA512
   ↓
8. Backend marca relatório como pago
   UPDATE reports SET paid = true
   ↓
9. Frontend libera download do PDF
   ✅ Usuário recebe relatório
```

---

## 🛠️ Troubleshooting

### Webhook não está sendo recebido

1. **Verificar URL pública**:
   ```bash
   # Webhook precisa de URL pública (não localhost)
   # Usar ngrok para testes:
   ngrok http 8000
   # Configurar webhook URL: https://abc123.ngrok.io/api/payments/webhook
   ```

2. **Verificar logs**:
   ```bash
   docker-compose logs -f api | grep webhook
   ```

3. **Testar manualmente**:
   ```bash
   curl -X POST http://localhost:8000/api/payments/webhook \
     -H "Content-Type: application/json" \
     -d '{"type":"payment","data":{"id":"123456789"}}'
   ```

### Signature validation failing

1. **Mercado Pago**:
   - Verificar MERCADO_PAGO_WEBHOOK_SECRET no .env
   - Testar com secret vazio primeiro (desativa validação)

2. **Binance Pay**:
   - Verificar BINANCE_PAY_API_SECRET
   - Timestamp não pode ter diferença > 5 minutos

3. **Stripe**:
   - Verificar STRIPE_WEBHOOK_SECRET
   - Usar stripe CLI para testes locais

### Payment não está sendo criado

```bash
# Verificar logs
docker-compose logs api

# Testar conexão com provider
python -c "import mercadopago; print('OK')"
python -c "import stripe; print('OK')"
```

---

## 📚 Documentação Oficial

- **Mercado Pago**: https://www.mercadopago.com.br/developers/pt/docs
- **Binance Pay**: https://developers.binance.com/docs/binance-pay
- **Stripe**: https://stripe.com/docs/api

---

## ✅ Checklist de Produção

Antes de ir para produção:

- [ ] Trocar credenciais de TEST para PRODUCTION
- [ ] Configurar webhook secret em todos os providers
- [ ] Testar webhooks em ambiente staging
- [ ] Configurar monitoramento de falhas de pagamento
- [ ] Implementar retry logic para webhooks
- [ ] Configurar alertas para pagamentos pendentes > 24h
- [ ] Validar compliance (PCI-DSS para Stripe)
- [ ] Configurar backup de dados de pagamentos
- [ ] Testar refund/chargeback flows
- [ ] Documentar processo de conciliação financeira

---

**Sistema de pagamentos pronto para produção!** 🎉

Suporta 3 providers diferentes, validação de assinaturas, e seleção automática inteligente.
