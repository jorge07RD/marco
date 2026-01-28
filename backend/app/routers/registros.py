from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import date, datetime
import logging

from app.database import get_db
from app.models import registros, progreso_habitos, usuario, habitos
from app.schemas import (
    RegistroCreate, RegistroUpdate, RegistroResponse, RegistroConProgresos,
    ProgresoHabitoCreate, ProgresoHabitoUpdate, ProgresoHabitoResponse,
    ProgresoDiaCalendario, ProgresoHabitoDiaCalendario
)
from app.security import get_current_user
from app.utils import parsear_dias_habito, obtener_dia_letra

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registros", tags=["registros"])


@router.get("/", response_model=List[RegistroResponse])
async def get_registros(
    skip: int = 0,
    limit: int = 100,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todos los registros del usuario autenticado."""
    result = await db.execute(
        select(registros)
        .where(registros.usuario_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/fecha/{fecha}", response_model=RegistroConProgresos)
async def get_or_create_registro_por_fecha(
    fecha: str,  # Formato: YYYY-MM-DD
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el registro del usuario autenticado para una fecha específica.
    Si no existe, lo crea automáticamente con los hábitos activos para ese día.
    Si la fecha es futura, verifica que el usuario tenga 'ver_futuro' activado.
    """
    # Validar formato de fecha
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    # Verificar si es fecha futura
    hoy = date.today()
    if fecha_obj > hoy:
        if not current_user.ver_futuro:
            raise HTTPException(
                status_code=403,
                detail="No puedes ver fechas futuras. Activa 'Ver futuro' en configuración."
            )
    
    # Buscar registro existente
    result = await db.execute(
        select(registros).where(
            and_(registros.usuario_id == current_user.id, registros.fecha == fecha)
        )
    )
    db_registro = result.scalar_one_or_none()

    # Si no existe, crear uno nuevo
    if not db_registro:
        db_registro = registros(usuario_id=current_user.id, fecha=fecha)
        db.add(db_registro)
        await db.flush()

        # Obtener hábitos activos del usuario para ese día de la semana
        dia_letra = obtener_dia_letra(fecha_obj)

        habitos_result = await db.execute(
            select(habitos).where(
                and_(habitos.usuario_id == current_user.id, habitos.activo == 1)
            )
        )
        habitos_usuario = habitos_result.scalars().all()

        # Crear progreso para cada hábito activo ese día
        for habito in habitos_usuario:
            try:
                dias_habito = parsear_dias_habito(habito.dias)

                if dia_letra in dias_habito:
                    progreso = progreso_habitos(
                        registro_id=db_registro.id,
                        habito_id=habito.id,
                        valor=0,
                        completado=False
                    )
                    db.add(progreso)

            except ValueError as e:
                # Log del error pero continuar con otros hábitos
                logger.warning(
                    f"Error parseando días del hábito {habito.id}: {e}. "
                    f"Saltando este hábito."
                )
                continue
        
        await db.commit()
        await db.refresh(db_registro)
    
    # Obtener progresos del registro
    progresos_result = await db.execute(
        select(progreso_habitos).where(progreso_habitos.registro_id == db_registro.id)
    )
    progresos = progresos_result.scalars().all()
    
    return RegistroConProgresos(
        id=db_registro.id,
        usuario_id=db_registro.usuario_id,
        fecha=db_registro.fecha,
        notas=db_registro.notas,
        created_at=db_registro.created_at,
        updated_at=db_registro.updated_at,
        progresos=[ProgresoHabitoResponse(
            id=p.id,
            registro_id=p.registro_id,
            habito_id=p.habito_id,
            valor=p.valor,
            completado=p.completado,
            created_at=p.created_at,
            updated_at=p.updated_at
        ) for p in progresos]
    )


@router.put("/progreso/{progreso_id}", response_model=ProgresoHabitoResponse)
async def update_progreso(
    progreso_id: int,
    progreso_data: ProgresoHabitoUpdate,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualiza el progreso de un hábito específico (solo del usuario autenticado)."""
    result = await db.execute(
        select(progreso_habitos).where(progreso_habitos.id == progreso_id)
    )
    db_progreso = result.scalar_one_or_none()
    if not db_progreso:
        raise HTTPException(status_code=404, detail="Progreso no encontrado")

    # Verificar que el progreso pertenece al usuario actual
    registro_result = await db.execute(
        select(registros).where(registros.id == db_progreso.registro_id)
    )
    registro = registro_result.scalar_one_or_none()

    if not registro or registro.usuario_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para modificar este progreso"
        )

    update_data = progreso_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_progreso, key, value)

    await db.commit()
    await db.refresh(db_progreso)
    return db_progreso


@router.post("/progreso/toggle/{progreso_id}", response_model=ProgresoHabitoResponse)
async def toggle_progreso(
    progreso_id: int,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Alterna el estado de completado de un progreso (solo del usuario autenticado)."""
    result = await db.execute(
        select(progreso_habitos).where(progreso_habitos.id == progreso_id)
    )
    db_progreso = result.scalar_one_or_none()
    if not db_progreso:
        raise HTTPException(status_code=404, detail="Progreso no encontrado")

    # Verificar que el progreso pertenece al usuario actual
    registro_result = await db.execute(
        select(registros).where(registros.id == db_progreso.registro_id)
    )
    registro = registro_result.scalar_one_or_none()

    if not registro or registro.usuario_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para modificar este progreso"
        )

    # Obtener la meta del hábito
    habito_result = await db.execute(
        select(habitos).where(habitos.id == db_progreso.habito_id)
    )
    db_habito = habito_result.scalar_one_or_none()

    if db_progreso.completado:
        db_progreso.completado = False
        db_progreso.valor = 0
    else:
        db_progreso.completado = True
        db_progreso.valor = db_habito.meta_diaria if db_habito else 1

    await db.commit()
    await db.refresh(db_progreso)
    return db_progreso


@router.get("/{registro_id}", response_model=RegistroResponse)
async def get_registro(
    registro_id: int,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene un registro específico por su ID (solo del usuario autenticado)."""
    result = await db.execute(select(registros).where(registros.id == registro_id))
    db_registro = result.scalar_one_or_none()
    if not db_registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    # Verificar que el registro pertenece al usuario actual
    if db_registro.usuario_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para ver este registro"
        )

    return db_registro


@router.put("/{registro_id}", response_model=RegistroResponse)
async def update_registro(
    registro_id: int,
    registro_data: RegistroUpdate,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualiza las notas de un registro (solo del usuario autenticado)."""
    result = await db.execute(select(registros).where(registros.id == registro_id))
    db_registro = result.scalar_one_or_none()
    if not db_registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    # Verificar que el registro pertenece al usuario actual
    if db_registro.usuario_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para modificar este registro"
        )

    update_data = registro_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_registro, key, value)

    await db.commit()
    await db.refresh(db_registro)
    return db_registro


@router.delete("/{registro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registro(
    registro_id: int,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Elimina un registro del sistema por su ID (solo del usuario autenticado)."""
    result = await db.execute(select(registros).where(registros.id == registro_id))
    db_registro = result.scalar_one_or_none()
    if not db_registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    # Verificar que el registro pertenece al usuario actual
    if db_registro.usuario_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para eliminar este registro"
        )

    await db.delete(db_registro)
    await db.commit()


@router.get("/calendario/{year}/{month}", response_model=List[ProgresoDiaCalendario])
async def get_progreso_mes(
    year: int,
    month: int,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el progreso de cada día del mes para mostrar en el calendario.

    Args:
        year: Año del calendario
        month: Mes del calendario (1-12)
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Lista con progreso diario del mes
    """
    import calendar
    from datetime import timedelta

    # Validar mes
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Mes inválido. Debe estar entre 1 y 12")

    # Calcular primer y último día del mes
    primer_dia = date(year, month, 1)
    _, ultimo_dia_mes = calendar.monthrange(year, month)
    ultimo_dia = date(year, month, ultimo_dia_mes)

    # Obtener hábitos activos del usuario creados antes del último día del mes
    habitos_result = await db.execute(
        select(habitos).where(
            and_(
                habitos.usuario_id == current_user.id,
                habitos.activo == 1,
                habitos.created_at <= datetime.combine(ultimo_dia, datetime.max.time())
            )
        )
    )
    habitos_usuario = habitos_result.scalars().all()

    # Obtener todos los registros del mes
    registros_result = await db.execute(
        select(registros).where(
            and_(
                registros.usuario_id == current_user.id,
                registros.fecha >= primer_dia.strftime("%Y-%m-%d"),
                registros.fecha <= ultimo_dia.strftime("%Y-%m-%d")
            )
        )
    )
    registros_mes = {r.fecha: r for r in registros_result.scalars().all()}

    # Obtener todos los progresos de esos registros
    if registros_mes:
        registro_ids = [r.id for r in registros_mes.values()]
        progresos_result = await db.execute(
            select(progreso_habitos).where(progreso_habitos.registro_id.in_(registro_ids))
        )
        progresos_list = progresos_result.scalars().all()

        # Agrupar progresos por registro_id
        progresos_por_registro = {}
        for p in progresos_list:
            if p.registro_id not in progresos_por_registro:
                progresos_por_registro[p.registro_id] = []
            progresos_por_registro[p.registro_id].append(p)
    else:
        progresos_por_registro = {}

    # Generar respuesta para cada día del mes
    resultado = []

    fecha_actual = primer_dia
    while fecha_actual <= ultimo_dia:
        fecha_str = fecha_actual.strftime("%Y-%m-%d")

        # Calcular día de la semana
        dia_letra = obtener_dia_letra(fecha_actual)

        # Contar hábitos programados para este día
        habitos_del_dia = []
        for habito in habitos_usuario:
            # Solo considerar el hábito si ya existía en esta fecha
            if habito.created_at.date() > fecha_actual:
                continue
            
            try:
                dias_habito = parsear_dias_habito(habito.dias)

                if dia_letra in dias_habito:
                    habitos_del_dia.append(habito.id)

            except ValueError as e:
                # Log del error pero continuar con otros hábitos
                logger.warning(
                    f"Error parseando días del hábito {habito.id} en calendario: {e}. "
                    f"Saltando este hábito."
                )
                continue

        total_habitos = len(habitos_del_dia)

        # Verificar si hay registro para este día
        registro = registros_mes.get(fecha_str)
        tiene_registro = registro is not None

        # Contar hábitos completados
        habitos_completados = 0
        if registro and registro.id in progresos_por_registro:
            progresos = progresos_por_registro[registro.id]
            habitos_completados = sum(1 for p in progresos if p.completado)

        # Calcular porcentaje
        porcentaje = (habitos_completados / total_habitos * 100) if total_habitos > 0 else 0

        resultado.append(ProgresoDiaCalendario(
            fecha=fecha_str,
            total_habitos=total_habitos,
            habitos_completados=habitos_completados,
            porcentaje=round(porcentaje, 1),
            tiene_registro=tiene_registro
        ))

        fecha_actual += timedelta(days=1)

    return resultado


@router.get("/calendario/{year}/{month}/habito/{habito_id}", response_model=List[ProgresoHabitoDiaCalendario])
async def get_progreso_mes_habito(
    year: int,
    month: int,
    habito_id: int,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el progreso de un hábito específico para cada día del mes.

    Args:
        year: Año del calendario
        month: Mes del calendario (1-12)
        habito_id: ID del hábito a consultar
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Lista con progreso diario del hábito en el mes
    """
    import calendar
    from datetime import timedelta

    # Validar mes
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Mes inválido. Debe estar entre 1 y 12")

    # Verificar que el hábito pertenece al usuario
    habito_result = await db.execute(
        select(habitos).where(
            and_(
                habitos.id == habito_id,
                habitos.usuario_id == current_user.id
            )
        )
    )
    habito = habito_result.scalar_one_or_none()
    
    if not habito:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")

    # Calcular primer y último día del mes
    primer_dia = date(year, month, 1)
    _, ultimo_dia_mes = calendar.monthrange(year, month)
    ultimo_dia = date(year, month, ultimo_dia_mes)

    # Parsear días del hábito
    try:
        dias_habito = parsear_dias_habito(habito.dias)
    except ValueError as e:
        logger.error(f"Error parseando días del hábito {habito_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar los días del hábito")

    # Obtener todos los registros del mes
    registros_result = await db.execute(
        select(registros).where(
            and_(
                registros.usuario_id == current_user.id,
                registros.fecha >= primer_dia.strftime("%Y-%m-%d"),
                registros.fecha <= ultimo_dia.strftime("%Y-%m-%d")
            )
        )
    )
    registros_mes = {r.fecha: r for r in registros_result.scalars().all()}

    # Obtener progresos del hábito específico
    progresos_por_fecha = {}
    if registros_mes:
        registro_ids = [r.id for r in registros_mes.values()]
        progresos_result = await db.execute(
            select(progreso_habitos).where(
                and_(
                    progreso_habitos.registro_id.in_(registro_ids),
                    progreso_habitos.habito_id == habito_id
                )
            )
        )
        for p in progresos_result.scalars().all():
            # Encontrar la fecha del registro
            for fecha, reg in registros_mes.items():
                if reg.id == p.registro_id:
                    progresos_por_fecha[fecha] = p
                    break

    # Generar respuesta para cada día del mes
    resultado = []
    fecha_actual = primer_dia

    while fecha_actual <= ultimo_dia:
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        dia_letra = obtener_dia_letra(fecha_actual)
        
        # Verificar si el hábito está programado para este día
        programado = dia_letra in dias_habito and habito.created_at.date() <= fecha_actual
        
        # Verificar si fue completado
        progreso = progresos_por_fecha.get(fecha_str)
        completado = progreso.completado if progreso else False

        resultado.append(ProgresoHabitoDiaCalendario(
            fecha=fecha_str,
            completado=completado,
            programado=programado
        ))

        fecha_actual += timedelta(days=1)

    return resultado
