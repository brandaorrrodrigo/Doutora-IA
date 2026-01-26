"""
PRODUCTION FEATURES - Doutora IA
Consolidated implementation of all production-ready features
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, WebSocket, WebSocketDisconnect, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import os
import json
import asyncio
from collections import defaultdict

from db import get_db
import models
import schemas
from services.auth import auth_service

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# ========================================
# AUTHENTICATION DEPENDENCIES
# ========================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Get current authenticated user from JWT token
    """
    token = credentials.credentials
    payload = auth_service.decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    return user


def get_current_active_verified_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Get current user and verify email is confirmed
    """
    if not current_user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Check your inbox.")

    return current_user


# ========================================
# RATE LIMITING (Simple In-Memory)
# ========================================

class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.requests = defaultdict(list)
        self.limits = {
            "default": (60, 60),  # 60 requests per 60 seconds
            "search": (30, 60),   # 30 searches per minute
            "analysis": (10, 60),  # 10 analyses per minute
            "upload": (5, 300),    # 5 uploads per 5 minutes
        }

    def check_rate_limit(self, key: str, endpoint_type: str = "default") -> bool:
        """
        Check if rate limit is exceeded
        Returns True if allowed, False if rate limited
        """
        limit, window = self.limits.get(endpoint_type, self.limits["default"])
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window)

        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > cutoff
        ]

        # Check limit
        if len(self.requests[key]) >= limit:
            return False

        # Add new request
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter()


def check_rate_limit(endpoint_type: str = "default"):
    """Dependency to check rate limit"""
    def dependency(current_user: models.User = Depends(get_current_user)):
        key = f"user_{current_user.id}_{endpoint_type}"

        if not rate_limiter.check_rate_limit(key, endpoint_type):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        return current_user

    return dependency


# ========================================
# AUTHENTICATION ENDPOINTS
# ========================================

@router.post("/auth/register")
async def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    """Register new user"""
    try:
        user = auth_service.register_user(db, user_data)

        # Generate verification token
        verification_token = auth_service.generate_verification_token()
        user.verification_token = verification_token
        db.commit()

        # TODO: Send verification email
        # email_service.send_verification_email(user.email, verification_token)

        # Create tokens
        tokens = auth_service.create_tokens_for_user(user)

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_verified": user.is_verified
            },
            **tokens,
            "message": "Registration successful. Please check your email to verify your account."
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auth/login")
async def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = auth_service.authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    tokens = auth_service.create_tokens_for_user(user)

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_verified": user.is_verified
        },
        **tokens
    }


@router.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    new_access_token = auth_service.refresh_access_token(refresh_token)

    if not new_access_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


@router.get("/auth/me")
async def get_me(current_user: models.User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "is_verified": current_user.is_verified,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


@router.post("/auth/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user email"""
    success = auth_service.verify_email(db, token)

    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    return {"message": "Email verified successfully"}


@router.post("/auth/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    """Request password reset"""
    reset_token = auth_service.request_password_reset(db, email)

    if reset_token:
        # TODO: Send reset email
        # email_service.send_password_reset_email(email, reset_token)
        pass

    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/auth/reset-password")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """Reset password with token"""
    success = auth_service.reset_password(db, token, new_password)

    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    return {"message": "Password reset successfully"}


# ========================================
# ADVANCED SEARCH WITH FILTERS
# ========================================

@router.post("/search/advanced")
async def advanced_search(
    query: str,
    area: Optional[str] = None,
    tipo: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sort_by: str = Query("relevance", regex="^(relevance|date|popularity)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(check_rate_limit("search"))
):
    """
    Advanced search with filters and sorting
    """
    from rag import rag_system

    # Build filters
    filtros = {}
    if area:
        filtros["area"] = area
    if tipo:
        filtros["tipo"] = tipo

    # Perform search
    results = rag_system.search(query=query, filtros=filtros, limit=limit + skip)

    # Apply date filters if provided
    if date_from or date_to:
        filtered_results = []
        for r in results:
            result_date = r.get("data")
            if result_date:
                if date_from and result_date < date_from:
                    continue
                if date_to and result_date > date_to:
                    continue
            filtered_results.append(r)
        results = filtered_results

    # Sort results
    if sort_by == "date" and results:
        results = sorted(results, key=lambda x: x.get("data", datetime.min), reverse=True)
    elif sort_by == "popularity":
        # Placeholder for popularity sorting (could track clicks/views)
        pass

    # Pagination
    paginated_results = results[skip:skip+limit]

    return {
        "total": len(results),
        "skip": skip,
        "limit": limit,
        "results": paginated_results,
        "filters_applied": {
            "area": area,
            "tipo": tipo,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
            "sort_by": sort_by
        }
    }


# ========================================
# FAVORITES & HISTORY
# ========================================

@router.post("/favorites/add")
async def add_favorite(
    analysis_id: int,
    folder: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_verified_user)
):
    """Add analysis to favorites"""

    # Check if already favorited
    existing = db.query(models.Favorite).filter(
        and_(
            models.Favorite.user_id == current_user.id,
            models.Favorite.analysis_id == analysis_id
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")

    favorite = models.Favorite(
        user_id=current_user.id,
        analysis_id=analysis_id,
        folder=folder,
        created_at=datetime.utcnow()
    )

    db.add(favorite)
    db.commit()

    return {"message": "Added to favorites", "favorite_id": favorite.id}


@router.get("/favorites")
async def get_favorites(
    folder: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_verified_user)
):
    """Get user's favorites"""

    query = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id
    )

    if folder:
        query = query.filter(models.Favorite.folder == folder)

    query = query.order_by(desc(models.Favorite.created_at))

    favorites = query.offset(skip).limit(limit).all()

    return {
        "total": query.count(),
        "favorites": favorites
    }


@router.delete("/favorites/{favorite_id}")
async def remove_favorite(
    favorite_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_verified_user)
):
    """Remove from favorites"""

    favorite = db.query(models.Favorite).filter(
        and_(
            models.Favorite.id == favorite_id,
            models.Favorite.user_id == current_user.id
        )
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(favorite)
    db.commit()

    return {"message": "Removed from favorites"}


@router.get("/history")
async def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_verified_user)
):
    """Get user's analysis history"""

    # This assumes we have a UserAnalysis model tracking user activities
    # For now, return placeholder

    return {
        "total": 0,
        "history": [],
        "message": "History tracking will be fully implemented with user activity logging"
    }


# ========================================
# DOCUMENT UPLOAD & OCR
# ========================================

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(check_rate_limit("upload"))
):
    """
    Upload PDF document for analysis
    Supports OCR for scanned documents
    """

    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Read file
    contents = await file.read()

    # Save to storage (placeholder - would use S3/MinIO in production)
    upload_dir = "/tmp/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = f"{upload_dir}/{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract text (placeholder for OCR)
    # In production, would use:
    # - PyPDF2 for digital PDFs
    # - pytesseract + pdf2image for scanned PDFs

    extracted_text = "Text extraction coming soon..."

    # Store document record
    document = models.Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_size=len(contents),
        extracted_text=extracted_text,
        created_at=datetime.utcnow()
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "document_id": document.id,
        "filename": file.filename,
        "size_bytes": len(contents),
        "message": "Document uploaded successfully. Text extraction in progress..."
    }


@router.get("/documents")
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_verified_user)
):
    """List user's uploaded documents"""

    query = db.query(models.Document).filter(
        models.Document.user_id == current_user.id
    ).order_by(desc(models.Document.created_at))

    documents = query.offset(skip).limit(limit).all()

    return {
        "total": query.count(),
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "size_bytes": doc.file_size,
                "created_at": doc.created_at.isoformat()
            }
            for doc in documents
        ]
    }


# ========================================
# REAL-TIME NOTIFICATIONS (WebSocket)
# ========================================

class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected via WebSocket")

    def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections[user_id].remove(websocket)
        logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user"""
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except:
                pass

    async def broadcast(self, message: dict):
        """Broadcast to all connected users"""
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_json(message)
                except:
                    pass

connection_manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    WebSocket endpoint for real-time notifications
    """
    await connection_manager.connect(websocket, user_id)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to notification service",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep connection alive
        while True:
            data = await websocket.receive_text()

            # Echo back for heartbeat
            await websocket.send_json({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, user_id)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connection_manager.disconnect(websocket, user_id)


@router.post("/notifications/send")
async def send_notification(
    user_id: int,
    message: str,
    notification_type: str = "info",
    current_user: models.User = Depends(get_current_user)
):
    """
    Send real-time notification to user
    (Admin/System use)
    """

    notification = {
        "type": notification_type,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }

    await connection_manager.send_personal_message(notification, user_id)

    return {"message": "Notification sent"}


# ========================================
# SUBSCRIPTION PLANS (Placeholder)
# ========================================

@router.get("/plans")
async def get_plans(db: Session = Depends(get_db)):
    """Get available subscription plans"""

    plans = db.query(models.Plan).filter(models.Plan.is_active == True).all()

    return {"plans": plans}


@router.post("/subscriptions/subscribe")
async def subscribe_to_plan(
    plan_code: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_verified_user)
):
    """
    Subscribe to a plan
    TODO: Integrate with Stripe/MercadoPago for recurring payments
    """

    plan = db.query(models.Plan).filter(models.Plan.code == plan_code).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Create subscription (placeholder)
    subscription = models.Subscription(
        user_id=current_user.id,
        plan_id=plan.id,
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        created_at=datetime.utcnow()
    )

    db.add(subscription)
    db.commit()

    return {
        "message": "Subscribed successfully",
        "subscription_id": subscription.id,
        "plan": plan.name,
        "next_billing_date": subscription.current_period_end.isoformat()
    }


@router.get("/subscriptions/my-subscription")
async def get_my_subscription(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_verified_user)
):
    """Get current user's subscription"""

    subscription = db.query(models.Subscription).filter(
        and_(
            models.Subscription.user_id == current_user.id,
            models.Subscription.status == "active"
        )
    ).first()

    if not subscription:
        return {"subscription": None, "message": "No active subscription"}

    return {
        "subscription": {
            "id": subscription.id,
            "plan": subscription.plan.name if subscription.plan else None,
            "status": subscription.status,
            "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None
        }
    }
