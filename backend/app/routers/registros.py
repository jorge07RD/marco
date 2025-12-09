from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import date, datetime

from app.database import get_db
from app.models import registros, progreso_habitos, usuario, habitos
from app.schemas import (
    RegistroCreate, RegistroUpdate, RegistroResponse, RegistroConProgresos,
    ProgresoHabitoCreate, ProgresoHabitoUpdate, ProgresoHabitoResponse
)

router = APIRouter(prefix="/registros", tags=["registros"])


@router.get("/", response_model=List[RegistroResponse])
async def get_registros(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Obtiene la lista de todos los registros."""
    result = await db.execute(select(registros).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/usuario/{usuario_id}", response_model=List[RegistroResponse])
async def get_registros_by_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene todos los registros de un usuario específico."""
    result = await db.execute(select(registros).where(registros.usuario_id == usuario_id))
    return result.scalars().all()


@router.get("/usuario/{usuario_id}/fecha/{fecha}", response_model=RegistroConProgresos)
async def get_or_create_registro_por_fecha(
    usuario_id: int, 
    fecha: str,  # Formato: YYYY-MM-DD
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el registro de un usuario para una fecha específica.
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
        # Verificar si el usuario puede ver el futuro
        user_result = await db.execute(select(usuario).where(usuario.id == usuario_id))
        db_usuario = user_result.scalar_one_or_none()
        if not db_usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if not db_usuario.ver_futuro:
            raise HTTPException(
                status_code=403, 
                detail="No puedes ver fechas futuras. Activa 'Ver futuro' en configuración."
            )
    
    # Buscar registro existente
    result = await db.execute(
        select(registros).where(
            and_(registros.usuario_id == usuario_id, registros.fecha == fecha)
        )
    )
    db_registro = result.scalar_one_or_none()
    
    # Si no existe, crear uno nuevo
    if not db_registro:
        db_registro = registros(usuario_id=usuario_id, fecha=fecha)
        db.add(db_registro)
        await db.flush()
        
        # Obtener hábitos activos del usuario para ese día de la semana
        dias_semana = ['D', 'L', 'M', 'X', 'J', 'V', 'S']
        dia_letra = dias_semana[fecha_obj.weekday() + 1] if fecha_obj.weekday() < 6 else dias_semana[0]
        
        habitos_result = await db.execute(
            select(habitos).where(
                and_(habitos.usuario_id == usuario_id, habitos.activo == 1)
            )
        )
        habitos_usuario = habitos_result.scalars().all()
        
        # Crear progreso para cada hábito activo ese día
        for habito in habitos_usuario:
            try:
                dias_habito = eval(habito.dias)  # Parse JSON string
                if dia_letra in dias_habito:
                    progreso = progreso_habitos(
                        registro_id=db_registro.id,
                        habito_id=habito.id,
                        valor=0,
                        completado=False
                    )
                    db.add(progreso)
            except:
                pass
        
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
    db: AsyncSession = Depends(get_db)
):
    """Actualiza el progreso de un hábito específico."""
    result = await db.execute(
        select(progreso_habitos).where(progreso_habitos.id == progreso_id)
    )
    db_progreso = result.scalar_one_or_none()
    if not db_progreso:
        raise HTTPException(status_code=404, detail="Progreso no encontrado")
    
    update_data = progreso_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_progreso, key, value)
    
    await db.commit()
    await db.refresh(db_progreso)
    return db_progreso


@router.post("/progreso/toggle/{progreso_id}", response_model=ProgresoHabitoResponse)
async def toggle_progreso(progreso_id: int, db: AsyncSession = Depends(get_db)):
    """Alterna el estado de completado de un progreso."""
    result = await db.execute(
        select(progreso_habitos).where(progreso_habitos.id == progreso_id)
    )
    db_progreso = result.scalar_one_or_none()
    if not db_progreso:
        raise HTTPException(status_code=404, detail="Progreso no encontrado")
    
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
async def get_registro(registro_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene un registro específico por su ID."""
    result = await db.execute(select(registros).where(registros.id == registro_id))
    db_registro = result.scalar_one_or_none()
    if not db_registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return db_registro


@router.put("/{registro_id}", response_model=RegistroResponse)
async def update_registro(registro_id: int, registro_data: RegistroUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza las notas de un registro."""
    result = await db.execute(select(registros).where(registros.id == registro_id))
    db_registro = result.scalar_one_or_none()
    if not db_registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    
    update_data = registro_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_registro, key, value)
    
    await db.commit()
    await db.refresh(db_registro)
    return db_registro


@router.delete("/{registro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registro(registro_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina un registro del sistema por su ID."""
    result = await db.execute(select(registros).where(registros.id == registro_id))
    db_registro = result.scalar_one_or_none()
    if not db_registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    
    await db.delete(db_registro)
    await db.commit()
