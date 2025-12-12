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

El proyecto usa SQLite con SQLAlchemy asíncrono. La base de datos se crea automáticamente al iniciar la aplicación.

### Modelos principales:
- **usuarios** - Usuarios del sistema
- **categorias** - Categorías de hábitos
- **habitos** - Hábitos de los usuarios
- **registros** - Registros diarios
- **progreso_habitos** - Progreso de hábitos por día
- **habito_dias** - Días específicos de hábitos
