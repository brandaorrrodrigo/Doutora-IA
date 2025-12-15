"""
Endpoints de Autenticação JWT
Login, registro, refresh token, verificação de email, reset de senha
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from main import get_db
from services.jwt_auth import (
    jwt_service,
    get_current_lawyer,
    create_email_verification_token,
    verify_email_token,
    create_password_reset_token,
    verify_password_reset_token
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


# ==========================================
# SCHEMAS
# ==========================================

class RegisterRequest(BaseModel):
    """Dados para registro de novo advogado"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=3)
    oab: str = Field(..., min_length=5)
    phone: str
    cpf: Optional[str] = None
    areas: list[str] = Field(default_factory=list)
    cities: list[str] = Field(default_factory=list)
    states: list[str] = Field(default_factory=list)
    bio: Optional[str] = None


class LoginRequest(BaseModel):
    """Dados para login"""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Dados para refresh token"""
    refresh_token: str


class TokenResponse(BaseModel):
    """Resposta com tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LawyerResponse(BaseModel):
    """Dados públicos do advogado"""
    id: int
    email: str
    name: str
    oab: str
    phone: str
    areas: list[str]
    cities: list[str]
    states: list[str]
    bio: Optional[str]
    rating: Optional[float]
    total_ratings: int
    is_verified: bool
    created_at: datetime


class VerifyEmailRequest(BaseModel):
    """Token de verificação de email"""
    token: str


class ForgotPasswordRequest(BaseModel):
    """Solicitar reset de senha"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Resetar senha com token"""
    token: str
    new_password: str = Field(..., min_length=6)


class ChangePasswordRequest(BaseModel):
    """Alterar senha (já autenticado)"""
    old_password: str
    new_password: str = Field(..., min_length=6)


# ==========================================
# ENDPOINTS DE AUTENTICAÇÃO
# ==========================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Registrar novo advogado

    - Cria conta
    - Retorna tokens de acesso
    - Envia email de verificação (em background)
    """
    try:
        # Registrar advogado
        lawyer = jwt_service.register_lawyer(
            db=db,
            email=request.email,
            password=request.password,
            name=request.name,
            oab=request.oab,
            phone=request.phone,
            cpf=request.cpf,
            areas=request.areas,
            cities=request.cities,
            states=request.states,
            bio=request.bio
        )

        # Criar tokens
        tokens = jwt_service.create_token_pair(lawyer.id, lawyer.email)

        # Enviar email de verificação (em background)
        verification_token = create_email_verification_token(lawyer.id)
        background_tasks.add_task(
            send_verification_email,
            lawyer.email,
            lawyer.name,
            verification_token
        )

        return tokens

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar advogado: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Fazer login

    - Valida email e senha
    - Retorna tokens de acesso
    """
    # Autenticar
    lawyer = jwt_service.authenticate_lawyer(db, request.email, request.password)

    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Criar tokens
    tokens = jwt_service.create_token_pair(lawyer.id, lawyer.email)

    # Atualizar último login
    lawyer.last_login_at = datetime.utcnow()
    db.commit()

    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Renovar access token usando refresh token

    - Valida refresh token
    - Retorna novo par de tokens
    """
    try:
        # Verificar refresh token
        payload = jwt_service.verify_refresh_token(request.refresh_token)

        lawyer_id = int(payload.get("sub"))
        email = payload.get("email")

        # Verificar se advogado ainda existe e está ativo
        from models import Lawyer
        lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()

        if not lawyer or not lawyer.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

        # Criar novos tokens
        tokens = jwt_service.create_token_pair(lawyer.id, lawyer.email)

        return tokens

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )


@router.get("/me", response_model=LawyerResponse)
async def get_current_user(lawyer = Depends(get_current_lawyer)):
    """
    Obter dados do advogado autenticado

    Requer: Bearer token no header Authorization
    """
    return LawyerResponse(
        id=lawyer.id,
        email=lawyer.email,
        name=lawyer.name,
        oab=lawyer.oab,
        phone=lawyer.phone,
        areas=lawyer.areas or [],
        cities=lawyer.cities or [],
        states=lawyer.states or [],
        bio=lawyer.bio,
        rating=float(lawyer.rating) if lawyer.rating else None,
        total_ratings=lawyer.total_ratings or 0,
        is_verified=lawyer.is_verified,
        created_at=lawyer.created_at
    )


@router.post("/logout")
async def logout(lawyer = Depends(get_current_lawyer)):
    """
    Fazer logout

    Nota: Com JWT stateless, o logout é feito no client
    (remover token do localStorage). Este endpoint é apenas informativo.
    """
    return {
        "message": "Logout realizado com sucesso",
        "action": "Remova o token do client-side storage"
    }


# ==========================================
# VERIFICAÇÃO DE EMAIL
# ==========================================

@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Verificar email com token enviado por email

    - Valida token
    - Marca email como verificado
    """
    lawyer_id = verify_email_token(request.token)

    if not lawyer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado"
        )

    from models import Lawyer
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()

    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Advogado não encontrado"
        )

    if lawyer.is_verified:
        return {"message": "Email já verificado"}

    # Marcar como verificado
    lawyer.is_verified = True
    lawyer.verified_at = datetime.utcnow()
    db.commit()

    return {
        "message": "Email verificado com sucesso!",
        "verified_at": lawyer.verified_at.isoformat()
    }


@router.post("/resend-verification")
async def resend_verification(
    background_tasks: BackgroundTasks,
    lawyer = Depends(get_current_lawyer)
):
    """
    Reenviar email de verificação

    Requer: Bearer token
    """
    if lawyer.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já verificado"
        )

    # Criar novo token
    verification_token = create_email_verification_token(lawyer.id)

    # Enviar email
    background_tasks.add_task(
        send_verification_email,
        lawyer.email,
        lawyer.name,
        verification_token
    )

    return {
        "message": "Email de verificação reenviado",
        "email": lawyer.email
    }


# ==========================================
# RESET DE SENHA
# ==========================================

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Solicitar reset de senha

    - Envia email com token de reset
    - Não revela se email existe ou não (segurança)
    """
    from models import Lawyer

    lawyer = db.query(Lawyer).filter(Lawyer.email == request.email).first()

    # Sempre retornar sucesso (não revelar se email existe)
    if lawyer:
        # Criar token de reset
        reset_token = create_password_reset_token(lawyer.id)

        # Enviar email
        background_tasks.add_task(
            send_password_reset_email,
            lawyer.email,
            lawyer.name,
            reset_token
        )

    return {
        "message": "Se o email existir, você receberá instruções para resetar sua senha"
    }


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Resetar senha com token

    - Valida token de reset
    - Altera senha
    """
    lawyer_id = verify_password_reset_token(request.token)

    if not lawyer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado"
        )

    from models import Lawyer
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()

    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Advogado não encontrado"
        )

    # Alterar senha
    lawyer.hashed_password = jwt_service.hash_password(request.new_password)
    db.commit()

    return {
        "message": "Senha alterada com sucesso"
    }


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    lawyer = Depends(get_current_lawyer)
):
    """
    Alterar senha (já autenticado)

    - Verifica senha antiga
    - Define nova senha

    Requer: Bearer token
    """
    # Verificar senha antiga
    if not jwt_service.verify_password(request.old_password, lawyer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )

    # Alterar senha
    lawyer.hashed_password = jwt_service.hash_password(request.new_password)
    db.commit()

    return {
        "message": "Senha alterada com sucesso"
    }


# ==========================================
# FUNÇÕES AUXILIARES (Email)
# ==========================================

async def send_verification_email(email: str, name: str, token: str):
    """Envia email de verificação via SMTP"""
    from services.email_service import email_service
    email_service.send_verification_email(email, name, token)


async def send_password_reset_email(email: str, name: str, token: str):
    """Envia email de reset de senha via SMTP"""
    from services.email_service import email_service
    email_service.send_password_reset_email(email, name, token)
