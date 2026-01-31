from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, func
from app.database import Base


class usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    contrasena = Column(String, nullable=False)
    ver_futuro = Column(Boolean, default=False)  # Permite ver fechas futuras
    # Campos de notificaciones push (nombres de columnas existentes en la BD)
    notificaciones_activas = Column(Boolean, default=False)
    recordatorios_activos = Column(Boolean, default=False)
    hora_recordatorio = Column(String, default="08:00")  # Formato HH:MM
    timezone = Column(String, default="America/Santo_Domingo")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class categorias(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class habitos(Base):
    __tablename__ = "habitos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    descripcion = Column(String, nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    unidad_medida = Column(String, nullable=False)
    meta_diaria = Column(Float, nullable=False)
    dias = Column(String, nullable=False)  # Store as JSON string
    color = Column(String, nullable=False)
    activo = Column(Integer, default=1)  # 1 for True, 0 for False
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class registros(Base):
    """Registro diario único por usuario y fecha"""
    __tablename__ = "registros"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha = Column(String, nullable=False)  # Formato: YYYY-MM-DD
    notas = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint: un registro por usuario por día
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class progreso_habitos(Base):
    """Progreso de cada hábito dentro de un registro diario"""
    __tablename__ = "progreso_habitos"

    id = Column(Integer, primary_key=True, index=True)
    registro_id = Column(Integer, ForeignKey("registros.id"), nullable=False)
    habito_id = Column(Integer, ForeignKey("habitos.id"), nullable=False)
    valor = Column(Float, default=0)  # Valor actual del progreso
    completado = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class registro_habito_dias(Base):
    """Tabla intermedia para relación muchos a muchos entre registros y habito_dias"""
    __tablename__ = "registro_habito_dias"

    id = Column(Integer, primary_key=True, index=True)
    registro_id = Column(Integer, ForeignKey("registros.id"), nullable=False)
    habito_dia_id = Column(Integer, ForeignKey("habito_dias.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class habito_dias(Base):
    __tablename__ = "habito_dias"

    id = Column(Integer, primary_key=True, index=True)
    habito_id = Column(Integer, ForeignKey("habitos.id"), nullable=False)
    estado = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class push_subscriptions(Base):
    """Suscripciones push para notificaciones del navegador"""
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    endpoint = Column(String, nullable=False, unique=True)
    p256dh_key = Column(String, nullable=False)  # Clave pública del cliente
    auth_key = Column(String, nullable=False)  # Token de autenticación
    user_agent = Column(String, nullable=True)  # Navegador/dispositivo
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())