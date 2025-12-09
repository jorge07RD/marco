from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


# ==================== Usuario Schemas ====================
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    ver_futuro: bool = False


class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    contrasena: Optional[str] = Field(None, min_length=6)
    ver_futuro: Optional[bool] = None


class UsuarioResponse(UsuarioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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


class HabitoCreate(HabitoBase):
    pass


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


# ==================== Schemas con relaciones ====================
class RegistroConHabitoDias(RegistroResponse):
    habito_dias: list[HabitoDiaResponse] = []


class HabitoConCategoria(HabitoResponse):
    categoria: Optional[CategoriaResponse] = None


class UsuarioConHabitos(UsuarioResponse):
    habitos: list[HabitoResponse] = []
