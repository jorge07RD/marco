from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


# ==================== Usuario Schemas ====================
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    ver_futuro: bool = False
    notificaciones_activas: bool = False
    hora_recordatorio: str = "08:00"
    timezone: str = "America/Santo_Domingo"


class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    contrasena: Optional[str] = Field(None, min_length=6)
    ver_futuro: Optional[bool] = None
    notificaciones_activas: Optional[bool] = None
    hora_recordatorio: Optional[str] = None
    timezone: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Categoria Schemas ====================
class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)


class CategoriaResponse(CategoriaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Habito Schemas ====================
class HabitoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    categoria_id: int
    usuario_id: int
    unidad_medida: str = Field(..., max_length=50)
    meta_diaria: float
    dias: str  # JSON string: '["L", "M", "X"]'
    color: str = Field(..., max_length=20)
    activo: int = Field(default=1)


class HabitoCreate(BaseModel):
    """Esquema para creación de hábito (sin usuario_id, se toma del token)."""
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    categoria_id: int
    unidad_medida: str = Field(..., max_length=50)
    meta_diaria: float
    dias: str  # JSON string: '["L", "M", "X"]'
    color: str = Field(..., max_length=20)
    activo: int = Field(default=1)


class HabitoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    unidad_medida: Optional[str] = Field(None, max_length=50)
    meta_diaria: Optional[float] = None
    dias: Optional[str] = None
    color: Optional[str] = Field(None, max_length=20)
    activo: Optional[int] = None


class HabitoResponse(HabitoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Registro Schemas ====================
class RegistroBase(BaseModel):
    usuario_id: int
    fecha: str  # Formato: YYYY-MM-DD
    notas: Optional[str] = None


class RegistroCreate(BaseModel):
    usuario_id: int
    fecha: str  # Formato: YYYY-MM-DD
    notas: Optional[str] = None


class RegistroUpdate(BaseModel):
    notas: Optional[str] = None


class RegistroResponse(RegistroBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== ProgresoHabito Schemas ====================
class ProgresoHabitoBase(BaseModel):
    registro_id: int
    habito_id: int
    valor: float = 0
    completado: bool = False


class ProgresoHabitoCreate(BaseModel):
    habito_id: int
    valor: float = 0
    completado: bool = False


class ProgresoHabitoUpdate(BaseModel):
    valor: Optional[float] = None
    completado: Optional[bool] = None


class ProgresoHabitoResponse(ProgresoHabitoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Registro con Progresos ====================
class RegistroConProgresos(RegistroResponse):
    progresos: list[ProgresoHabitoResponse] = []


# ==================== RegistroHabitoDias Schemas ====================
class RegistroHabitoDiaBase(BaseModel):
    registro_id: int
    habito_dia_id: int


class RegistroHabitoDiaCreate(RegistroHabitoDiaBase):
    pass


class RegistroHabitoDiaResponse(RegistroHabitoDiaBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== HabitoDia Schemas ====================
class HabitoDiaBase(BaseModel):
    habito_id: int
    estado: bool = False


class HabitoDiaCreate(HabitoDiaBase):
    pass


class HabitoDiaUpdate(BaseModel):
    estado: Optional[bool] = None


class HabitoDiaResponse(HabitoDiaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Schemas con relaciones ====================
class RegistroConHabitoDias(RegistroResponse):
    habito_dias: list[HabitoDiaResponse] = []


class HabitoConCategoria(HabitoResponse):
    categoria: Optional[CategoriaResponse] = None


class UsuarioConHabitos(UsuarioResponse):
    habitos: list[HabitoResponse] = []


# ==================== Auth Schemas ====================
class LoginRequest(BaseModel):
    """Esquema para solicitud de login."""
    identifier: str = Field(..., min_length=1, description="Nombre de usuario o email")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identifier": "jorge@jorge.com",
                "password": "12345678"
            }
        }
    )


class RegisterRequest(BaseModel):
    """Esquema para solicitud de registro."""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Email único del usuario")
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")
    ver_futuro: bool = Field(default=False, description="Permite ver fechas futuras")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan@example.com",
                "password": "MiPassword123",
                "ver_futuro": False
            }
        }
    )


class TokenResponse(BaseModel):
    """Esquema de respuesta con token de acceso."""
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    user: UsuarioResponse = Field(..., description="Datos del usuario autenticado")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "nombre": "Juan Pérez",
                    "email": "juan@example.com",
                    "ver_futuro": False,
                    "created_at": "2025-12-10T10:00:00",
                    "updated_at": None
                }
            }
        }
    )


# ==================== Analytics Schemas ====================
class RendimientoDiaResponse(BaseModel):
    """Esquema para rendimiento por día."""
    fecha: str
    habitos: int
    habitos_completados: int

    model_config = ConfigDict(from_attributes=True)


class CumplimientoHabitoResponse(BaseModel):
    """Esquema para cumplimiento de hábitos por categoría."""
    fecha: str
    nombre_habito: str
    habitos_completados: int
    total_habitos: int
    color: str

    model_config = ConfigDict(from_attributes=True)


# ==================== Calendario Schemas ====================
class ProgresoDiaCalendario(BaseModel):
    """Esquema para mostrar progreso de un día en el calendario."""
    fecha: str  # Formato YYYY-MM-DD
    total_habitos: int  # Total de hábitos programados para ese día
    habitos_completados: int  # Hábitos completados
    porcentaje: float  # Porcentaje de completitud (0-100)
    tiene_registro: bool  # Si existe un registro para ese día

    model_config = ConfigDict(from_attributes=True)


class ProgresoHabitoDiaCalendario(BaseModel):
    """Esquema para mostrar si un hábito específico fue completado en un día."""
    fecha: str  # Formato YYYY-MM-DD
    completado: bool  # Si el hábito fue completado ese día
    programado: bool  # Si el hábito estaba programado para ese día

    model_config = ConfigDict(from_attributes=True)


# ==================== Push Notifications Schemas ====================
class PushSubscriptionCreate(BaseModel):
    """Esquema para crear una suscripción push."""
    endpoint: str = Field(..., description="URL del endpoint push del navegador")
    p256dh_key: str = Field(..., description="Clave pública del cliente")
    auth_key: str = Field(..., description="Token de autenticación")
    user_agent: Optional[str] = Field(None, description="User agent del navegador")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "endpoint": "https://fcm.googleapis.com/fcm/send/...",
                "p256dh_key": "BNcR...",
                "auth_key": "tBH...",
                "user_agent": "Mozilla/5.0..."
            }
        }
    )


class PushSubscriptionResponse(BaseModel):
    """Esquema de respuesta para suscripción push."""
    id: int
    usuario_id: int
    endpoint: str
    activa: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationPreferencesUpdate(BaseModel):
    """Esquema para actualizar preferencias de notificación."""
    notificaciones_activas: Optional[bool] = None
    hora_recordatorio: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    timezone: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "notificaciones_activas": True,
                "hora_recordatorio": "09:00",
                "timezone": "America/Santo_Domingo"
            }
        }
    )


class NotificationPreferencesResponse(BaseModel):
    """Esquema de respuesta para preferencias de notificación."""
    notificaciones_activas: bool
    hora_recordatorio: str
    timezone: str

    model_config = ConfigDict(from_attributes=True)


class TestNotificationRequest(BaseModel):
    """Esquema para enviar notificación de prueba."""
    title: Optional[str] = Field("Prueba de notificación", description="Título de la notificación")
    body: Optional[str] = Field("¡Las notificaciones funcionan correctamente!", description="Cuerpo de la notificación")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Prueba",
                "body": "Esta es una notificación de prueba"
            }
        }
    )


class VapidPublicKeyResponse(BaseModel):
    """Esquema de respuesta para la clave pública VAPID."""
    public_key: str = Field(..., description="Clave pública VAPID para suscripción push")
