"""Seed database with initial data."""
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from db import SessionLocal
from models import User, Lawyer, Plan, Subscription, Case
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database():
    """Seed database with initial data."""
    db = SessionLocal()

    try:
        # Create plans
        logger.info("Creating plans...")

        plans_data = [
            {
                "code": "pesquisa",
                "name": "Plano Pesquisa",
                "price_cents": 4900,  # R$ 49,00
                "features": {
                    "search": True,
                    "search_limit": 100,
                    "downloads": False,
                    "leads": False,
                    "composition": False
                }
            },
            {
                "code": "leads",
                "name": "Plano Leads",
                "price_cents": 9900,  # R$ 99,00
                "features": {
                    "search": True,
                    "search_limit": 500,
                    "downloads": False,
                    "leads": True,
                    "leads_limit": 10,
                    "composition": False
                }
            },
            {
                "code": "redacao",
                "name": "Plano Redação",
                "price_cents": 14900,  # R$ 149,00
                "features": {
                    "search": True,
                    "search_limit": 1000,
                    "downloads": True,
                    "leads": False,
                    "composition": True,
                    "composition_limit": 20
                }
            },
            {
                "code": "pro",
                "name": "Plano Pro",
                "price_cents": 24900,  # R$ 249,00
                "features": {
                    "search": True,
                    "search_limit": -1,  # unlimited
                    "downloads": True,
                    "leads": True,
                    "leads_limit": 50,
                    "composition": True,
                    "composition_limit": 100,
                    "priority_support": True
                }
            },
            {
                "code": "full",
                "name": "Plano Full",
                "price_cents": 49900,  # R$ 499,00
                "features": {
                    "search": True,
                    "search_limit": -1,
                    "downloads": True,
                    "leads": True,
                    "leads_limit": -1,
                    "composition": True,
                    "composition_limit": -1,
                    "priority_support": True,
                    "api_access": True,
                    "white_label": True
                }
            }
        ]

        for plan_data in plans_data:
            existing = db.query(Plan).filter(Plan.code == plan_data["code"]).first()
            if not existing:
                plan = Plan(**plan_data)
                db.add(plan)
                logger.info(f"Created plan: {plan_data['name']}")

        db.commit()

        # Create demo lawyer
        logger.info("Creating demo lawyer...")
        existing_lawyer = db.query(Lawyer).filter(Lawyer.oab == "SP123456").first()
        if not existing_lawyer:
            lawyer = Lawyer(
                name="Dr. João Silva",
                oab="SP123456",
                email="joao.silva@example.com",
                areas=["familia", "consumidor", "bancario"],
                city="São Paulo",
                success_score=0.85,
                active=True
            )
            db.add(lawyer)
            db.commit()
            db.refresh(lawyer)
            logger.info("Created demo lawyer")

            # Subscribe lawyer to Pro plan
            pro_plan = db.query(Plan).filter(Plan.code == "pro").first()
            if pro_plan:
                subscription = Subscription(
                    lawyer_id=lawyer.id,
                    plan_id=pro_plan.id,
                    status="active",
                    started_at=datetime.now(),
                    ends_at=datetime.now() + timedelta(days=30)
                )
                db.add(subscription)
                db.commit()
                logger.info("Subscribed lawyer to Pro plan")

        # Create demo user
        logger.info("Creating demo user...")
        existing_user = db.query(User).filter(User.email == "demo@doutora-ia.com").first()
        if not existing_user:
            user = User(
                email="demo@doutora-ia.com",
                role="user"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info("Created demo user")

            # Create demo case
            case = Case(
                user_id=user.id,
                area="familia",
                descricao="Necessito ajustar o valor da pensão alimentícia que pago ao meu filho de 10 anos. Atualmente pago R$ 2.000,00 mensais, mas perdi meu emprego há 3 meses e só consigo trabalhos temporários com renda variável de R$ 3.000,00 a R$ 4.000,00. Tenho outro filho pequeno da segunda união. A mãe dele não aceita reduzir o valor.",
                score_prob="MÉDIA",
                cost_estimate="R$ 3.000 - R$ 5.000",
                status="analyzed"
            )
            db.add(case)
            db.commit()
            logger.info("Created demo case")

        logger.info("Database seeded successfully!")

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
