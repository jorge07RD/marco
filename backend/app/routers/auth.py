"""
Router de autenticación con endpoints de login y registro.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.database import get_db
from app.models import usuario
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, AuthResponse
from app.security import hash_password, verify_password, create_access_token
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.

    - Verifica que el email no esté en uso
    - Hashea la contraseña antes de guardarla
    - Crea y retorna un token de acceso
    """
    # Verificar si el email ya está registrado
    result = await db.execute(select(usuario).where(usuario.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Verificar si el nombre de usuario ya está en uso
    result = await db.execute(select(usuario).where(usuario.nombre == request.nombre))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso"
        )

    # Crear el nuevo usuario con la contraseña hasheada
    hashed_password = hash_password(request.contrasena)
    new_user = usuario(
        nombre=request.nombre,
        email=request.email,
        contrasena=hashed_password,
        ver_futuro=False
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Crear token de acceso
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        usuario=new_user
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Autentica un usuario y retorna un token de acceso.

    - Verifica que el usuario exista
    - Verifica que la contraseña sea correcta
    - Crea y retorna un token de acceso
    """
    # Buscar usuario por email
    result = await db.execute(select(usuario).where(usuario.email == request.email))
    user = result.scalar_one_or_none()

    # Verificar que el usuario exista
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar la contraseña
    if not verify_password(request.contrasena, user.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token de acceso
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        usuario=user
    )
