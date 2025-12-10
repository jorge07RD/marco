"""
Módulo de seguridad para autenticación y autorización.

Proporciona funciones para:
- Hashing y verificación de contraseñas con bcrypt
- Generación y verificación de tokens JWT
- Dependencias para obtener el usuario autenticado
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import usuario

# Configuración
settings = get_settings()

# Security scheme para extraer el token del header Authorization
security = HTTPBearer()

# Configuración JWT (cargada desde variables de entorno)
SECRET_KEY = settings.secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt.

    Args:
        password: Contraseña en texto plano

    Returns:
        Contraseña hasheada como string

    Note:
        Bcrypt tiene un límite de 72 bytes para contraseñas.
        Las contraseñas se truncan automáticamente si exceden este límite.
    """
    # Convertir a bytes y truncar a 72 bytes (límite de bcrypt)
    password_bytes = password.encode('utf-8')[:72]
    # Generar salt y hashear
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Retornar como string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash.

    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña almacenado en BD

    Returns:
        True si la contraseña coincide, False en caso contrario

    Note:
        Bcrypt tiene un límite de 72 bytes para contraseñas.
        Las contraseñas se truncan automáticamente si exceden este límite.
    """
    # Convertir a bytes y truncar a 72 bytes (límite de bcrypt)
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    # Verificar contraseña
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.

    Args:
        data: Datos a incluir en el token (típicamente {"sub": user_id})
        expires_delta: Tiempo de expiración opcional

    Returns:
        Token JWT firmado
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> usuario:
    """
    Dependencia para obtener el usuario autenticado actual.

    Extrae el token JWT del header Authorization, lo valida,
    y retorna el usuario correspondiente.

    Args:
        credentials: Credenciales HTTP Bearer (token)
        db: Sesión de base de datos

    Returns:
        Usuario autenticado

    Raises:
        HTTPException 401: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extraer token
        token = credentials.credentials

        # Decodificar token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Buscar usuario en la base de datos
    result = await db.execute(
        select(usuario).where(usuario.id == int(user_id))
    )
    db_user = result.scalar_one_or_none()

    if db_user is None:
        raise credentials_exception

    return db_user


async def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[usuario]:
    """
    Autentica un usuario verificando email y contraseña.

    Args:
        email: Email del usuario
        password: Contraseña en texto plano
        db: Sesión de base de datos

    Returns:
        Usuario si las credenciales son válidas, None en caso contrario
    """
    # Buscar usuario por email
    result = await db.execute(
        select(usuario).where(usuario.email == email)
    )
    db_user = result.scalar_one_or_none()

    if not db_user:
        return None

    # Verificar contraseña
    if not verify_password(password, db_user.contrasena):
        return None

    return db_user
