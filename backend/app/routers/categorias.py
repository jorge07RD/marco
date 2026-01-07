from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import categorias, usuario
from app.schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from app.security import get_current_user

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("/", response_model=List[CategoriaResponse])
async def get_categorias(
    skip: int = 0,
    limit: int = 100,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene la lista de todas las categorías de hábitos (requiere autenticación)."""
    result = await db.execute(select(categorias).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{categoria_id}", response_model=CategoriaResponse)
async def get_categoria(
    categoria_id: int,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene una categoría específica por su ID (requiere autenticación)."""
    result = await db.execute(select(categorias).where(categorias.id == categoria_id))
    db_categoria = result.scalar_one_or_none()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return db_categoria


@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def create_categoria(
    categoria_data: CategoriaCreate,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Crea una nueva categoría para clasificar hábitos (requiere autenticación)."""
    # Verificar si ya existe una categoría con ese nombre
    existing = await db.execute(
        select(categorias).where(categorias.nombre == categoria_data.nombre)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una categoría con el nombre '{categoria_data.nombre}'"
        )

    db_categoria = categorias(**categoria_data.model_dump())
    db.add(db_categoria)
    await db.commit()
    await db.refresh(db_categoria)
    return db_categoria


@router.put("/{categoria_id}", response_model=CategoriaResponse)
async def update_categoria(
    categoria_id: int,
    categoria_data: CategoriaUpdate,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualiza el nombre u otros datos de una categoría existente (requiere autenticación)."""
    result = await db.execute(select(categorias).where(categorias.id == categoria_id))
    db_categoria = result.scalar_one_or_none()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    update_data = categoria_data.model_dump(exclude_unset=True)

    # Si se está actualizando el nombre, verificar que no esté en uso
    if 'nombre' in update_data and update_data['nombre'] != db_categoria.nombre:
        existing = await db.execute(
            select(categorias).where(categorias.nombre == update_data['nombre'])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una categoría con el nombre '{update_data['nombre']}'"
            )

    for key, value in update_data.items():
        setattr(db_categoria, key, value)

    await db.commit()
    await db.refresh(db_categoria)
    return db_categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categoria(
    categoria_id: int,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Elimina una categoría del sistema por su ID (requiere autenticación)."""
    result = await db.execute(select(categorias).where(categorias.id == categoria_id))
    db_categoria = result.scalar_one_or_none()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    await db.delete(db_categoria)
    await db.commit()
