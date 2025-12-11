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

    # Obtener todas las fechas del rango donde el usuario tiene registros
    fechas_query = (
        select(registros.fecha)
        .where(
            and_(
                registros.usuario_id == current_user.id,
                registros.fecha >= fecha_inicio,
                registros.fecha <= fecha_fin
            )
        )
        .distinct()
        .order_by(registros.fecha)
    )
    fechas_result = await db.execute(fechas_query)
    fechas = [row[0] for row in fechas_result.all()]

    # Obtener todos los hábitos activos del usuario
    habitos_query = (
        select(habitos.id)
        .where(habitos.usuario_id == current_user.id)
    )
    habitos_result = await db.execute(habitos_query)
    habitos_ids = [row[0] for row in habitos_result.all()]

    respuesta = []
    for fecha in fechas:
        # Contar hábitos completados ese día
        completados_query = (
            select(func.count())
            .select_from(progreso_habitos)
            .join(registros, registros.id == progreso_habitos.registro_id)
            .where(
                and_(
                    registros.usuario_id == current_user.id,
                    registros.fecha == fecha,
                    progreso_habitos.completado == True
                )
            )
        )
        completados_result = await db.execute(completados_query)
        habitos_completados = completados_result.scalar() or 0

        respuesta.append(
            RendimientoDiaResponse(
                fecha=fecha,
                habitos=len(habitos_ids),
                habitos_completados=habitos_completados
            )
        )

    return respuesta


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

    # Subconsulta: todas las fechas del rango para el usuario
    fechas_query = (
        select(registros.fecha)
        .where(
            and_(
                registros.usuario_id == current_user.id,
                registros.fecha >= fecha_inicio,
                registros.fecha <= fecha_fin
            )
        )
        .distinct()
    )

    fechas_result = await db.execute(fechas_query)
    fechas = [row[0] for row in fechas_result.all()]

    # Si no hay fechas, retorna vacío
    if not fechas:
        return []

    # Consulta principal: para cada hábito, contar cuántos días debió hacerse y cuántos se completó
    habitos_query = (
        select(
            habitos.id,
            habitos.nombre.label('nombre_habito'),
            habitos.color
        )
        .where(habitos.usuario_id == current_user.id)
    )
    habitos_result = await db.execute(habitos_query)
    habitos_list = habitos_result.all()

    respuesta = []
    for habito in habitos_list:
        # Para cada fecha, buscar si hay progreso
        total_habitos = 0
        habitos_completados = 0
        fecha_primera = None

        for fecha in fechas:
            # Buscar progreso para este hábito y fecha
            prog_query = (
                select(progreso_habitos.completado)
                .join(registros, registros.id == progreso_habitos.registro_id)
                .where(
                    and_(
                        progreso_habitos.habito_id == habito.id,
                        registros.fecha == fecha,
                        registros.usuario_id == current_user.id
                    )
                )
            )
            prog_result = await db.execute(prog_query)
            prog = prog_result.scalar()
            total_habitos += 1
            if prog:
                habitos_completados += 1
            if fecha_primera is None or fecha < fecha_primera:
                fecha_primera = fecha

        respuesta.append(
            CumplimientoHabitoResponse(
                fecha=fecha_primera,
                nombre_habito=habito.nombre_habito,
                habitos_completados=habitos_completados,
                total_habitos=total_habitos,
                color=habito.color
            )
        )

    return respuesta
