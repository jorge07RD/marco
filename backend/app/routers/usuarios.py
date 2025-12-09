from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from app.database import get_db
from app.models import usuario
from app.schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/", response_model=List[UsuarioResponse])
async def get_usuarios(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Obtiene la lista de todos los usuarios con paginación."""
    result = await db.execute(select(usuario).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene un usuario específico por su ID."""
    result = await db.execute(select(usuario).where(usuario.id == usuario_id))
    db_usuario = result.scalar_one_or_none()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(usuario_data: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    """Crea un nuevo usuario en el sistema."""
    db_usuario = usuario(**usuario_data.model_dump())
    db.add(db_usuario)
    await db.commit()
    await db.refresh(db_usuario)
    return db_usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(usuario_id: int, usuario_data: UsuarioUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza los datos de un usuario existente."""
    result = await db.execute(select(usuario).where(usuario.id == usuario_id))
    db_usuario = result.scalar_one_or_none()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    update_data = usuario_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_usuario, key, value)
    
    await db.commit()
    await db.refresh(db_usuario)
    return db_usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina un usuario del sistema por su ID."""
    result = await db.execute(select(usuario).where(usuario.id == usuario_id))
    db_usuario = result.scalar_one_or_none()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    await db.delete(db_usuario)
    await db.commit()
