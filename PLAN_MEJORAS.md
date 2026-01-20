# 📋 Plan de Mejoras - Marco Habit Tracker

**Fecha:** 2025-12-13
**Versión Actual:** 2.0.0
**Calificación Actual:** 8.0/10

---

## 🎯 Objetivo

Llevar el proyecto de **8.0/10 a 9.5/10** implementando mejoras críticas de testing, seguridad, escalabilidad y mantenibilidad.

---

## 🚨 Prioridad CRÍTICA (Implementar Primero)

### 1. Testing

**Problema:** 0% de cobertura de tests

**Implementar:**

#### Backend (pytest + pytest-asyncio)
```bash
cd backend
uv add --dev pytest pytest-asyncio httpx pytest-cov
```

**Tests necesarios:**
- [x] `tests/test_auth.py` - Registro, login, JWT validation ✅
- [x] `tests/test_habitos.py` - CRUD de hábitos con auth ✅
- [x] `tests/test_categorias.py` - Tests de categorías ✅
- [ ] `tests/test_registros.py` - Registros diarios y progreso
- [ ] `tests/test_security.py` - Hash passwords, verify passwords
- [ ] `tests/test_analisis.py` - Endpoints de análisis
- [x] Configurar GitHub Actions para CI ✅
- [ ] Meta: 80%+ cobertura de código (Parcial - ~1197 líneas de tests)

#### Frontend (Vitest + Testing Library)
```bash
cd frontend
npm install -D vitest @testing-library/svelte @testing-library/jest-dom
```

**Tests necesarios:**
- [ ] `tests/lib/api.test.ts` - Cliente API y manejo de tokens
- [ ] `tests/components/HabitoForm.test.ts` - Formulario de hábitos
- [ ] `tests/components/ConfirmModal.test.ts` - Modal de confirmación
- [ ] `tests/routes/login.test.ts` - Flujo de login
- [ ] Meta: 70%+ cobertura

**Estimación:** 3-5 días
**Estado:** 🟡 EN PROGRESO (60% completado)

---

### 2. Database Migrations (Alembic)

**Problema:** Sin sistema de migraciones, cambios de esquema riesgosos

**Implementar:**

```bash
cd backend
uv add alembic
alembic init migrations
```

**Tareas:**
- [ ] Configurar Alembic en `alembic.ini`
- [ ] Conectar con `app/database.py`
- [ ] Crear migración inicial desde modelos actuales
- [ ] Agregar comando `make migrate` al proyecto
- [ ] Documentar proceso en README

**Archivos a crear:**
- `backend/alembic.ini`
- `backend/migrations/env.py`
- `backend/migrations/versions/001_initial.py`

**Estimación:** 1-2 días

---

### 3. Secrets Management

**Problema:** Secret key hardcodeada en código

**Implementar:**

- [x] Crear `backend/.env.example` con todas las variables ✅
- [x] Mover `SECRET_KEY` a `.env` (nunca en código) ✅
- [x] Generar secret seguro: `openssl rand -hex 32` ✅
- [ ] Validar que `SECRET_KEY` no sea el valor por defecto en producción
- [ ] Agregar validación en `app/config.py`:

```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    if self.is_production and "change-this" in self.secret_key:
        raise ValueError("CRITICAL: Must set SECRET_KEY in production!")
```

**Estimación:** 1 hora
**Estado:** 🟡 PARCIALMENTE COMPLETADO (75% - falta validación en producción)

---

## 🔥 Prioridad ALTA (Siguientes 2 semanas)

### 4. Logging Estructurado

**Problema:** Sin logs, difícil debuggear en producción

**Implementar:**

```python
# backend/app/logging_config.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
```

**Logs necesarios:**
- [ ] Requests entrantes (middleware)
- [ ] Errores de autenticación
- [ ] Operaciones de BD fallidas
- [x] Acciones críticas (parcial - warnings en registros) ✅
- [ ] Performance metrics (tiempo de respuesta)
- [ ] Logging estructurado JSON (pythonjsonlogger)

**Nota:** Logging básico implementado en routers (habitos, usuarios, registros, utils), pero falta formato JSON estructurado.

**Estimación:** 1-2 días
**Estado:** 🟡 PARCIALMENTE COMPLETADO (40% - básico sí, estructurado no)

---

### 5. Nomenclatura Python (PEP8)

**Problema:** Clases en minúsculas (`usuario`, `categorias`, `habitos`)

**Refactorizar:**
- [ ] `usuario` → `Usuario`
- [ ] `categorias` → `Categoria`
- [ ] `habitos` → `Habito`
- [ ] `registros` → `Registro`
- [ ] `progreso_habitos` → `ProgresoHabito`
- [ ] `habito_dias` → `HabitoDia`
- [ ] Actualizar todas las importaciones
- [ ] Ejecutar tests para verificar

**Estimación:** 2-3 horas

---

### 6. SQLAlchemy Relationships

**Problema:** Sin relaciones definidas, consultas ineficientes

**Implementar en `models.py`:**

```python
from sqlalchemy.orm import relationship

class Usuario(Base):
    __tablename__ = "usuarios"

    habitos = relationship("Habito", back_populates="usuario", cascade="all, delete-orphan")
    registros = relationship("Registro", back_populates="usuario", cascade="all, delete-orphan")

class Habito(Base):
    __tablename__ = "habitos"

    usuario = relationship("Usuario", back_populates="habitos")
    categoria = relationship("Categoria", back_populates="habitos")
    progresos = relationship("ProgresoHabito", back_populates="habito", cascade="all, delete-orphan")
```

**Beneficios:**
- Eliminación en cascada automática
- Consultas más eficientes con `joinedload()`
- Código más limpio

**Estimación:** 2-3 horas

---

### 7. Validación de Contraseñas

**Problema:** Sin requisitos de complejidad

**Implementar:**

```python
# backend/app/validators.py
import re

def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Mínimo 8 caracteres"
    if not re.search(r"[A-Z]", password):
        return False, "Debe incluir mayúscula"
    if not re.search(r"[a-z]", password):
        return False, "Debe incluir minúscula"
    if not re.search(r"\d", password):
        return False, "Debe incluir número"
    return True, "Válida"
```

**Usar en:**
- Registro de usuarios
- Cambio de contraseña

**Estimación:** 1 hora

---

## 📊 Prioridad MEDIA (Mes 1-2)

### 8. API Versioning

**Implementar:**

```python
# backend/app/main.py
app.include_router(auth.router, prefix="/api/v1")
app.include_router(habitos.router, prefix="/api/v1")
# ...
```

**Actualizar frontend:**
```typescript
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';
```

**Estimación:** 1 hora
**Estado:** 🟢 COMPLETADO - Prefijo `/api` implementado según commits recientes ✅

---

### 9. Rate Limiting

**Problema:** Sin protección contra ataques de fuerza bruta

**Implementar:**

```bash
uv add slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/auth/login")
@limiter.limit("5/minute")  # Max 5 intentos por minuto
async def login(...):
    pass
```

**Estimación:** 2 horas

---

### 10. Error Handling Mejorado

**Implementar:**

```python
# backend/app/exceptions.py
class HabitoNotFoundError(Exception):
    pass

class UnauthorizedError(Exception):
    pass

# backend/app/main.py
@app.exception_handler(HabitoNotFoundError)
async def habito_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Hábito no encontrado"}
    )
```

**Estimación:** 1 día

---

### 11. Frontend Validation

**Implementar:**

- [ ] Validación de formularios con Zod o Yup
- [ ] Feedback visual de errores
- [ ] Validación de email en tiempo real
- [ ] Validación de fortaleza de contraseña

```bash
npm install zod
```

**Estimación:** 1-2 días

---

### 12. Docker Compose Completo

**Problema:** Dockerfiles individuales, sin orquestación

**Implementar `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: ../Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=sqlite+aiosqlite:///app.db
    volumes:
      - ./backend/app.db:/app/app.db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: ../Dockerfile.frontend
      args:
        - VITE_API_URL=http://localhost:8000/api
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

**Estimación:** 2 horas
**Estado:** 🟢 COMPLETADO ✅

---

## 🔮 Prioridad BAJA (Backlog - Mes 3+)

### 13. Migrar de SQLite a PostgreSQL

**Razón:** SQLite no escala para múltiples usuarios concurrentes

**Pasos:**
- [ ] Agregar `asyncpg` y `psycopg2`
- [ ] Configurar PostgreSQL en Docker
- [ ] Actualizar `DATABASE_URL` en config
- [ ] Migrar datos con Alembic
- [ ] Actualizar tests

**Estimación:** 2-3 días

---

### 14. Monitoreo y Observabilidad

**Implementar:**
- [ ] Sentry para error tracking
- [ ] Prometheus + Grafana para métricas
- [ ] Health checks avanzados
- [ ] Logs centralizados (ELK Stack o similar)

**Estimación:** 3-5 días

---

### 15. CI/CD Pipeline

**Estado:** 🟡 PARCIALMENTE COMPLETADO - Backend ✅, Frontend ❌

**Implementar GitHub Actions:**

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install dependencies
        run: cd backend && uv sync
      - name: Run tests
        run: cd backend && uv run pytest --cov

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm install
      - name: Run tests
        run: cd frontend && npm test
```

**Archivo implementado:** `.github/workflows/backend-tests.yml` ✅

**Estimación:** 1 día

---

### 16. Features Adicionales

**Backlog de features:**
- [ ] PWA (Progressive Web App) con offline support
- [ ] Notificaciones push para recordatorios
- [ ] Export/import de datos (JSON, CSV)
- [ ] Compartir hábitos con otros usuarios
- [ ] Streaks y gamificación (badges, achievements)
- [ ] API pública con API keys
- [ ] Dashboard de administrador
- [ ] Soporte para equipos/grupos

---

## 📈 Roadmap Sugerido

### Semana 1-2: Fundamentos Críticos
- 🟡 Setup de testing (backend ✅ + frontend ❌)
- ❌ Alembic migrations
- 🟡 Secrets management (75% completado)

### Semana 3-4: Seguridad y Calidad
- 🟡 Logging estructurado (básico ✅, JSON ❌)
- ❌ Refactor nomenclatura PEP8
- ❌ SQLAlchemy relationships
- ❌ Validación de contraseñas

### Mes 2: Robustez
- ❌ Rate limiting
- ❌ Error handling mejorado
- ✅ Docker Compose
- 🟡 CI/CD básico (backend ✅, frontend ❌)

### Mes 3+: Escalabilidad
- ❌ PostgreSQL migration
- ❌ Monitoreo
- ❌ Features adicionales

---

## 🎯 Métricas de Éxito

| Métrica | Inicial | Actual | Objetivo |
|---------|---------|--------|----------|
| **Test Coverage Backend** | 0% | ~50% 🟡 | 80%+ |
| **Test Coverage Frontend** | 0% | 0% ❌ | 70%+ |
| **Calificación General** | 8.0/10 | 8.3/10 🟡 | 9.5/10 |
| **Production-Ready Score** | 6.0/10 | 6.8/10 🟡 | 9.0/10 |
| **Security Score** | 7.5/10 | 7.8/10 🟡 | 9.5/10 |
| **Tiempo de deploy** | Manual | Automatizado (backend) 🟡 | <5 min (CI/CD completo) |
| **Documentación** | 10/10 | 10/10 ✅ | 10/10 ✅ |

---

## 📚 Recursos Útiles

### Testing
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Svelte Testing Library](https://testing-library.com/docs/svelte-testing-library/intro/)
- [Pytest Asyncio](https://pytest-asyncio.readthedocs.io/)

### Migrations
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [FastAPI + Alembic](https://testdriven.io/blog/fastapi-sqlmodel/)

### Security
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

### DevOps
- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## 💡 Notas Finales

Este plan está diseñado para ser **incremental y pragmático**. No intentes hacer todo a la vez:

1. **Prioriza CRÍTICO primero** - Testing y migrations son base sólida
2. **Itera en sprints cortos** - 1-2 semanas por sección
3. **Mantén tests pasando** - Nunca rompas el build
4. **Documenta cambios** - Actualiza README con cada mejora
5. **Celebra progreso** - Cada mejora cuenta

**El proyecto ya es muy bueno (8.0/10)**. Estas mejoras lo llevarán a **excelente (9.5/10)** y **production-ready**.

---

**Creado:** 2025-12-13
**Última actualización:** 2026-01-20
**Versión del plan:** 1.1

---

## 📝 Resumen de Progreso (2026-01-20)

### ✅ Completadas
1. **Testing Backend** - Estructura completa de tests (~1197 líneas)
2. **GitHub Actions CI** - Pipeline automatizado para backend
3. **Docker Compose** - Orquestación completa backend + frontend
4. **API Versioning** - Prefijo `/api` implementado
5. **.env Management** - Archivos .env y .env.example configurados

### 🟡 Parcialmente Completadas
1. **Secrets Management** - Falta validación de SECRET_KEY en producción (75%)
2. **Logging** - Básico implementado, falta formato JSON estructurado (40%)
3. **Test Coverage** - Backend ~50%, Frontend 0%

### ❌ Pendientes Prioritarias
1. **Alembic Migrations** - Sistema de migraciones de BD
2. **Nomenclatura PEP8** - Refactorizar clases a PascalCase
3. **SQLAlchemy Relationships** - Optimizar consultas
4. **Validación de Contraseñas** - Requisitos de complejidad
5. **Rate Limiting** - Protección contra fuerza bruta
6. **Frontend Testing** - Vitest + Testing Library
7. **Error Handling** - Sistema de excepciones custom
