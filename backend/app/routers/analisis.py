from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List
from datetime import datetime
import json

from app.database import get_db
from app.models import habitos, registros, progreso_habitos, usuario
from app.schemas import RendimientoDiaResponse, CumplimientoHabitoResponse
from app.security import get_current_user

router = APIRouter(prefix="/analisis", tags=["analisis"])


@router.get("/rendimiento", response_model=List[RendimientoDiaResponse])
async def get_rendimiento_por_dia(
    fecha_inicio: str,  # Formato: YYYY-MM-DD
    fecha_fin: str,     # Formato: YYYY-MM-DD
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el rendimiento de hábitos por día en un rango de fechas.

    Retorna para cada día:
    - fecha: La fecha del registro
    - habitos: Total de hábitos que aplican ese día
    - habitos_completados: Cuántos se completaron

    Args:
        fecha_inicio: Fecha de inicio (YYYY-MM-DD)
        fecha_fin: Fecha de fin (YYYY-MM-DD)
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Lista de rendimiento por día
    """
    # Validar fechas
    try:
        datetime.strptime(fecha_inicio, "%Y-%m-%d")
        datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )

    # Query para obtener registros y progresos en el rango de fechas
    query = (
        select(
            registros.fecha,
            func.count(progreso_habitos.id).label('total_habitos'),
            func.sum(progreso_habitos.completado).label('habitos_completados')
        )
        .join(progreso_habitos, progreso_habitos.registro_id == registros.id)
        .where(
            and_(
                registros.usuario_id == current_user.id,
                registros.fecha >= fecha_inicio,
                registros.fecha <= fecha_fin
            )
        )
        .group_by(registros.fecha)
        .order_by(registros.fecha)
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        RendimientoDiaResponse(
            fecha=row.fecha,
            habitos=row.total_habitos or 0,
            habitos_completados=int(row.habitos_completados or 0)
        )
        for row in rows
    ]


@router.get("/cumplimiento", response_model=List[CumplimientoHabitoResponse])
async def get_cumplimiento_habitos(
    fecha_inicio: str,  # Formato: YYYY-MM-DD
    fecha_fin: str,     # Formato: YYYY-MM-DD
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el cumplimiento de cada hábito en un rango de fechas.

    Retorna para cada hábito:
    - nombre_habito: Nombre del hábito
    - habitos_completados: Veces que se completó en el periodo
    - total_habitos: Total de días que aplica en el periodo
    - color: Color del hábito

    Args:
        fecha_inicio: Fecha de inicio (YYYY-MM-DD)
        fecha_fin: Fecha de fin (YYYY-MM-DD)
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Lista de cumplimiento por hábito
    """
    # Validar fechas
    try:
        datetime.strptime(fecha_inicio, "%Y-%m-%d")
        datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )

    # Query para obtener el cumplimiento por hábito
    query = (
        select(
            habitos.nombre.label('nombre_habito'),
            habitos.color,
            func.count(progreso_habitos.id).label('total_habitos'),
            func.sum(progreso_habitos.completado).label('habitos_completados'),
            func.min(registros.fecha).label('fecha')
        )
        .join(progreso_habitos, progreso_habitos.habito_id == habitos.id)
        .join(registros, registros.id == progreso_habitos.registro_id)
        .where(
            and_(
                habitos.usuario_id == current_user.id,
                registros.fecha >= fecha_inicio,
                registros.fecha <= fecha_fin
            )
        )
        .group_by(habitos.id, habitos.nombre, habitos.color)
        .order_by(habitos.nombre)
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        CumplimientoHabitoResponse(
            fecha=row.fecha,
            nombre_habito=row.nombre_habito,
            habitos_completados=int(row.habitos_completados or 0),
            total_habitos=row.total_habitos or 0,
            color=row.color
        )
        for row in rows
    ]
