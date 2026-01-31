# Backend API

API REST construida con FastAPI, SQLite asíncrono, Pydantic y **UV** para gestión de hábitos y análisis de progreso.

## Requisitos

- Python 3.11+
- [UV](https://github.com/astral-sh/uv) (gestor de paquetes Python ultrarrápido)

## Instalación

```bash
# Instalar UV si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependencias (esto crea el venv automáticamente)
uv sync

# Copiar archivo de configuración
cp .env.example .env
```

## Ejecutar

```bash
# Modo desarrollo
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints Principales

### 🔐 Autenticación
- `POST /api/auth/register` - Registrar nuevo usuario
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Obtener usuario actual

### 👤 Usuarios
- `GET /api/usuarios/` - Listar usuarios
- `GET /api/usuarios/{id}` - Obtener usuario
- `POST /api/usuarios/` - Crear usuario
- `PUT /api/usuarios/{id}` - Actualizar usuario
- `DELETE /api/usuarios/{id}` - Eliminar usuario

### 📁 Categorías
- `GET /api/categorias/` - Listar categorías
- `GET /api/categorias/{id}` - Obtener categoría
- `POST /api/categorias/` - Crear categoría
- `PUT /api/categorias/{id}` - Actualizar categoría
- `DELETE /api/categorias/{id}` - Eliminar categoría

### 🎯 Hábitos (Protegido)
- `GET /api/habitos/` - Listar hábitos del usuario autenticado
- `GET /api/habitos/{id}` - Obtener hábito
- `POST /api/habitos/` - Crear hábito
- `PUT /api/habitos/{id}` - Actualizar hábito
- `DELETE /api/habitos/{id}` - Eliminar hábito

### 📊 Registros (Protegido)
- `GET /api/registros/` - Listar registros del usuario
- `GET /api/registros/fecha/{fecha}` - Obtener/crear registro para fecha específica
- `PUT /api/registros/progreso/{progreso_id}` - Actualizar progreso de hábito
- `POST /api/registros/progreso/toggle/{progreso_id}` - Alternar estado completado

### 📈 Análisis (Protegido)
- `GET /api/analisis/rendimiento?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD` - Obtener rendimiento por día
- `GET /api/analisis/cumplimiento?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD` - Obtener cumplimiento de hábitos

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal FastAPI
│   ├── config.py            # Configuración desde variables de entorno
│   ├── database.py          # Configuración de base de datos
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Esquemas Pydantic
│   ├── security.py          # JWT y autenticación
│   └── routers/
│       ├── auth.py          # Endpoints de autenticación
│       ├── usuarios.py      # CRUD de usuarios
│       ├── categorias.py    # CRUD de categorías
│       ├── habitos.py       # CRUD de hábitos
│       ├── registros.py     # CRUD de registros
│       ├── habito_dias.py   # Gestión de días de hábitos
│       └── analisis.py      # Endpoints de análisis y reportes
├── migrations/              # Migraciones de Alembic
│   ├── env.py               # Configuración del entorno
│   └── versions/            # Archivos de migración
├── alembic.ini              # Configuración de Alembic
├── app.db                   # Base de datos SQLite
└── .env                     # Variables de entorno
```

## Autenticación

Todos los endpoints protegidos requieren un token JWT en el header:
```
Authorization: Bearer {token}
```

Ver [AUTENTICACION.md](../AUTENTICACION.md) para más detalles.

## Base de Datos

El proyecto usa SQLite con SQLAlchemy asíncrono y **Alembic** para migraciones.

### Modelos principales:
- **usuarios** - Usuarios del sistema
- **categorias** - Categorías de hábitos
- **habitos** - Hábitos de los usuarios
- **registros** - Registros diarios
- **progreso_habitos** - Progreso de hábitos por día
- **habito_dias** - Días específicos de hábitos

## Migraciones con Alembic

El proyecto usa Alembic para gestionar cambios en el esquema de la base de datos.

### Comandos principales

```bash
# Ver versión actual de la base de datos
uv run alembic current

# Ver historial de migraciones
uv run alembic history

# Aplicar todas las migraciones pendientes
uv run alembic upgrade head

# Revertir la última migración
uv run alembic downgrade -1

# Crear nueva migración automática (detecta cambios en models.py)
uv run alembic revision --autogenerate -m "descripcion_del_cambio"

# Crear migración manual vacía
uv run alembic revision -m "descripcion_del_cambio"
```

### Flujo de trabajo para cambios de esquema

1. Modifica los modelos en `app/models.py`
2. Genera la migración: `uv run alembic revision --autogenerate -m "descripcion"`
3. Revisa el archivo generado en `migrations/versions/`
4. Aplica la migración: `uv run alembic upgrade head`

### Estructura de migraciones

```
backend/
├── alembic.ini              # Configuración de Alembic
├── migrations/
│   ├── env.py               # Configuración del entorno (conecta con app/)
│   ├── script.py.mako       # Template para nuevas migraciones
│   └── versions/            # Archivos de migración
│       └── xxxx_descripcion.py
```

### Producción

En Docker, las migraciones se ejecutan automáticamente al iniciar el contenedor con `alembic upgrade head`.
