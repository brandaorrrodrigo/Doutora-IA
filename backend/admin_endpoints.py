"""
Admin Dashboard Endpoints for Doutora IA
Real-time analytics, user management, system metrics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
import os

from db import get_db
import models
import schemas
from services.cache import get_cache_metrics, cache_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


# ========================================
# AUTHENTICATION / AUTHORIZATION
# ========================================

def verify_admin(admin_token: str = Query(...)):
    """
    Simple admin authentication
    TODO: Replace with proper JWT-based admin auth
    """
    expected_token = os.getenv("ADMIN_SECRET_TOKEN", "admin_dev_token_change_in_prod")

    if admin_token != expected_token:
        raise HTTPException(status_code=403, detail="Admin access denied")

    return True


# ========================================
# ANALYTICS ENDPOINTS
# ========================================

@router.get("/analytics/overview")
async def get_analytics_overview(
    db: Session = Depends(get_db),
    admin: bool = Depends(verify_admin)
):
    """
    Real-time overview of platform metrics
    Returns: Users, lawyers, cases, revenue, activity
    """

    # Time ranges
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    # User metrics
    total_users = db.query(func.count(models.User.id)).scalar() or 0
    users_today = db.query(func.count(models.User.id)).filter(
        models.User.created_at >= today_start
    ).scalar() or 0
    users_week = db.query(func.count(models.User.id)).filter(
        models.User.created_at >= week_start
    ).scalar() or 0

    # Lawyer metrics
    total_lawyers = db.query(func.count(models.Lawyer.id)).scalar() or 0
    lawyers_active = db.query(func.count(models.Lawyer.id)).filter(
        models.Lawyer.status == "active"
    ).scalar() or 0

    # Case/Analysis metrics
    total_cases = db.query(func.count(models.Case.id)).scalar() or 0
    cases_today = db.query(func.count(models.Case.id)).filter(
        models.Case.created_at >= today_start
    ).scalar() or 0
    cases_open = db.query(func.count(models.Case.id)).filter(
        models.Case.status == "open"
    ).scalar() or 0

    # Revenue metrics (in cents)
    total_revenue = db.query(func.sum(models.Payment.amount)).filter(
        models.Payment.status == "approved"
    ).scalar() or 0

    revenue_today = db.query(func.sum(models.Payment.amount)).filter(
        and_(
            models.Payment.status == "approved",
            models.Payment.created_at >= today_start
        )
    ).scalar() or 0

    revenue_month = db.query(func.sum(models.Payment.amount)).filter(
        and_(
            models.Payment.status == "approved",
            models.Payment.created_at >= month_start
        )
    ).scalar() or 0

    # Lead metrics
    total_leads = db.query(func.count(models.Lead.id)).scalar() or 0
    leads_pending = db.query(func.count(models.Lead.id)).filter(
        models.Lead.status == "pending"
    ).scalar() or 0
    leads_converted = db.query(func.count(models.Lead.id)).filter(
        models.Lead.status == "converted"
    ).scalar() or 0

    conversion_rate = (leads_converted / total_leads * 100) if total_leads > 0 else 0

    # Report metrics
    total_reports = db.query(func.count(models.Report.id)).scalar() or 0
    reports_paid = db.query(func.count(models.Report.id)).filter(
        models.Report.paid == True
    ).scalar() or 0

    return {
        "users": {
            "total": total_users,
            "today": users_today,
            "week": users_week,
            "growth_rate": round((users_week / max(total_users - users_week, 1)) * 100, 2)
        },
        "lawyers": {
            "total": total_lawyers,
            "active": lawyers_active,
            "inactive": total_lawyers - lawyers_active,
            "activation_rate": round((lawyers_active / max(total_lawyers, 1)) * 100, 2)
        },
        "cases": {
            "total": total_cases,
            "today": cases_today,
            "open": cases_open,
            "closed": total_cases - cases_open
        },
        "revenue": {
            "total": total_revenue / 100,  # Convert to reais
            "today": revenue_today / 100,
            "month": revenue_month / 100,
            "average_order_value": round((total_revenue / max(reports_paid, 1)) / 100, 2)
        },
        "leads": {
            "total": total_leads,
            "pending": leads_pending,
            "converted": leads_converted,
            "conversion_rate": round(conversion_rate, 2)
        },
        "reports": {
            "total": total_reports,
            "paid": reports_paid,
            "free": total_reports - reports_paid,
            "payment_rate": round((reports_paid / max(total_reports, 1)) * 100, 2)
        },
        "timestamp": now.isoformat()
    }


@router.get("/analytics/activity")
async def get_activity_timeline(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    admin: bool = Depends(verify_admin)
):
    """
    Daily activity timeline for charts
    Returns: Array of {date, users, cases, revenue}
    """

    activity_data = []
    now = datetime.utcnow()

    for i in range(days):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        # Count metrics for this day
        users = db.query(func.count(models.User.id)).filter(
            and_(
                models.User.created_at >= day_start,
                models.User.created_at < day_end
            )
        ).scalar() or 0

        cases = db.query(func.count(models.Case.id)).filter(
            and_(
                models.Case.created_at >= day_start,
                models.Case.created_at < day_end
            )
        ).scalar() or 0

        revenue = db.query(func.sum(models.Payment.amount)).filter(
            and_(
                models.Payment.status == "approved",
                models.Payment.created_at >= day_start,
                models.Payment.created_at < day_end
            )
        ).scalar() or 0

        activity_data.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "users": users,
            "cases": cases,
            "revenue": revenue / 100  # Convert to reais
        })

    # Reverse to show oldest first
    activity_data.reverse()

    return {
        "days": days,
        "data": activity_data
    }


@router.get("/analytics/system")
async def get_system_metrics(
    admin: bool = Depends(verify_admin)
):
    """
    System health and performance metrics
    Returns: Cache stats, email stats, API performance
    """

    # Cache metrics
    cache_metrics = get_cache_metrics()

    # Email metrics (placeholder - would need email service metrics)
    email_metrics = {
        "provider": os.getenv("EMAIL_PROVIDER", "console"),
        "enabled": os.getenv("EMAIL_PROVIDER", "console") != "console",
        # TODO: Integrate with Resend API for real stats
        "sent_today": 0,
        "delivery_rate": 0,
        "open_rate": 0
    }

    # API metrics (placeholder - would need API monitoring)
    api_metrics = {
        "uptime_percentage": 99.9,
        "avg_response_time_ms": 250,
        "requests_today": 0,
        "errors_today": 0
    }

    # Database stats
    db_metrics = {
        "connection_pool": "healthy",
        "query_performance": "normal"
    }

    return {
        "cache": cache_metrics,
        "email": email_metrics,
        "api": api_metrics,
        "database": db_metrics,
        "timestamp": datetime.utcnow().isoformat()
    }


# ========================================
# USER MANAGEMENT ENDPOINTS
# ========================================

@router.get("/users", response_model=List[schemas.UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: bool = Depends(verify_admin)
):
    """
    List all users with filtering and pagination
    """

    query = db.query(models.User)

    # Filter by status
    if status:
        query = query.filter(models.User.status == status)

    # Search by name or email
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.User.name.ilike(search_pattern),
                models.User.email.ilike(search_pattern)
            )
        )

    # Order by most recent first
    query = query.order_by(models.User.created_at.desc())

    # Pagination
    users = query.offset(skip).limit(limit).all()

    return users


@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    admin: bool = Depends(verify_admin)
):
    """
    Get detailed information about a specific user
    """

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    status: str = Query(..., regex="^(active|suspended|banned)$"),
    db: Session = Depends(get_db),
    admin: bool = Depends(verify_admin)
):
    """
    Update user status (active, suspended, banned)
    """

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = status
    db.commit()

    logger.info(f"Admin updated user {user_id} status to {status}")

    return {
        "user_id": user_id,
        "status": status,
        "updated_at": datetime.utcnow().isoformat()
    }


# ========================================
# LAWYER MANAGEMENT ENDPOINTS
# ========================================

@router.get("/lawyers", response_model=List[schemas.LawyerResponse])
async def list_lawyers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: bool = Depends(verify_admin)
):
    """
    List all lawyers with filtering
    """

    query = db.query(models.Lawyer)

    # Filter by status
    if status:
        query = query.filter(models.Lawyer.status == status)

    # Filter by area
    if area:
        query = query.filter(models.Lawyer.areas.contains([area]))

    # Order by most recent first
    query = query.order_by(models.Lawyer.created_at.desc())

    lawyers = query.offset(skip).limit(limit).all()

    return lawyers


@router.patch("/lawyers/{lawyer_id}/approve")
async def approve_lawyer(
    lawyer_id: int,
    db: Session = Depends(get_db),
    admin: bool = Depends(verify_admin)
):
    """
    Approve lawyer registration (after OAB verification)
    """

    lawyer = db.query(models.Lawyer).filter(models.Lawyer.id == lawyer_id).first()

    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    lawyer.status = "active"
    lawyer.verified_at = datetime.utcnow()
    db.commit()

    logger.info(f"Admin approved lawyer {lawyer_id}")

    return {
        "lawyer_id": lawyer_id,
        "status": "active",
        "approved_at": lawyer.verified_at.isoformat()
    }


# ========================================
# PAYMENT / REVENUE MANAGEMENT
# ========================================

@router.get("/payments")
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: bool = Depends(verify_admin)
):
    """
    List all payments with filtering
    """

    query = db.query(models.Payment)

    if status:
        query = query.filter(models.Payment.status == status)

    query = query.order_by(models.Payment.created_at.desc())

    payments = query.offset(skip).limit(limit).all()

    return {
        "total": query.count(),
        "payments": [
            {
                "id": p.id,
                "amount": p.amount / 100,  # Convert to reais
                "status": p.status,
                "provider": p.provider,
                "external_id": p.external_id,
                "metadata": p.metadata,
                "created_at": p.created_at.isoformat()
            }
            for p in payments
        ]
    }


@router.get("/revenue/mrr")
async def get_monthly_recurring_revenue(
    db: Session = Depends(get_db),
    admin: bool = Depends(verify_admin)
):
    """
    Calculate MRR (Monthly Recurring Revenue)
    """

    # Get subscriptions (if implemented)
    # For now, calculate based on avg monthly revenue from last 3 months

    now = datetime.utcnow()
    three_months_ago = now - timedelta(days=90)

    total_revenue = db.query(func.sum(models.Payment.amount)).filter(
        and_(
            models.Payment.status == "approved",
            models.Payment.created_at >= three_months_ago
        )
    ).scalar() or 0

    # Average per month
    mrr = (total_revenue / 3) / 100  # Convert to reais

    # Revenue by month
    revenue_by_month = []
    for i in range(6):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

        monthly_revenue = db.query(func.sum(models.Payment.amount)).filter(
            and_(
                models.Payment.status == "approved",
                models.Payment.created_at >= month_start,
                models.Payment.created_at <= month_end
            )
        ).scalar() or 0

        revenue_by_month.append({
            "month": month_start.strftime("%Y-%m"),
            "revenue": monthly_revenue / 100
        })

    revenue_by_month.reverse()

    return {
        "mrr": round(mrr, 2),
        "by_month": revenue_by_month
    }


# ========================================
# LOGS / DEBUGGING
# ========================================

@router.get("/logs")
async def get_recent_logs(
    level: str = Query("INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"),
    limit: int = Query(100, ge=1, le=1000),
    admin: bool = Depends(verify_admin)
):
    """
    Get recent application logs
    TODO: Implement proper log storage/retrieval
    """

    # Placeholder - would need proper logging infrastructure
    # Options: File tailing, ELK stack, CloudWatch, etc.

    return {
        "message": "Log retrieval not yet implemented",
        "suggestion": "Use 'docker-compose logs api' for now",
        "todo": [
            "Implement structured logging with JSON",
            "Store logs in database or external service",
            "Add log search and filtering"
        ]
    }


# ========================================
# CACHE MANAGEMENT
# ========================================

@router.post("/cache/clear")
async def admin_clear_cache(
    pattern: str = Query("*"),
    admin: bool = Depends(verify_admin)
):
    """
    Clear cache (all or by pattern)
    """

    if pattern == "*":
        success = cache_service.clear_all()
        return {
            "status": "cleared_all" if success else "failed",
            "pattern": pattern
        }
    else:
        deleted = cache_service.delete_pattern(f"doutora_ia:{pattern}:*")
        return {
            "status": "cleared",
            "pattern": pattern,
            "keys_deleted": deleted
        }


@router.get("/cache/stats")
async def admin_cache_stats(
    admin: bool = Depends(verify_admin)
):
    """
    Get detailed cache statistics
    """

    return get_cache_metrics()
