# Backend API

API REST construida con FastAPI, SQLite asíncrono, Pydantic y UV.

## Requisitos

- Python 3.11+
- UV (gestor de paquetes)

## Instalación

```bash
# Instalar UV si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Crear entorno virtual e instalar dependencias
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

## Endpoints

### Items
- `GET /api/items` - Listar items
- `GET /api/items/{id}` - Obtener item
- `POST /api/items` - Crear item
- `PUT /api/items/{id}` - Actualizar item
- `DELETE /api/items/{id}` - Eliminar item

### Charts
- `GET /api/charts/data` - Obtener datos de gráficos
- `GET /api/charts/series` - Listar series disponibles
- `GET /api/charts/series/{name}` - Obtener datos de una serie
- `POST /api/charts/data` - Crear dato de gráfico
- `POST /api/charts/data/bulk` - Crear múltiples datos
- `DELETE /api/charts/data/{id}` - Eliminar dato
- `DELETE /api/charts/series/{name}` - Eliminar serie completa
