"""
Payment service integration (Mercado Pago stub)
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from models import Payment, Subscription, Plan, Lawyer


class PaymentService:
    """Payment service for Mercado Pago integration"""

    def __init__(self):
        self.access_token = os.getenv("MERCADO_PAGO_ACCESS_TOKEN", "")
        self.base_url = "https://api.mercadopago.com"

    def create_payment(
        self,
        db: Session,
        case_id: int,
        amount: float = 7.0,
        description: str = "Relatório Premium Doutora IA"
    ) -> Payment:
        """
        Create a payment for a case report

        In production, this would:
        1. Create payment in Mercado Pago
        2. Get PIX QR code
        3. Store payment details
        4. Return payment link

        For MVP, this is a stub
        """
        payment = Payment(
            case_id=case_id,
            amount=amount,
            currency="BRL",
            status="pending",
            external_payment_id=f"stub_{case_id}_{int(datetime.utcnow().timestamp())}",
            pix_qr_code="00020126580014BR.GOV.BCB.PIX...",  # Stub QR code
            pix_qr_code_base64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment

    def check_payment_status(self, db: Session, payment_id: int) -> str:
        """
        Check payment status with Mercado Pago

        For MVP stub: returns "approved" after 30 seconds (for testing)
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).first()

        if not payment:
            return "not_found"

        # Stub: auto-approve after 30 seconds
        if payment.created_at and (datetime.utcnow() - payment.created_at).seconds > 30:
            payment.status = "approved"
            payment.approved_at = datetime.utcnow()
            db.commit()
            return "approved"

        return payment.status

    def create_subscription(
        self,
        db: Session,
        lawyer_id: int,
        plan_id: int
    ) -> Subscription:
        """
        Create a subscription for a lawyer

        In production, this would:
        1. Create subscription in Mercado Pago
        2. Set up recurring billing
        3. Handle first payment

        For MVP, this is a stub
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
            return existing

        # Create new subscription
        subscription = Subscription(
            lawyer_id=lawyer_id,
            plan_id=plan_id,
            status="active",
            expires_at=datetime.utcnow() + timedelta(days=30),
            external_subscription_id=f"stub_sub_{lawyer_id}_{int(datetime.utcnow().timestamp())}"
        )

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

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
