"""
Payment service integration
Uses MultiPaymentService for real integrations (Mercado Pago, Stripe, Binance Pay)
Falls back to stub mode when no providers are configured
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from models import Payment, Subscription, Plan, Case

# Import the multi-provider service
try:
    from services.payments_multi import MultiPaymentService, multi_payment_service
    HAS_MULTI_PROVIDER = True
except ImportError:
    HAS_MULTI_PROVIDER = False
    multi_payment_service = None

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Payment service wrapper

    Uses MultiPaymentService for real payments when configured,
    falls back to stub mode for development/testing.
    """

    def __init__(self):
        self.use_real_payments = HAS_MULTI_PROVIDER and bool(
            os.getenv("MERCADO_PAGO_ACCESS_TOKEN") or
            os.getenv("STRIPE_SECRET_KEY") or
            os.getenv("BINANCE_PAY_API_KEY")
        )

        if self.use_real_payments:
            self.multi_service = multi_payment_service
            providers = self.multi_service.get_available_providers()
            logger.info(f"PaymentService using real providers: {providers}")
        else:
            self.multi_service = None
            logger.warning("PaymentService running in STUB mode (no payment providers configured)")

    def create_payment(
        self,
        db: Session,
        case_id: int,
        amount: float = 7.0,
        description: str = "Relatório Premium Doutora IA",
        payer_email: Optional[str] = None,
        provider: Optional[str] = None
    ) -> Payment:
        """
        Create a payment for a case report

        Args:
            db: Database session
            case_id: Case ID to associate payment with
            amount: Amount in BRL (default R$ 7.00)
            description: Payment description
            payer_email: Customer email
            provider: Specific provider (mercado_pago, stripe, binance_pay, auto)

        Returns:
            Payment object with payment URL
        """
        amount_cents = int(amount * 100)

        if self.use_real_payments and self.multi_service:
            # Use real payment provider
            try:
                result = self.multi_service.create_payment(
                    amount_cents=amount_cents,
                    description=description,
                    metadata={"case_id": case_id, "type": "report"},
                    payer_email=payer_email,
                    provider=provider
                )

                payment = Payment(
                    case_id=case_id,
                    amount=amount,
                    currency="BRL",
                    status="pending",
                    external_payment_id=result["payment_id"],
                    payment_url=result["payment_url"],
                    provider=result["provider"],
                    pix_qr_code=result.get("qr_code", ""),
                    pix_qr_code_base64=result.get("qr_code_base64", "")
                )

                db.add(payment)
                db.commit()
                db.refresh(payment)

                logger.info(f"Created {result['provider']} payment {payment.id} for case {case_id}")
                return payment

            except Exception as e:
                logger.error(f"Real payment failed, falling back to stub: {e}")
                # Fall through to stub mode

        # Stub mode
        payment = Payment(
            case_id=case_id,
            amount=amount,
            currency="BRL",
            status="pending",
            external_payment_id=f"stub_{case_id}_{int(datetime.utcnow().timestamp())}",
            payment_url=f"http://localhost:8080/payments/stub/{case_id}?auto_approve=true",
            provider="stub",
            pix_qr_code="00020126580014BR.GOV.BCB.PIX...",
            pix_qr_code_base64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        logger.info(f"Created STUB payment {payment.id} for case {case_id}")
        return payment

    def check_payment_status(self, db: Session, payment_id: int) -> str:
        """
        Check payment status

        For real providers, queries the provider API.
        For stub mode, auto-approves after 30 seconds.
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).first()

        if not payment:
            return "not_found"

        # Real payment - status is updated via webhook
        if payment.provider and payment.provider != "stub":
            return payment.status

        # Stub: auto-approve after 30 seconds (for testing)
        if payment.created_at and (datetime.utcnow() - payment.created_at).seconds > 30:
            payment.status = "approved"
            payment.approved_at = datetime.utcnow()

            # Also mark the case as paid
            if payment.case_id:
                case = db.query(Case).filter(Case.id == payment.case_id).first()
                if case:
                    case.report_paid = True
                    case.paid_at = datetime.utcnow()

            db.commit()
            return "approved"

        return payment.status

    def process_webhook(
        self,
        db: Session,
        payload: dict,
        headers: Optional[dict] = None,
        provider: Optional[str] = None
    ) -> Optional[dict]:
        """
        Process payment webhook from any provider

        Args:
            db: Database session
            payload: Webhook payload
            headers: HTTP headers (for signature verification)
            provider: Provider name (auto-detected if not specified)

        Returns:
            Processed webhook data or None if invalid
        """
        if not self.use_real_payments or not self.multi_service:
            # Stub webhook processing
            payment_id = payload.get("payment_id") or payload.get("data", {}).get("id")
            if payment_id:
                payment = db.query(Payment).filter(
                    Payment.external_payment_id == str(payment_id)
                ).first()
                if payment:
                    payment.status = "approved"
                    payment.approved_at = datetime.utcnow()

                    if payment.case_id:
                        case = db.query(Case).filter(Case.id == payment.case_id).first()
                        if case:
                            case.report_paid = True
                            case.paid_at = datetime.utcnow()

                    db.commit()
                    return {"status": "approved", "payment_id": payment_id}
            return None

        # Real webhook processing
        try:
            result = self.multi_service.verify_webhook(payload, headers, provider)

            if not result:
                logger.warning("Invalid webhook signature or payload")
                return None

            # Find and update payment
            payment = db.query(Payment).filter(
                Payment.external_payment_id == result["payment_id"]
            ).first()

            if payment:
                payment.status = result["status"]
                if result["status"] == "approved":
                    payment.approved_at = datetime.utcnow()

                    # Mark case as paid
                    if payment.case_id:
                        case = db.query(Case).filter(Case.id == payment.case_id).first()
                        if case:
                            case.report_paid = True
                            case.paid_at = datetime.utcnow()

                db.commit()
                logger.info(f"Webhook processed: payment {payment.id} -> {result['status']}")

            return result

        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return None

    def create_subscription(
        self,
        db: Session,
        lawyer_id: int,
        plan_id: int
    ) -> Subscription:
        """
        Create a subscription for a lawyer

        Note: Subscription billing is handled separately.
        This creates the subscription record and sets initial status.
        """
        # Get plan
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            raise ValueError("Plan not found")

        # Check if lawyer already has subscription
        existing = db.query(Subscription).filter(
            Subscription.lawyer_id == lawyer_id
        ).first()

        if existing:
            # Update subscription
            existing.plan_id = plan_id
            existing.status = "active"
            existing.expires_at = datetime.utcnow() + timedelta(days=30)
            db.commit()
            db.refresh(existing)
            logger.info(f"Updated subscription {existing.id} for lawyer {lawyer_id}")
            return existing

        # Create new subscription
        subscription = Subscription(
            lawyer_id=lawyer_id,
            plan_id=plan_id,
            status="active",
            expires_at=datetime.utcnow() + timedelta(days=30),
            external_subscription_id=f"sub_{lawyer_id}_{int(datetime.utcnow().timestamp())}"
        )

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        logger.info(f"Created subscription {subscription.id} for lawyer {lawyer_id}")
        return subscription

    def cancel_subscription(self, db: Session, subscription_id: int) -> bool:
        """Cancel a subscription"""
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()

        if not subscription:
            return False

        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.utcnow()
        db.commit()

        logger.info(f"Cancelled subscription {subscription_id}")
        return True

    def check_subscription_limits(
        self,
        db: Session,
        lawyer_id: int,
        action: str  # "search", "lead", "doc"
    ) -> bool:
        """
        Check if lawyer has reached subscription limits

        Returns True if action is allowed, False otherwise
        """
        subscription = db.query(Subscription).join(Plan).filter(
            Subscription.lawyer_id == lawyer_id,
            Subscription.status == "active"
        ).first()

        if not subscription:
            return False

        plan = subscription.plan

        # Check limits based on action
        if action == "search":
            if plan.searches_per_day == 0:
                return True  # Unlimited

            # Reset counter if new day
            if subscription.last_search_date and subscription.last_search_date.date() < datetime.utcnow().date():
                subscription.searches_today = 0

            if subscription.searches_today >= plan.searches_per_day:
                return False

            # Increment counter
            subscription.searches_today += 1
            subscription.last_search_date = datetime.utcnow()
            db.commit()
            return True

        elif action == "lead":
            if plan.leads_per_month == 0:
                return True  # Unlimited

            if subscription.leads_used >= plan.leads_per_month:
                return False

            subscription.leads_used += 1
            db.commit()
            return True

        elif action == "doc":
            if plan.docs_per_month == 0:
                return True  # Unlimited

            if subscription.docs_used >= plan.docs_per_month:
                return False

            subscription.docs_used += 1
            db.commit()
            return True

        return False

    def get_available_providers(self) -> list:
        """Get list of available payment providers"""
        if self.use_real_payments and self.multi_service:
            return self.multi_service.get_available_providers()
        return ["stub"]


# Global instance for convenience
payment_service = PaymentService()
