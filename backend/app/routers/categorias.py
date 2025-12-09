from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import categorias
from app.schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("/", response_model=List[CategoriaResponse])
async def get_categorias(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Obtiene la lista de todas las categorías de hábitos."""
    result = await db.execute(select(categorias).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{categoria_id}", response_model=CategoriaResponse)
async def get_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene una categoría específica por su ID."""
    result = await db.execute(select(categorias).where(categorias.id == categoria_id))
    db_categoria = result.scalar_one_or_none()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return db_categoria


@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def create_categoria(categoria_data: CategoriaCreate, db: AsyncSession = Depends(get_db)):
    """Crea una nueva categoría para clasificar hábitos."""
    db_categoria = categorias(**categoria_data.model_dump())
    db.add(db_categoria)
    await db.commit()
    await db.refresh(db_categoria)
    return db_categoria


@router.put("/{categoria_id}", response_model=CategoriaResponse)
async def update_categoria(categoria_id: int, categoria_data: CategoriaUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza el nombre u otros datos de una categoría existente."""
    result = await db.execute(select(categorias).where(categorias.id == categoria_id))
    db_categoria = result.scalar_one_or_none()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    update_data = categoria_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_categoria, key, value)
    
    await db.commit()
    await db.refresh(db_categoria)
    return db_categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina una categoría del sistema por su ID."""
    result = await db.execute(select(categorias).where(categorias.id == categoria_id))
    db_categoria = result.scalar_one_or_none()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    await db.delete(db_categoria)
    await db.commit()
