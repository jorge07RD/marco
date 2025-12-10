from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from app.database import get_db
from app.models import usuario
from app.schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.security import hash_password
from app.dependencies import get_current_user

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/", response_model=List[UsuarioResponse])
async def get_usuarios(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Obtiene la lista de todos los usuarios con paginación."""
    result = await db.execute(select(usuario).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/me", response_model=UsuarioResponse)
async def get_current_user_info(current_user: usuario = Depends(get_current_user)):
    """Obtiene la información del usuario autenticado."""
    return current_user


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: usuario = Depends(get_current_user)
):
    """Obtiene un usuario específico por su ID."""
    result = await db.execute(select(usuario).where(usuario.id == usuario_id))
    db_usuario = result.scalar_one_or_none()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(usuario_data: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    """Crea un nuevo usuario en el sistema."""
    # Hashear la contraseña antes de guardar
    usuario_dict = usuario_data.model_dump()
    usuario_dict['contrasena'] = hash_password(usuario_dict['contrasena'])

    db_usuario = usuario(**usuario_dict)
    db.add(db_usuario)
    await db.commit()
    await db.refresh(db_usuario)
    return db_usuario


@router.put("/me", response_model=UsuarioResponse)
async def update_current_user(
    usuario_data: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: usuario = Depends(get_current_user)
):
    """Actualiza los datos del usuario autenticado."""
    update_data = usuario_data.model_dump(exclude_unset=True)

    # Si se está actualizando la contraseña, hashearla
    if 'contrasena' in update_data and update_data['contrasena']:
        update_data['contrasena'] = hash_password(update_data['contrasena'])

    for key, value in update_data.items():
        setattr(current_user, key, value)

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: usuario = Depends(get_current_user)
):
    """Actualiza los datos de un usuario existente (requiere autenticación)."""
    # Solo permitir actualizar el propio usuario
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este usuario"
        )

    update_data = usuario_data.model_dump(exclude_unset=True)

    # Si se está actualizando la contraseña, hashearla
    if 'contrasena' in update_data and update_data['contrasena']:
        update_data['contrasena'] = hash_password(update_data['contrasena'])

    for key, value in update_data.items():
        setattr(current_user, key, value)

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina un usuario del sistema por su ID."""
    result = await db.execute(select(usuario).where(usuario.id == usuario_id))
    db_usuario = result.scalar_one_or_none()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    await db.delete(db_usuario)
    await db.commit()
