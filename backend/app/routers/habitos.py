from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import date
import logging

from app.database import get_db
from app.models import habitos, registros, progreso_habitos, usuario
from app.schemas import HabitoCreate, HabitoUpdate, HabitoResponse
from app.security import get_current_user
from app.utils import dia_en_lista, obtener_dia_letra

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/habitos", tags=["habitos"])


async def agregar_habito_a_registro_hoy(habito_id: int, usuario_id: int, db: AsyncSession):
    """
    Agrega un hábito al registro del día actual si existe.
    No crea el registro si no existe.
    """
    hoy = date.today().isoformat()
    
    # Buscar registro de hoy
    result = await db.execute(
        select(registros).where(
            and_(registros.usuario_id == usuario_id, registros.fecha == hoy)
        )
    )
    registro = result.scalar_one_or_none()
    
    if registro:
        # Verificar si ya existe el progreso para este hábito
        prog_result = await db.execute(
            select(progreso_habitos).where(
                and_(
                    progreso_habitos.registro_id == registro.id,
                    progreso_habitos.habito_id == habito_id
                )
            )
        )
        existe = prog_result.scalar_one_or_none()
        
        if not existe:
            # Crear progreso para el hábito
            progreso = progreso_habitos(
                registro_id=registro.id,
                habito_id=habito_id,
                valor=0,
                completado=False
            )
            db.add(progreso)


async def quitar_habito_de_registro_hoy(habito_id: int, usuario_id: int, db: AsyncSession):
    """
    Quita un hábito del registro del día actual si existe.
    """
    hoy = date.today().isoformat()
    
    # Buscar registro de hoy
    result = await db.execute(
        select(registros).where(
            and_(registros.usuario_id == usuario_id, registros.fecha == hoy)
        )
    )
    registro = result.scalar_one_or_none()
    
    if registro:
        # Buscar y eliminar el progreso
        prog_result = await db.execute(
            select(progreso_habitos).where(
                and_(
                    progreso_habitos.registro_id == registro.id,
                    progreso_habitos.habito_id == habito_id
                )
            )
        )
        progreso = prog_result.scalar_one_or_none()
        
        if progreso:
            await db.delete(progreso)


@router.get("/", response_model=List[HabitoResponse])
async def get_habitos(
    skip: int = 0,
    limit: int = 100,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todos los hábitos del usuario autenticado con paginación."""
    result = await db.execute(
        select(habitos)
        .where(habitos.usuario_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{habito_id}", response_model=HabitoResponse)
async def get_habito(
    habito_id: int,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene un hábito específico por su ID (solo si pertenece al usuario)."""
    result = await db.execute(
        select(habitos).where(
            and_(habitos.id == habito_id, habitos.usuario_id == current_user.id)
        )
    )
    db_habito = result.scalar_one_or_none()
    if not db_habito:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    return db_habito


@router.post("/", response_model=HabitoResponse, status_code=status.HTTP_201_CREATED)
async def create_habito(
    habito_data: HabitoCreate,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Crea un nuevo hábito para el usuario autenticado."""
    # Agregar el usuario_id del usuario autenticado
    habito_dict = habito_data.model_dump()
    habito_dict['usuario_id'] = current_user.id

    db_habito = habitos(**habito_dict)
    db.add(db_habito)
    await db.flush()  # Para obtener el ID

    # Si el día actual está en los días del hábito y está activo, agregarlo al registro de hoy
    dia_hoy = obtener_dia_letra(date.today())
    if db_habito.activo and dia_en_lista(db_habito.dias, dia_hoy):
        await agregar_habito_a_registro_hoy(db_habito.id, current_user.id, db)

    await db.commit()
    await db.refresh(db_habito)
    return db_habito


@router.put("/{habito_id}", response_model=HabitoResponse)
async def update_habito(
    habito_id: int,
    habito_data: HabitoUpdate,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualiza la configuración de un hábito existente (solo si pertenece al usuario)."""
    result = await db.execute(
        select(habitos).where(
            and_(habitos.id == habito_id, habitos.usuario_id == current_user.id)
        )
    )
    db_habito = result.scalar_one_or_none()
    if not db_habito:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    
    # Guardar estado anterior de días y activo
    dias_antes = db_habito.dias
    activo_antes = db_habito.activo
    
    update_data = habito_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_habito, key, value)

    # Verificar si cambió la configuración de días o activo
    dia_hoy = obtener_dia_letra(date.today())
    estaba_en_hoy = activo_antes and dia_en_lista(dias_antes, dia_hoy)
    esta_en_hoy = db_habito.activo and dia_en_lista(db_habito.dias, dia_hoy)
    
    if not estaba_en_hoy and esta_en_hoy:
        # Ahora debe aparecer en el día de hoy
        await agregar_habito_a_registro_hoy(db_habito.id, db_habito.usuario_id, db)
    elif estaba_en_hoy and not esta_en_hoy:
        # Ya no debe aparecer en el día de hoy
        await quitar_habito_de_registro_hoy(db_habito.id, db_habito.usuario_id, db)
    
    await db.commit()
    await db.refresh(db_habito)
    return db_habito


@router.delete("/{habito_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habito(
    habito_id: int,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Elimina un hábito del usuario por su ID (solo si pertenece al usuario)."""
    result = await db.execute(
        select(habitos).where(
            and_(habitos.id == habito_id, habitos.usuario_id == current_user.id)
        )
    )
    db_habito = result.scalar_one_or_none()
    if not db_habito:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    
    # Eliminar todos los progresos asociados a este hábito
    progresos_result = await db.execute(
        select(progreso_habitos).where(progreso_habitos.habito_id == habito_id)
    )
    progresos = progresos_result.scalars().all()
    for progreso in progresos:
        await db.delete(progreso)
    
    # Eliminar el hábito
    await db.delete(db_habito)
    await db.commit()
