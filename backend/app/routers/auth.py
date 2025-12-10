"""
Router de autenticación.

Endpoints para registro, login y obtención del usuario actual.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import usuario
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, UsuarioResponse, UsuarioUpdate
from app.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password
)

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario y retorna un token de acceso."
)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Registra un nuevo usuario en el sistema.

    Args:
        user_data: Datos del nuevo usuario (nombre, email, password)
        db: Sesión de base de datos

    Returns:
        Token de acceso JWT y datos del usuario creado

    Raises:
        HTTPException 400: Si el email ya está registrado
    """
    # Verificar si el email ya existe
    result = await db.execute(
        select(usuario).where(usuario.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email {user_data.email} ya está registrado"
        )

    # Verificar si el nombre ya existe
    result = await db.execute(
        select(usuario).where(usuario.nombre == user_data.nombre)
    )
    existing_nombre = result.scalar_one_or_none()

    if existing_nombre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El nombre de usuario {user_data.nombre} ya está en uso"
        )

    # Crear nuevo usuario con contraseña hasheada
    hashed_password = hash_password(user_data.password)

    new_user = usuario(
        nombre=user_data.nombre,
        email=user_data.email,
        contrasena=hashed_password,
        ver_futuro=user_data.ver_futuro
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generar token de acceso
    access_token = create_access_token(data={"sub": str(new_user.id)})

    # Preparar respuesta del usuario
    user_response = UsuarioResponse(
        id=new_user.id,
        nombre=new_user.nombre,
        email=new_user.email,
        ver_futuro=new_user.ver_futuro,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna un token de acceso."
)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Inicia sesión de un usuario existente.

    Args:
        credentials: Credenciales de login (email y password)
        db: Sesión de base de datos

    Returns:
        Token de acceso JWT y datos del usuario

    Raises:
        HTTPException 401: Si las credenciales son inválidas
    """
    # Autenticar usuario
    user = await authenticate_user(credentials.email, credentials.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generar token de acceso
    access_token = create_access_token(data={"sub": str(user.id)})

    # Preparar respuesta del usuario
    user_response = UsuarioResponse(
        id=user.id,
        nombre=user.nombre,
        email=user.email,
        ver_futuro=user.ver_futuro,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Obtener usuario actual",
    description="Retorna los datos del usuario autenticado."
)
async def get_me(
    current_user: usuario = Depends(get_current_user)
) -> UsuarioResponse:
    """
    Obtiene los datos del usuario autenticado actual.

    Args:
        current_user: Usuario autenticado (inyectado por dependencia)

    Returns:
        Datos del usuario actual
    """
    return UsuarioResponse(
        id=current_user.id,
        nombre=current_user.nombre,
        email=current_user.email,
        ver_futuro=current_user.ver_futuro,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.put(
    "/me",
    response_model=UsuarioResponse,
    summary="Actualizar usuario actual",
    description="Actualiza los datos del usuario autenticado."
)
async def update_me(
    user_data: UsuarioUpdate,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UsuarioResponse:
    """
    Actualiza los datos del usuario autenticado actual.

    Args:
        user_data: Datos a actualizar (nombre, email, ver_futuro)
        current_user: Usuario autenticado (inyectado por dependencia)
        db: Sesión de base de datos

    Returns:
        Datos actualizados del usuario

    Raises:
        HTTPException 400: Si el email o nombre ya está en uso por otro usuario
    """
    # Obtener los datos a actualizar (solo los que se enviaron)
    update_data = user_data.model_dump(exclude_unset=True)

    # Si se está actualizando el email, verificar que no esté en uso
    if 'email' in update_data and update_data['email'] != current_user.email:
        result = await db.execute(
            select(usuario).where(usuario.email == update_data['email'])
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El email {update_data['email']} ya está en uso"
            )

    # Si se está actualizando el nombre, verificar que no esté en uso
    if 'nombre' in update_data and update_data['nombre'] != current_user.nombre:
        result = await db.execute(
            select(usuario).where(usuario.nombre == update_data['nombre'])
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El nombre {update_data['nombre']} ya está en uso"
            )

    # Actualizar los campos
    for key, value in update_data.items():
        setattr(current_user, key, value)

    await db.commit()
    await db.refresh(current_user)

    return UsuarioResponse(
        id=current_user.id,
        nombre=current_user.nombre,
        email=current_user.email,
        ver_futuro=current_user.ver_futuro,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
