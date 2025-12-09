from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import habito_dias
from app.schemas import HabitoDiaCreate, HabitoDiaUpdate, HabitoDiaResponse

router = APIRouter(prefix="/habito-dias", tags=["habito_dias"])


@router.get("/", response_model=List[HabitoDiaResponse])
async def get_habito_dias(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Obtiene la lista de todos los días de hábitos con paginación."""
    result = await db.execute(select(habito_dias).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/habito/{habito_id}", response_model=List[HabitoDiaResponse])
async def get_habito_dias_by_habito(habito_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene todos los días registrados para un hábito específico."""
    result = await db.execute(select(habito_dias).where(habito_dias.habito_id == habito_id))
    return result.scalars().all()


@router.get("/{habito_dia_id}", response_model=HabitoDiaResponse)
async def get_habito_dia(habito_dia_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene un día de hábito específico por su ID."""
    result = await db.execute(select(habito_dias).where(habito_dias.id == habito_dia_id))
    db_habito_dia = result.scalar_one_or_none()
    if not db_habito_dia:
        raise HTTPException(status_code=404, detail="Habito dia no encontrado")
    return db_habito_dia


@router.post("/", response_model=HabitoDiaResponse, status_code=status.HTTP_201_CREATED)
async def create_habito_dia(habito_dia_data: HabitoDiaCreate, db: AsyncSession = Depends(get_db)):
    """Crea un nuevo registro de día para un hábito."""
    db_habito_dia = habito_dias(**habito_dia_data.model_dump())
    db.add(db_habito_dia)
    await db.commit()
    await db.refresh(db_habito_dia)
    return db_habito_dia


@router.put("/{habito_dia_id}", response_model=HabitoDiaResponse)
async def update_habito_dia(habito_dia_id: int, habito_dia_data: HabitoDiaUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza el estado de cumplimiento de un día de hábito."""
    result = await db.execute(select(habito_dias).where(habito_dias.id == habito_dia_id))
    db_habito_dia = result.scalar_one_or_none()
    if not db_habito_dia:
        raise HTTPException(status_code=404, detail="Habito dia no encontrado")
    
    update_data = habito_dia_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_habito_dia, key, value)
    
    await db.commit()
    await db.refresh(db_habito_dia)
    return db_habito_dia


@router.delete("/{habito_dia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habito_dia(habito_dia_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina un día de hábito del sistema por su ID."""
    result = await db.execute(select(habito_dias).where(habito_dias.id == habito_dia_id))
    db_habito_dia = result.scalar_one_or_none()
    if not db_habito_dia:
        raise HTTPException(status_code=404, detail="Habito dia no encontrado")
    
    await db.delete(db_habito_dia)
    await db.commit()
