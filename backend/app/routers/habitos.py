from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import date
import json

from app.database import get_db
from app.models import habitos, registros, progreso_habitos, usuario
from app.schemas import HabitoCreate, HabitoUpdate, HabitoResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/habitos", tags=["habitos"])


def get_dia_letra_hoy() -> str:
    """Retorna la letra del día actual (D, L, M, X, J, V, S)."""
    dias_semana = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
    return dias_semana[date.today().weekday()]


def dia_en_lista(dias_str: str, dia_letra: str) -> bool:
    """Verifica si un día está en la lista de días del hábito."""
    try:
        dias = json.loads(dias_str)
        return dia_letra in dias
    except:
        return False


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
async def get_habitos(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Obtiene la lista de todos los hábitos con paginación."""
    result = await db.execute(select(habitos).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/me", response_model=List[HabitoResponse])
async def get_my_habitos(
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todos los hábitos del usuario autenticado."""
    result = await db.execute(select(habitos).where(habitos.usuario_id == current_user.id))
    return result.scalars().all()


@router.get("/usuario/{usuario_id}")
async def get_habitos_by_usuario(
    usuario_id: int,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todos los hábitos de un usuario específico (requiere autenticación)."""
    # Solo permitir ver los propios hábitos
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver los hábitos de otro usuario"
        )
    result = await db.execute(select(habitos).where(habitos.usuario_id == usuario_id))
    return result.scalars().all()


@router.get("/{habito_id}", response_model=HabitoResponse)
async def get_habito(habito_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene un hábito específico por su ID."""
    result = await db.execute(select(habitos).where(habitos.id == habito_id))
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
    # Verificar que el usuario_id del hábito coincida con el usuario autenticado
    if habito_data.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes crear hábitos para otro usuario"
        )

    db_habito = habitos(**habito_data.model_dump())
    db.add(db_habito)
    await db.flush()  # Para obtener el ID

    # Si el día actual está en los días del hábito y está activo, agregarlo al registro de hoy
    dia_hoy = get_dia_letra_hoy()
    if db_habito.activo and dia_en_lista(db_habito.dias, dia_hoy):
        await agregar_habito_a_registro_hoy(db_habito.id, db_habito.usuario_id, db)

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
    """Actualiza la configuración de un hábito existente."""
    result = await db.execute(select(habitos).where(habitos.id == habito_id))
    db_habito = result.scalar_one_or_none()
    if not db_habito:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")

    # Verificar que el hábito pertenece al usuario autenticado
    if db_habito.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este hábito"
        )
    
    # Guardar estado anterior de días y activo
    dias_antes = db_habito.dias
    activo_antes = db_habito.activo
    
    update_data = habito_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_habito, key, value)
    
    # Verificar si cambió la configuración de días o activo
    dia_hoy = get_dia_letra_hoy()
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
    """Elimina un hábito del sistema por su ID y todos sus progresos asociados."""
    result = await db.execute(select(habitos).where(habitos.id == habito_id))
    db_habito = result.scalar_one_or_none()
    if not db_habito:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")

    # Verificar que el hábito pertenece al usuario autenticado
    if db_habito.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este hábito"
        )
    
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
