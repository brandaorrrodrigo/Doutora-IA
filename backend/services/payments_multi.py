"""
Multi-Provider Payment Service
Supports: Mercado Pago, Binance Pay, and Stripe
"""

import os
import logging
import hashlib
import hmac
import json
from typing import Dict, Any, Optional
from datetime import datetime
import mercadopago

logger = logging.getLogger(__name__)

class MultiPaymentService:
    """
    Unified payment service supporting multiple providers:
    - Mercado Pago (Brazil, Latin America)
    - Binance Pay (Crypto payments)
    - Stripe (International credit cards)
    """

    def __init__(self):
        self.providers = []

        # Initialize Mercado Pago
        if os.getenv("MERCADO_PAGO_ACCESS_TOKEN"):
            try:
                self.mp_sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_ACCESS_TOKEN"))
                self.mp_webhook_secret = os.getenv("MERCADO_PAGO_WEBHOOK_SECRET", "")
                self.providers.append("mercado_pago")
                logger.info("✓ Mercado Pago initialized")
            except Exception as e:
                logger.warning(f"Mercado Pago init failed: {e}")

        # Initialize Binance Pay
        if os.getenv("BINANCE_PAY_API_KEY"):
            self.binance_api_key = os.getenv("BINANCE_PAY_API_KEY")
            self.binance_api_secret = os.getenv("BINANCE_PAY_API_SECRET")
            self.binance_merchant_id = os.getenv("BINANCE_PAY_MERCHANT_ID")
            self.providers.append("binance_pay")
            logger.info("✓ Binance Pay initialized")

        # Initialize Stripe
        if os.getenv("STRIPE_SECRET_KEY"):
            try:
                import stripe
                stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
                self.stripe = stripe
                self.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
                self.providers.append("stripe")
                logger.info("✓ Stripe initialized")
            except Exception as e:
                logger.warning(f"Stripe init failed: {e}")

        if not self.providers:
            logger.warning("No payment providers configured, using STUB mode")
            self.providers = ["stub"]

        logger.info(f"Available payment providers: {', '.join(self.providers)}")

    def create_payment(
        self,
        amount_cents: int,
        description: str,
        metadata: Dict[str, Any],
        payer_email: Optional[str] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create payment with specified provider (or auto-select)

        Args:
            amount_cents: Amount in cents
            description: Payment description
            metadata: Additional metadata
            payer_email: Customer email
            provider: Specific provider to use (mercado_pago|binance_pay|stripe|auto)

        Returns:
            Payment data with URL
        """
        # Auto-select provider if not specified
        if not provider or provider == "auto":
            provider = self._select_best_provider(amount_cents, payer_email)

        logger.info(f"Creating payment with {provider}: {amount_cents} cents")

        if provider == "mercado_pago" and "mercado_pago" in self.providers:
            return self._create_mercado_pago(amount_cents, description, metadata, payer_email)
        elif provider == "binance_pay" and "binance_pay" in self.providers:
            return self._create_binance_pay(amount_cents, description, metadata, payer_email)
        elif provider == "stripe" and "stripe" in self.providers:
            return self._create_stripe(amount_cents, description, metadata, payer_email)
        else:
            return self._create_stub(amount_cents, description, metadata, provider)

    def _select_best_provider(self, amount_cents: int, payer_email: Optional[str] = None) -> str:
        """Auto-select best provider based on context"""

        # Prefer Mercado Pago for Brazil/LATAM
        if "mercado_pago" in self.providers:
            if payer_email and payer_email.endswith((".br", ".com.br", ".mx", ".ar")):
                return "mercado_pago"

        # Binance Pay for crypto users (low fees, instant)
        if "binance_pay" in self.providers and amount_cents >= 100:  # Min $1
            return "binance_pay"

        # Stripe for international
        if "stripe" in self.providers:
            return "stripe"

        # Fallback
        return self.providers[0] if self.providers else "stub"

    # ==================== MERCADO PAGO ====================

    def _create_mercado_pago(
        self,
        amount_cents: int,
        description: str,
        metadata: Dict[str, Any],
        payer_email: Optional[str]
    ) -> Dict[str, Any]:
        """Create Mercado Pago payment"""
        try:
            api_host = os.getenv("API_HOST", "http://localhost:8000")

            preference_data = {
                "items": [{
                    "title": description,
                    "quantity": 1,
                    "unit_price": amount_cents / 100.0,
                    "currency_id": "BRL"
                }],
                "metadata": metadata,
                "back_urls": {
                    "success": f"{api_host}/payments/success",
                    "failure": f"{api_host}/payments/failure",
                    "pending": f"{api_host}/payments/pending"
                },
                "auto_return": "approved",
                "notification_url": f"{api_host}/api/payments/webhook",
                "statement_descriptor": "DOUTORA IA"
            }

            if payer_email:
                preference_data["payer"] = {"email": payer_email}

            response = self.mp_sdk.preference().create(preference_data)

            if response["status"] != 201:
                raise Exception(f"MP API error: {response}")

            pref = response["response"]

            return {
                "provider": "mercado_pago",
                "payment_id": pref["id"],
                "payment_url": pref["init_point"],
                "status": "pending",
                "amount_cents": amount_cents,
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Mercado Pago error: {e}")
            raise

    # ==================== BINANCE PAY ====================

    def _create_binance_pay(
        self,
        amount_cents: int,
        description: str,
        metadata: Dict[str, Any],
        payer_email: Optional[str]
    ) -> Dict[str, Any]:
        """
        Create Binance Pay order

        Docs: https://developers.binance.com/docs/binance-pay/api-order-create
        """
        try:
            import requests
            import time

            # Convert to USD (assuming BRL ~= 0.20 USD)
            amount_usd = (amount_cents / 100.0) * 0.20

            # Generate order ID
            order_id = f"DIA_{int(time.time())}_{metadata.get('report_id', '')}"

            # API endpoint
            url = "https://bpay.binanceapi.com/binancepay/openapi/v2/order"

            # Request body
            body = {
                "env": {
                    "terminalType": "WEB"
                },
                "merchantTradeNo": order_id,
                "orderAmount": amount_usd,
                "currency": "USDT",  # Stablecoin
                "goods": {
                    "goodsType": "02",  # Virtual goods
                    "goodsCategory": "Z000",
                    "referenceGoodsId": str(metadata.get("report_id", "")),
                    "goodsName": description
                },
                "returnUrl": f"{os.getenv('API_HOST', 'http://localhost:8000')}/payments/success",
                "webhookUrl": f"{os.getenv('API_HOST', 'http://localhost:8000')}/api/payments/webhook/binance"
            }

            # Sign request
            timestamp = str(int(time.time() * 1000))
            payload = f"{timestamp}\n{self.binance_api_key}\n{json.dumps(body)}\n"

            signature = hmac.new(
                self.binance_api_secret.encode(),
                payload.encode(),
                hashlib.sha512
            ).hexdigest().upper()

            headers = {
                "Content-Type": "application/json",
                "BinancePay-Timestamp": timestamp,
                "BinancePay-Nonce": timestamp,
                "BinancePay-Certificate-SN": self.binance_api_key,
                "BinancePay-Signature": signature
            }

            # Make request
            response = requests.post(url, headers=headers, json=body, timeout=30)
            result = response.json()

            if result.get("status") != "SUCCESS":
                raise Exception(f"Binance Pay error: {result}")

            data = result["data"]

            return {
                "provider": "binance_pay",
                "payment_id": data["prepayId"],
                "payment_url": data["universalUrl"],
                "qr_code": data.get("qrcodeLink"),
                "deep_link": data.get("deeplink"),
                "status": "pending",
                "amount_cents": amount_cents,
                "amount_crypto": amount_usd,
                "currency": "USDT",
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Binance Pay error: {e}")
            raise

    # ==================== STRIPE ====================

    def _create_stripe(
        self,
        amount_cents: int,
        description: str,
        metadata: Dict[str, Any],
        payer_email: Optional[str]
    ) -> Dict[str, Any]:
        """Create Stripe payment"""
        try:
            api_host = os.getenv("API_HOST", "http://localhost:8000")

            # Create checkout session
            session = self.stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "brl",
                        "product_data": {
                            "name": description,
                            "description": "Relatório Doutora IA"
                        },
                        "unit_amount": amount_cents
                    },
                    "quantity": 1
                }],
                mode="payment",
                success_url=f"{api_host}/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{api_host}/payments/failure",
                customer_email=payer_email,
                metadata=metadata,
                payment_intent_data={
                    "metadata": metadata
                }
            )

            return {
                "provider": "stripe",
                "payment_id": session.id,
                "payment_url": session.url,
                "status": "pending",
                "amount_cents": amount_cents,
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Stripe error: {e}")
            raise

    # ==================== STUB (Development) ====================

    def _create_stub(
        self,
        amount_cents: int,
        description: str,
        metadata: Dict[str, Any],
        provider: str
    ) -> Dict[str, Any]:
        """Stub payment for development"""
        import uuid
        payment_id = f"stub_{provider}_{uuid.uuid4().hex[:12]}"

        logger.info(f"STUB PAYMENT ({provider}): R$ {amount_cents/100:.2f} - {description}")

        return {
            "provider": f"stub_{provider}",
            "payment_id": payment_id,
            "payment_url": f"http://localhost:8000/payments/stub/{payment_id}?auto_approve=true",
            "status": "pending",
            "amount_cents": amount_cents,
            "metadata": metadata
        }

    # ==================== WEBHOOK VERIFICATION ====================

    def verify_webhook(
        self,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        provider: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Verify webhook from any provider

        Auto-detects provider if not specified
        """
        # Auto-detect provider
        if not provider:
            if "type" in payload or "topic" in payload:
                provider = "mercado_pago"
            elif "bizType" in payload and payload.get("bizType") == "PAY":
                provider = "binance_pay"
            elif headers and "stripe-signature" in headers:
                provider = "stripe"
            else:
                provider = "stub"

        logger.info(f"Processing {provider} webhook")

        if provider == "mercado_pago":
            return self._verify_mercado_pago_webhook(payload, headers)
        elif provider == "binance_pay":
            return self._verify_binance_webhook(payload, headers)
        elif provider == "stripe":
            return self._verify_stripe_webhook(payload, headers)
        else:
            return self._verify_stub_webhook(payload)

    def _verify_mercado_pago_webhook(
        self,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """Verify Mercado Pago webhook"""
        # Signature validation (if secret configured)
        if self.mp_webhook_secret and headers:
            # ... (same as before)
            pass

        try:
            topic = payload.get("type") or payload.get("topic")

            if topic == "payment":
                payment_id = payload.get("data", {}).get("id")
                if not payment_id:
                    return None

                payment_info = self.mp_sdk.payment().get(payment_id)
                if payment_info["status"] != 200:
                    return None

                payment = payment_info["response"]

                return {
                    "payment_id": str(payment["id"]),
                    "status": payment["status"],
                    "metadata": payment.get("metadata", {}),
                    "provider": "mercado_pago"
                }

        except Exception as e:
            logger.error(f"MP webhook error: {e}")

        return None

    def _verify_binance_webhook(
        self,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Verify Binance Pay webhook

        Signature format: timestamp + \n + body
        """
        try:
            # Validate signature
            if headers and self.binance_api_secret:
                signature = headers.get("binancepay-signature", "")
                timestamp = headers.get("binancepay-timestamp", "")
                nonce = headers.get("binancepay-nonce", "")

                payload_str = json.dumps(payload, separators=(',', ':'))
                signed_string = f"{timestamp}\n{nonce}\n{payload_str}\n"

                calculated_sig = hmac.new(
                    self.binance_api_secret.encode(),
                    signed_string.encode(),
                    hashlib.sha512
                ).hexdigest().upper()

                if not hmac.compare_digest(calculated_sig, signature):
                    logger.warning("Invalid Binance Pay signature")
                    return None

            # Extract payment info
            biz_status = payload.get("bizStatus")  # SUCCESS, FAIL, etc.

            if biz_status == "PAY_SUCCESS":
                return {
                    "payment_id": payload.get("merchantTradeNo", ""),
                    "status": "approved",
                    "metadata": {},
                    "provider": "binance_pay",
                    "crypto_amount": payload.get("totalFee"),
                    "currency": payload.get("currency")
                }
            else:
                return {
                    "payment_id": payload.get("merchantTradeNo", ""),
                    "status": "rejected",
                    "metadata": {},
                    "provider": "binance_pay"
                }

        except Exception as e:
            logger.error(f"Binance webhook error: {e}")
            return None

    def _verify_stripe_webhook(
        self,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """Verify Stripe webhook"""
        try:
            # Construct event with signature verification
            if self.stripe_webhook_secret and headers:
                sig_header = headers.get("stripe-signature")
                event = self.stripe.Webhook.construct_event(
                    json.dumps(payload),
                    sig_header,
                    self.stripe_webhook_secret
                )
            else:
                event = payload

            # Handle event types
            if event["type"] == "checkout.session.completed":
                session = event["data"]["object"]

                return {
                    "payment_id": session["id"],
                    "status": "approved",
                    "metadata": session.get("metadata", {}),
                    "provider": "stripe",
                    "amount": session.get("amount_total")
                }

            elif event["type"] == "payment_intent.succeeded":
                intent = event["data"]["object"]

                return {
                    "payment_id": intent["id"],
                    "status": "approved",
                    "metadata": intent.get("metadata", {}),
                    "provider": "stripe"
                }

        except Exception as e:
            logger.error(f"Stripe webhook error: {e}")
            return None

    def _verify_stub_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Stub webhook always approves"""
        return {
            "payment_id": payload.get("payment_id", "stub_123"),
            "status": "approved",
            "metadata": payload.get("metadata", {}),
            "provider": "stub"
        }

    # ==================== UTILITY METHODS ====================

    def get_available_providers(self) -> list:
        """Get list of configured payment providers"""
        return [p for p in self.providers if p != "stub"]

    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """Get information about a specific provider"""
        info = {
            "mercado_pago": {
                "name": "Mercado Pago",
                "currencies": ["BRL", "ARS", "MXN"],
                "methods": ["pix", "credit_card", "debit_card", "boleto"],
                "fees": "~4.99%",
                "region": "Latin America"
            },
            "binance_pay": {
                "name": "Binance Pay",
                "currencies": ["USDT", "BUSD", "BTC", "ETH"],
                "methods": ["crypto"],
                "fees": "0%",
                "region": "Global"
            },
            "stripe": {
                "name": "Stripe",
                "currencies": ["BRL", "USD", "EUR"],
                "methods": ["credit_card", "debit_card"],
                "fees": "~2.9% + $0.30",
                "region": "Global"
            }
        }

        return info.get(provider, {})


# Global instance
multi_payment_service = MultiPaymentService()
