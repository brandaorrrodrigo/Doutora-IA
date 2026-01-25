"""
Serviço de Autenticação JWT para Advogados
Implementa login, registro, refresh token e proteção de rotas
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Header
from sqlalchemy.orm import Session
import os
import secrets

from database import get_db

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hora
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 dias

# Contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTAuthService:
    """Serviço de autenticação JWT"""

    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expire = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    # ==========================================
    # HASH DE SENHAS
    # ==========================================

    def hash_password(self, password: str) -> str:
        """Cria hash seguro da senha"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica se senha está correta"""
        return pwd_context.verify(plain_password, hashed_password)

    # ==========================================
    # GERAÇÃO DE TOKENS
    # ==========================================

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Cria token de acesso (curta duração)

        Args:
            data: Dados a serem incluídos no token (ex: {"sub": "lawyer_id"})

        Returns:
            Token JWT assinado
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + self.access_token_expire

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Cria refresh token (longa duração)

        Args:
            data: Dados a serem incluídos no token

        Returns:
            Refresh token JWT assinado
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + self.refresh_token_expire

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)  # Unique token ID
        })

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_token_pair(self, lawyer_id: int, email: str) -> Dict[str, str]:
        """
        Cria par de tokens (access + refresh)

        Args:
            lawyer_id: ID do advogado
            email: Email do advogado

        Returns:
            {"access_token": "...", "refresh_token": "...", "token_type": "bearer"}
        """
        access_token = self.create_access_token(
            data={"sub": str(lawyer_id), "email": email}
        )

        refresh_token = self.create_refresh_token(
            data={"sub": str(lawyer_id), "email": email}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # segundos
        }

    # ==========================================
    # VALIDAÇÃO DE TOKENS
    # ==========================================

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decodifica e valida token JWT

        Args:
            token: Token JWT

        Returns:
            Payload do token

        Raises:
            HTTPException: Se token for inválido ou expirado
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """
        Verifica se é um access token válido

        Args:
            token: Token JWT

        Returns:
            Payload do token

        Raises:
            HTTPException: Se token não for access token válido
        """
        payload = self.decode_token(token)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token inválido"
            )

        return payload

    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Verifica se é um refresh token válido

        Args:
            token: Token JWT

        Returns:
            Payload do token

        Raises:
            HTTPException: Se token não for refresh token válido
        """
        payload = self.decode_token(token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token inválido"
            )

        return payload

    # ==========================================
    # AUTENTICAÇÃO
    # ==========================================

    def authenticate_lawyer(self, db: Session, email: str, password: str):
        """
        Autentica advogado por email e senha

        Args:
            db: Sessão do banco
            email: Email do advogado
            password: Senha em texto plano

        Returns:
            Objeto Lawyer se autenticado, None caso contrário
        """
        from models import Lawyer

        lawyer = db.query(Lawyer).filter(Lawyer.email == email).first()

        if not lawyer:
            return None

        if not lawyer.is_active:
            return None

        if not self.verify_password(password, lawyer.hashed_password):
            return None

        return lawyer

    def register_lawyer(
        self,
        db: Session,
        email: str,
        password: str,
        name: str,
        oab: str,
        phone: str,
        **kwargs
    ):
        """
        Registra novo advogado

        Args:
            db: Sessão do banco
            email: Email
            password: Senha em texto plano
            name: Nome completo
            oab: Número OAB
            phone: Telefone
            **kwargs: Outros campos opcionais

        Returns:
            Objeto Lawyer criado

        Raises:
            HTTPException: Se email ou OAB já existir
        """
        from models import Lawyer

        # Verificar se já existe
        existing = db.query(Lawyer).filter(
            (Lawyer.email == email) | (Lawyer.oab == oab)
        ).first()

        if existing:
            if existing.email == email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OAB já cadastrada"
                )

        # Criar advogado
        lawyer = Lawyer(
            email=email,
            name=name,
            oab=oab,
            phone=phone,
            hashed_password=self.hash_password(password),
            is_active=True,
            is_verified=False,  # Precisa verificar email
            **kwargs
        )

        db.add(lawyer)
        db.commit()
        db.refresh(lawyer)

        return lawyer


# ==========================================
# DEPENDÊNCIAS PARA FASTAPI
# ==========================================

# Instância global do serviço
jwt_service = JWTAuthService()


def get_current_lawyer(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Dependency para obter advogado atual autenticado

    Uso:
        @app.get("/protected")
        def protected_route(lawyer = Depends(get_current_lawyer)):
            return {"lawyer_id": lawyer.id}

    Args:
        authorization: Header Authorization com Bearer token
        db: Sessão do banco

    Returns:
        Objeto Lawyer autenticado

    Raises:
        HTTPException: Se token for inválido ou advogado não existir
    """
    from models import Lawyer

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extrair token do header "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de autenticação inválido. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar token
    payload = jwt_service.verify_access_token(token)

    lawyer_id = payload.get("sub")
    if not lawyer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    # Buscar advogado no banco
    lawyer = db.query(Lawyer).filter(Lawyer.id == int(lawyer_id)).first()

    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Advogado não encontrado"
        )

    if not lawyer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada"
        )

    # Atualizar último acesso
    lawyer.last_login_at = datetime.utcnow()
    db.commit()

    return lawyer


def get_current_active_lawyer(
    lawyer = Depends(get_current_lawyer)
):
    """
    Dependency para garantir que advogado está ativo e verificado

    Args:
        lawyer: Advogado obtido de get_current_lawyer

    Returns:
        Objeto Lawyer ativo e verificado

    Raises:
        HTTPException: Se advogado não estiver verificado
    """
    if not lawyer.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email não verificado. Verifique seu email antes de continuar."
        )

    return lawyer


def get_optional_lawyer(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Dependency para rotas que podem ser acessadas com ou sem autenticação

    Returns:
        Objeto Lawyer se autenticado, None caso contrário
    """
    if not authorization:
        return None

    try:
        return get_current_lawyer(authorization, db)
    except HTTPException:
        return None


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def create_email_verification_token(lawyer_id: int) -> str:
    """
    Cria token de verificação de email (válido por 24h)

    Args:
        lawyer_id: ID do advogado

    Returns:
        Token de verificação
    """
    expire = datetime.utcnow() + timedelta(hours=24)

    payload = {
        "sub": str(lawyer_id),
        "exp": expire,
        "type": "email_verification"
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_email_token(token: str) -> Optional[int]:
    """
    Verifica token de confirmação de email

    Args:
        token: Token de verificação

    Returns:
        ID do advogado se válido, None caso contrário
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "email_verification":
            return None

        lawyer_id = payload.get("sub")
        return int(lawyer_id) if lawyer_id else None

    except JWTError:
        return None


def create_password_reset_token(lawyer_id: int) -> str:
    """
    Cria token de reset de senha (válido por 1h)

    Args:
        lawyer_id: ID do advogado

    Returns:
        Token de reset
    """
    expire = datetime.utcnow() + timedelta(hours=1)

    payload = {
        "sub": str(lawyer_id),
        "exp": expire,
        "type": "password_reset"
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_password_reset_token(token: str) -> Optional[int]:
    """
    Verifica token de reset de senha

    Args:
        token: Token de reset

    Returns:
        ID do advogado se válido, None caso contrário
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "password_reset":
            return None

        lawyer_id = payload.get("sub")
        return int(lawyer_id) if lawyer_id else None

    except JWTError:
        return None
