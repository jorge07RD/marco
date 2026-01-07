from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List
import logging

from app.database import get_db
from app.models import usuario
from app.schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.security import get_current_user, hash_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


# NOTA: Endpoint deshabilitado por seguridad. Solo debería estar disponible para administradores.
# Para habilitarlo, agregar un campo 'is_admin' al modelo de usuario y verificar permisos.
#
# @router.get("/", response_model=List[UsuarioResponse])
# async def get_usuarios(
#     skip: int = 0,
#     limit: int = 100,
#     current_user: usuario = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Obtiene la lista de todos los usuarios (solo administradores)."""
#     # Verificar que es administrador
#     if not getattr(current_user, 'is_admin', False):
#         raise HTTPException(
#             status_code=403,
#             detail="Solo administradores pueden listar usuarios"
#         )
#     result = await db.execute(select(usuario).offset(skip).limit(limit))
#     return result.scalars().all()


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: int,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene un usuario específico por su ID (solo el propio usuario)."""
    # Verificar que es el mismo usuario
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes ver tu propio perfil"
        )

    result = await db.execute(select(usuario).where(usuario.id == usuario_id))
    db_usuario = result.scalar_one_or_none()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario


# NOTA: Endpoint deshabilitado. Usa /auth/register para crear nuevos usuarios.
# Este endpoint no debe estar disponible públicamente ya que:
# 1. No hashea la contraseña (inseguro)
# 2. No genera token de autenticación
# 3. No valida duplicados de email/nombre
# 4. El endpoint correcto es /auth/register
#
# @router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
# async def create_usuario(usuario_data: UsuarioCreate, db: AsyncSession = Depends(get_db)):
#     """Crea un nuevo usuario en el sistema."""
#     # Esta implementación NO es segura - usa /auth/register en su lugar
#     db_usuario = usuario(**usuario_data.model_dump())
#     db.add(db_usuario)
#     await db.commit()
#     await db.refresh(db_usuario)
#     return db_usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualiza los datos de un usuario existente (solo el propio usuario)."""
    # Verificar que es el mismo usuario
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes actualizar tu propio perfil"
        )

    result = await db.execute(select(usuario).where(usuario.id == usuario_id))
    db_usuario = result.scalar_one_or_none()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = usuario_data.model_dump(exclude_unset=True)

    # Si se está actualizando el email, verificar que no esté en uso
    if 'email' in update_data and update_data['email'] != db_usuario.email:
        email_check = await db.execute(
            select(usuario).where(usuario.email == update_data['email'])
        )
        if email_check.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"El email {update_data['email']} ya está en uso"
            )

    # Si se está actualizando el nombre, verificar que no esté en uso
    if 'nombre' in update_data and update_data['nombre'] != db_usuario.nombre:
        nombre_check = await db.execute(
            select(usuario).where(usuario.nombre == update_data['nombre'])
        )
        if nombre_check.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"El nombre {update_data['nombre']} ya está en uso"
            )

    # Si se está actualizando la contraseña, hashearla
    if 'contrasena' in update_data:
        update_data['contrasena'] = hash_password(update_data['contrasena'])

    for key, value in update_data.items():
        setattr(db_usuario, key, value)

    await db.commit()
    await db.refresh(db_usuario)
    return db_usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(
    usuario_id: int,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Elimina un usuario del sistema por su ID (solo el propio usuario)."""
    # Verificar que es el mismo usuario
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes eliminar tu propio perfil"
        )

    result = await db.execute(select(usuario).where(usuario.id == usuario_id))
    db_usuario = result.scalar_one_or_none()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    await db.delete(db_usuario)
    await db.commit()
