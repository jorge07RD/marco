# Guía de Integración de Redis en Marco

## Resumen Ejecutivo

**Nivel de Complejidad:** MODERADO (2-4 horas de desarrollo + 1-2 horas de testing)

**Beneficio Principal:** Optimización significativa de endpoints de análisis que ejecutan múltiples queries complejas.

---

## Estado Actual del Proyecto

### Backend
- **Framework:** FastAPI con AsyncIO
- **Base de datos:** SQLite con SQLAlchemy AsyncIO
- **Autenticación:** JWT (tokens de 7 días)
- **Caché actual:** Solo `@lru_cache` para configuración (`config.py:33`)

### Arquitectura Preparada
✅ Ya usa AsyncIO completo → Compatible con `aioredis`
✅ Pattern de inyección de dependencias → Fácil agregar Redis como dependencia
✅ Código organizado por routers → Puntos claros de integración

---

## Endpoints Prioritarios para Caché

| Endpoint | Archivo | Línea | Beneficio | TTL Sugerido |
|----------|---------|-------|-----------|--------------|
| `GET /api/analisis/rendimiento` | `routers/analisis.py` | 23 | 🔥 MUY ALTO | 1 hora |
| `GET /api/analisis/cumplimiento` | `routers/analisis.py` | 89 | 🔥 MUY ALTO | 1 hora |
| `GET /api/categorias/` | `routers/categorias.py` | 12 | 🟡 MEDIO | 24 horas |
| `GET /api/habitos/` | `routers/habitos.py` | 17 | 🟢 BAJO | 15 minutos |

**Razón:** Los endpoints de análisis ejecutan múltiples queries para calcular métricas de rendimiento y cumplimiento, lo que los hace candidatos perfectos para caché.

---

## Plan de Implementación

### Paso 1: Instalar Redis

#### Opción A: Docker (Recomendado para desarrollo)
```bash
docker run -d \
  --name redis-marco \
  -p 6379:6379 \
  redis:7-alpine
```

#### Opción B: Instalación local
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# macOS
brew install redis

# Iniciar servicio
redis-server
```

#### Verificar instalación
```bash
redis-cli ping
# Debe responder: PONG
```

---

### Paso 2: Agregar Dependencia de Python

Editar `backend/pyproject.toml`:

```toml
[project]
dependencies = [
    # ... dependencias existentes ...
    "redis>=5.0.0",
]
```

Instalar:
```bash
cd backend
uv sync
```

---

### Paso 3: Configuración de Redis

#### 3.1. Actualizar `backend/app/config.py`

Añadir después de la línea 15 (después de `DATABASE_URL`):

```python
class Settings(BaseSettings):
    # ... campos existentes ...

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL_DEFAULT: int = 3600  # 1 hora en segundos
    REDIS_TTL_ANALYTICS: int = 3600  # 1 hora para análisis
    REDIS_TTL_CATEGORIES: int = 86400  # 24 horas para categorías
    REDIS_TTL_HABITS: int = 900  # 15 minutos para hábitos
    REDIS_ENABLED: bool = True  # Permitir desactivar en desarrollo
```

#### 3.2. Actualizar `backend/.env`

Añadir al final del archivo:

```bash
# REDIS
REDIS_URL=redis://localhost:6379/0
REDIS_TTL_DEFAULT=3600
REDIS_TTL_ANALYTICS=3600
REDIS_TTL_CATEGORIES=86400
REDIS_TTL_HABITS=900
REDIS_ENABLED=true
```

---

### Paso 4: Crear Módulo de Caché

Crear nuevo archivo `backend/app/cache.py`:

```python
"""
Sistema de caché con Redis para optimizar consultas frecuentes.
"""
import json
import hashlib
from typing import Any, Optional
from functools import wraps
import redis.asyncio as redis
from fastapi import Request

from .config import get_settings

settings = get_settings()

# Cliente Redis global (se inicializa en startup)
redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Inicializar conexión a Redis."""
    global redis_client
    if settings.REDIS_ENABLED:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        try:
            await redis_client.ping()
            print("✅ Redis conectado exitosamente")
        except Exception as e:
            print(f"⚠️  Redis no disponible: {e}")
            redis_client = None


async def close_redis():
    """Cerrar conexión a Redis."""
    global redis_client
    if redis_client:
        await redis_client.close()
        print("Redis desconectado")


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generar clave de caché única basada en parámetros.

    Args:
        prefix: Prefijo identificador (ej: "analisis:rendimiento")
        *args, **kwargs: Parámetros que afectan el resultado

    Returns:
        Clave de caché en formato "prefix:hash"
    """
    # Crear string único con todos los parámetros
    params_str = json.dumps([args, sorted(kwargs.items())], sort_keys=True)
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
    return f"{prefix}:{params_hash}"


async def get_cached(key: str) -> Optional[Any]:
    """
    Obtener valor del caché.

    Args:
        key: Clave de caché

    Returns:
        Valor deserializado o None si no existe
    """
    if not redis_client:
        return None

    try:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        print(f"Error obteniendo caché {key}: {e}")

    return None


async def set_cached(key: str, value: Any, ttl: int = None) -> bool:
    """
    Guardar valor en caché.

    Args:
        key: Clave de caché
        value: Valor a cachear (debe ser serializable a JSON)
        ttl: Tiempo de vida en segundos (usa default si no se especifica)

    Returns:
        True si se guardó exitosamente
    """
    if not redis_client:
        return False

    if ttl is None:
        ttl = settings.REDIS_TTL_DEFAULT

    try:
        serialized = json.dumps(value, default=str)
        await redis_client.setex(key, ttl, serialized)
        return True
    except Exception as e:
        print(f"Error guardando caché {key}: {e}")
        return False


async def delete_cached(pattern: str) -> int:
    """
    Eliminar claves de caché que coincidan con un patrón.

    Args:
        pattern: Patrón de Redis (ej: "user:123:*")

    Returns:
        Número de claves eliminadas
    """
    if not redis_client:
        return 0

    try:
        keys = await redis_client.keys(pattern)
        if keys:
            return await redis_client.delete(*keys)
    except Exception as e:
        print(f"Error eliminando caché {pattern}: {e}")

    return 0


def cached_endpoint(prefix: str, ttl: int = None):
    """
    Decorador para cachear respuestas de endpoints.

    Usage:
        @router.get("/data")
        @cached_endpoint("data", ttl=3600)
        async def get_data(user_id: int):
            ...

    Args:
        prefix: Prefijo para la clave de caché
        ttl: Tiempo de vida en segundos
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generar clave única basada en argumentos
            cache_key = generate_cache_key(prefix, *args, **kwargs)

            # Intentar obtener del caché
            cached_value = await get_cached(cache_key)
            if cached_value is not None:
                return cached_value

            # Ejecutar función original
            result = await func(*args, **kwargs)

            # Guardar en caché
            await set_cached(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


async def invalidate_user_cache(user_id: int):
    """
    Invalidar todo el caché relacionado con un usuario.

    Args:
        user_id: ID del usuario
    """
    patterns = [
        f"analisis:*:user:{user_id}:*",
        f"habitos:user:{user_id}:*",
        f"registros:user:{user_id}:*",
    ]

    for pattern in patterns:
        deleted = await delete_cached(pattern)
        if deleted > 0:
            print(f"Invalidadas {deleted} claves de caché: {pattern}")
```

---

### Paso 5: Integrar Redis en el Ciclo de Vida de FastAPI

Editar `backend/app/main.py`, añadir después de la línea 30 (después de `create_tables()`):

```python
from .cache import init_redis, close_redis

@app.on_event("startup")
async def startup():
    await create_tables()
    await init_redis()  # 👈 Nuevo

@app.on_event("shutdown")
async def shutdown():
    await close_redis()  # 👈 Nuevo
```

---

### Paso 6: Implementar Caché en Endpoints

#### 6.1. Análisis de Rendimiento

Editar `backend/app/routers/analisis.py`, añadir import al inicio:

```python
from ..cache import cached_endpoint, invalidate_user_cache
from ..config import get_settings

settings = get_settings()
```

Modificar el endpoint de rendimiento (línea 23):

```python
@router.get("/rendimiento")
@cached_endpoint(
    prefix="analisis:rendimiento",
    ttl=settings.REDIS_TTL_ANALYTICS
)
async def obtener_analisis_rendimiento(
    fecha_inicio: str,
    fecha_fin: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Análisis de rendimiento diario en un rango de fechas.

    CACHEABLE: Resultados se cachean por 1 hora.
    """
    # ... código existente sin cambios ...
```

#### 6.2. Análisis de Cumplimiento

Modificar el endpoint de cumplimiento (línea 89):

```python
@router.get("/cumplimiento")
@cached_endpoint(
    prefix="analisis:cumplimiento",
    ttl=settings.REDIS_TTL_ANALYTICS
)
async def obtener_analisis_cumplimiento(
    fecha_inicio: str,
    fecha_fin: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Análisis de cumplimiento por hábito.

    CACHEABLE: Resultados se cachean por 1 hora.
    """
    # ... código existente sin cambios ...
```

#### 6.3. Listado de Categorías

Editar `backend/app/routers/categorias.py`:

```python
from ..cache import cached_endpoint
from ..config import get_settings

settings = get_settings()

@router.get("/")
@cached_endpoint(
    prefix="categorias:list",
    ttl=settings.REDIS_TTL_CATEGORIES
)
async def obtener_categorias(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todas las categorías disponibles."""
    # ... código existente sin cambios ...
```

#### 6.4. Listado de Hábitos

Editar `backend/app/routers/habitos.py`:

```python
from ..cache import cached_endpoint, invalidate_user_cache
from ..config import get_settings

settings = get_settings()

@router.get("/")
@cached_endpoint(
    prefix="habitos:list",
    ttl=settings.REDIS_TTL_HABITS
)
async def obtener_habitos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener todos los hábitos del usuario."""
    # ... código existente sin cambios ...
```

---

### Paso 7: Invalidación de Caché

Para mantener los datos actualizados, debemos invalidar el caché cuando se crean/actualizan/eliminan datos.

#### 7.1. Invalidar al Crear Hábito

En `backend/app/routers/habitos.py`, endpoint de creación (línea ~40):

```python
@router.post("/", response_model=HabitoRead)
async def crear_habito(
    habito: HabitoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crear un nuevo hábito."""
    # ... código existente de creación ...

    # Invalidar caché del usuario
    await invalidate_user_cache(current_user.id)  # 👈 Nuevo

    return db_habito
```

#### 7.2. Invalidar al Actualizar Hábito

En el endpoint de actualización (línea ~70):

```python
@router.put("/{habito_id}", response_model=HabitoRead)
async def actualizar_habito(
    habito_id: int,
    habito_update: HabitoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualizar un hábito existente."""
    # ... código existente de actualización ...

    # Invalidar caché del usuario
    await invalidate_user_cache(current_user.id)  # 👈 Nuevo

    return db_habito
```

#### 7.3. Invalidar al Eliminar Hábito

En el endpoint de eliminación (línea ~100):

```python
@router.delete("/{habito_id}")
async def eliminar_habito(
    habito_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Eliminar un hábito."""
    # ... código existente de eliminación ...

    # Invalidar caché del usuario
    await invalidate_user_cache(current_user.id)  # 👈 Nuevo

    return {"message": "Hábito eliminado"}
```

#### 7.4. Invalidar al Registrar Progreso

En `backend/app/routers/registros.py`, cuando se actualiza progreso:

```python
from ..cache import invalidate_user_cache

# Después de actualizar progreso
await invalidate_user_cache(current_user.id)
```

---

### Paso 8: Testing

#### 8.1. Verificar Conexión

Crear `backend/test_redis.py`:

```python
"""Script de prueba para verificar conexión a Redis."""
import asyncio
from app.cache import init_redis, set_cached, get_cached, delete_cached

async def test_redis():
    print("Inicializando Redis...")
    await init_redis()

    # Test 1: Set y Get
    print("\n1. Test Set/Get")
    key = "test:simple"
    value = {"message": "Hello Redis"}

    success = await set_cached(key, value, ttl=60)
    print(f"   Set: {success}")

    cached = await get_cached(key)
    print(f"   Get: {cached}")
    assert cached == value, "Valor no coincide"

    # Test 2: Delete
    print("\n2. Test Delete")
    deleted = await delete_cached("test:*")
    print(f"   Deleted: {deleted} keys")

    cached = await get_cached(key)
    print(f"   Get after delete: {cached}")
    assert cached is None, "Clave debería estar eliminada"

    print("\n✅ Todos los tests pasaron")

if __name__ == "__main__":
    asyncio.run(test_redis())
```

Ejecutar:
```bash
cd backend
python test_redis.py
```

#### 8.2. Verificar Endpoints Cacheados

```bash
# Terminal 1: Iniciar servidor
cd backend
uvicorn app.main:app --reload

# Terminal 2: Hacer request al endpoint de análisis
curl -X GET "http://localhost:8000/api/analisis/rendimiento?fecha_inicio=2025-01-01&fecha_fin=2025-01-31" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -w "\nTime: %{time_total}s\n"

# Primera request: ~200-500ms (sin caché)
# Segunda request: ~10-50ms (con caché)
```

#### 8.3. Monitorear Redis

```bash
# Ver todas las claves
redis-cli KEYS "*"

# Ver valor de una clave
redis-cli GET "analisis:rendimiento:abc123"

# Ver TTL de una clave
redis-cli TTL "analisis:rendimiento:abc123"

# Limpiar todo el caché
redis-cli FLUSHDB
```

---

## Estructura de Claves de Caché

```
analisis:rendimiento:{hash}      # TTL: 1 hora
analisis:cumplimiento:{hash}     # TTL: 1 hora
categorias:list:{hash}           # TTL: 24 horas
habitos:list:{hash}              # TTL: 15 minutos
habitos:user:{user_id}:*         # Patrón para invalidación
```

---

## Configuración de Producción

### Docker Compose

Crear `docker-compose.yml` en la raíz:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: marco-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-changeme}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  backend:
    build: ./backend
    container_name: marco-backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://:${REDIS_PASSWORD:-changeme}@redis:6379/0
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped

volumes:
  redis_data:
```

### Variables de Entorno Producción

```bash
# .env.production
REDIS_URL=redis://:strong_password_here@redis:6379/0
REDIS_TTL_ANALYTICS=3600
REDIS_ENABLED=true
```

---

## Métricas y Monitoreo

### Endpoint de Health Check

Añadir a `backend/app/main.py`:

```python
from .cache import redis_client

@app.get("/health")
async def health_check():
    """Health check incluyendo estado de Redis."""
    redis_status = "disconnected"

    if redis_client:
        try:
            await redis_client.ping()
            redis_status = "connected"
        except:
            redis_status = "error"

    return {
        "status": "ok",
        "redis": redis_status,
        "timestamp": datetime.now().isoformat()
    }
```

### Estadísticas de Caché

Crear endpoint de admin para ver estadísticas:

```python
@router.get("/admin/cache/stats")
async def cache_stats(
    current_user: Usuario = Depends(get_current_user)
):
    """Ver estadísticas de Redis (solo admin)."""
    if redis_client:
        info = await redis_client.info()
        return {
            "keys": await redis_client.dbsize(),
            "memory": info.get("used_memory_human"),
            "hits": info.get("keyspace_hits"),
            "misses": info.get("keyspace_misses"),
        }
    return {"error": "Redis not available"}
```

---

## Troubleshooting

### Error: "Connection refused"

```bash
# Verificar que Redis esté corriendo
redis-cli ping

# Si no responde, iniciar Redis
redis-server
```

### Error: "Module not found: redis"

```bash
cd backend
uv sync
```

### Caché no se invalida correctamente

```bash
# Limpiar todo el caché manualmente
redis-cli FLUSHDB

# Ver logs del backend
uvicorn app.main:app --reload --log-level debug
```

### Performance no mejora

1. Verificar que `REDIS_ENABLED=true`
2. Verificar que los decoradores `@cached_endpoint` estén aplicados
3. Hacer múltiples requests al mismo endpoint con los mismos parámetros
4. Monitorear con `redis-cli MONITOR`

---

## Próximos Pasos (Opcional)

### 1. Caché de Sesiones JWT
Almacenar tokens invalidados en Redis para logout global.

### 2. Rate Limiting
Usar Redis para limitar requests por usuario/IP.

### 3. Pub/Sub para Notificaciones
Implementar notificaciones en tiempo real.

### 4. Redis Sentinel/Cluster
Alta disponibilidad en producción.

---

## Referencias

- [Redis Python Docs](https://redis.readthedocs.io/en/stable/)
- [FastAPI Async Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)

---

## Checklist de Implementación

- [ ] Instalar Redis
- [ ] Agregar dependencia `redis>=5.0.0`
- [ ] Actualizar `config.py` con settings de Redis
- [ ] Crear `cache.py` con funciones helper
- [ ] Integrar en lifecycle de FastAPI (`main.py`)
- [ ] Aplicar decorador `@cached_endpoint` en análisis
- [ ] Aplicar decorador en categorías
- [ ] Aplicar decorador en hábitos
- [ ] Implementar invalidación en creates/updates/deletes
- [ ] Ejecutar `test_redis.py`
- [ ] Verificar mejora de performance
- [ ] Documentar en README.md
- [ ] Configurar para producción (Docker Compose)

---

**Tiempo estimado total:** 3-6 horas (desarrollo + testing + documentación)

**Impacto esperado:** Reducción de 80-90% en tiempo de respuesta de endpoints de análisis.