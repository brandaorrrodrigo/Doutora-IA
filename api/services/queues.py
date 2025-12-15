"""
Lead queue management for lawyer assignment
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta

from models import Lawyer, Subscription, Plan


class LeadQueue:
    """Manages lead distribution to lawyers using round-robin and ranking"""

    def get_next_lawyer(
        self,
        db: Session,
        area: str,
        city: Optional[str] = None,
        state: Optional[str] = None
    ) -> Optional[Lawyer]:
        """
        Get next lawyer for a lead using intelligent distribution

        Algorithm:
        1. Filter by active lawyers with valid subscription
        2. Filter by area match
        3. Filter by location match (if provided)
        4. Rank by:
           - Priority leads (Full plan subscribers)
           - Success score
           - Time since last lead (round-robin)
        5. Return top lawyer
        """

        # Base query: active lawyers with active subscriptions
        query = db.query(Lawyer).join(Subscription).join(Plan).filter(
            and_(
                Lawyer.is_active == True,
                Lawyer.is_verified == True,
                Subscription.status == "active",
                Subscription.expires_at > datetime.utcnow(),
                or_(
                    Plan.feature_leads == True,
                    Plan.feature_priority_leads == True
                )
            )
        )

        # Filter by area
        if area:
            query = query.filter(Lawyer.areas.contains([area]))

        # Filter by location
        if state:
            query = query.filter(Lawyer.states.contains([state]))

        if city:
            query = query.filter(Lawyer.cities.contains([city]))

        # Get all matching lawyers
        lawyers = query.all()

        if not lawyers:
            return None

        # Rank lawyers
        ranked_lawyers = []
        for lawyer in lawyers:
            score = 0.0

            # Priority leads (Full plan) get +50 points
            if lawyer.subscription and lawyer.subscription.plan.feature_priority_leads:
                score += 50.0

            # Success score (0-100) contributes directly
            score += lawyer.success_score or 0.0

            # Time since last lead (round-robin fairness)
            if lawyer.last_lead_at:
                hours_since = (datetime.utcnow() - lawyer.last_lead_at).total_seconds() / 3600
                # Add points for waiting longer (max 20 points for 24h+)
                score += min(20.0, hours_since / 24 * 20)
            else:
                # Never received a lead, give high priority
                score += 25.0

            # Acceptance rate bonus
            if lawyer.total_leads > 0:
                acceptance_rate = lawyer.accepted_leads / lawyer.total_leads
                score += acceptance_rate * 10.0

            ranked_lawyers.append((lawyer, score))

        # Sort by score (descending)
        ranked_lawyers.sort(key=lambda x: x[1], reverse=True)

        # Return top lawyer
        return ranked_lawyers[0][0] if ranked_lawyers else None

    def get_available_lawyers(
        self,
        db: Session,
        area: str,
        limit: int = 5
    ) -> list[Lawyer]:
        """Get list of available lawyers for an area"""
        query = db.query(Lawyer).join(Subscription).join(Plan).filter(
            and_(
                Lawyer.is_active == True,
                Lawyer.is_verified == True,
                Subscription.status == "active",
                Subscription.expires_at > datetime.utcnow(),
                or_(
                    Plan.feature_leads == True,
                    Plan.feature_priority_leads == True
                ),
                Lawyer.areas.contains([area])
            )
        ).limit(limit)

        return query.all()

    def update_lawyer_score(
        self,
        db: Session,
        lawyer_id: int,
        accepted: bool
    ):
        """Update lawyer's success score based on lead acceptance"""
        lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()

        if not lawyer:
            return

        # Update counts
        if accepted:
            lawyer.accepted_leads += 1
        else:
            lawyer.rejected_leads += 1

        # Recalculate success score (weighted average)
        # Formula: (accepted * 100 + rejected * 0) / total = acceptance_rate * 100
        total = lawyer.total_leads
        if total > 0:
            lawyer.success_score = (lawyer.accepted_leads / total) * 100

        db.commit()
