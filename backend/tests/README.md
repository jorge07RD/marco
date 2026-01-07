# 🧪 Tests del Backend - Guía Zen de Testing

> *"Un test bien escrito es como un koan zen: claro, directo y revelador."*

## 📖 Filosofía de Testing

Estos tests siguen los principios del Zen de Python:

### 🧘 Principios Aplicados

1. **Explícito es mejor que implícito**
   - Nombres de tests descriptivos que documentan el comportamiento
   - Asserts claros con mensajes específicos
   - No hay "magic numbers" ni valores ambiguos

2. **Simple es mejor que complejo**
   - Un test = una responsabilidad
   - Tests fáciles de leer y entender
   - Fixtures reutilizables para reducir duplicación

3. **Plano es mejor que anidado**
   - Tests organizados en clases por funcionalidad
   - Early returns en validaciones
   - Fixtures independientes

4. **Los errores nunca deberían pasar silenciosamente**
   - Todos los casos de error tienen tests
   - Tests de validaciones explícitas
   - Tests de autenticación/autorización

---

## 📂 Estructura de Tests

```
tests/
├── __init__.py           # Documentación de la suite
├── conftest.py           # Fixtures compartidas
├── README.md            # Esta guía
│
├── unit/                # Tests unitarios
│   ├── __init__.py
│   └── test_security.py # Tests de funciones de seguridad
│
├── routers/             # Tests de endpoints
│   ├── __init__.py
│   ├── test_auth.py     # Tests de autenticación
│   ├── test_categorias.py
│   ├── test_habitos.py
│   └── test_registros.py
│
└── integration/         # Tests end-to-end
    └── __init__.py
```

---

## 🚀 Ejecución de Tests

### Instalar Dependencias de Testing

```bash
# Con uv (recomendado)
cd backend
uv sync --dev

# O con pip
pip install -e ".[dev]"
```

### Ejecutar Todos los Tests

```bash
# Desde el directorio backend/
pytest

# Con output verbose
pytest -v

# Con cobertura
pytest --cov=app --cov-report=html

# Solo tests de un módulo específico
pytest tests/routers/test_auth.py

# Solo tests que coincidan con un patrón
pytest -k "test_login"
```

### Ejecutar Tests con Diferentes Niveles de Detalle

```bash
# Mínimo (solo puntos)
pytest

# Normal (nombres de archivos)
pytest -v

# Detallado (nombres completos de tests)
pytest -vv

# Con print statements
pytest -s

# Detener en el primer fallo
pytest -x

# Mostrar tests más lentos
pytest --durations=10
```

---

## 🎯 Convenciones de Naming

### Nombres de Clases de Test

```python
class TestGetHabitos:      # Agrupa tests del endpoint GET /habitos
class TestCreateHabito:    # Agrupa tests del endpoint POST /habitos
class TestUpdateHabito:    # Agrupa tests del endpoint PUT /habitos
```

### Nombres de Funciones de Test

Formato: `test_<accion>_<condicion>_<resultado>`

```python
test_login_success()                    # Happy path
test_login_wrong_password_fails()       # Caso de error
test_get_habito_requires_auth()         # Validación de autenticación
test_create_habito_invalid_data_fails() # Validación de datos
```

---

## 🔧 Fixtures Disponibles

### Fixtures de Base de Datos

- `test_engine`: Engine SQLAlchemy con BD en memoria
- `test_db_session`: Sesión de BD para cada test (con rollback automático)
- `test_client`: Cliente HTTP asíncrono con BD de test

### Fixtures de Autenticación

- `test_user`: Usuario de prueba estándar
- `test_user_with_future`: Usuario con `ver_futuro=True`
- `auth_token`: Token JWT para el usuario de prueba
- `auth_headers`: Headers con `Authorization: Bearer <token>`

### Fixtures de Datos

- `test_categoria`: Categoría de prueba ("Salud")

### Ejemplo de Uso

```python
@pytest.mark.asyncio
async def test_mi_endpoint(
    test_client: AsyncClient,
    test_user: usuario,
    auth_headers: dict
):
    """Test: Descripción clara del comportamiento esperado."""
    response = await test_client.get(
        "/mi-endpoint",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == test_user.id
```

---

## ✅ Checklist de Test Completo

Para cada endpoint, asegúrate de tener tests para:

### Happy Path
- [ ] Operación exitosa con datos válidos
- [ ] Retorna el status code correcto
- [ ] Retorna los datos esperados en el formato correcto

### Autenticación y Autorización
- [ ] Requiere autenticación cuando corresponde
- [ ] Rechaza tokens inválidos
- [ ] Solo permite acceso a recursos propios

### Validación de Datos
- [ ] Rechaza datos faltantes
- [ ] Rechaza datos con formato inválido
- [ ] Valida límites (min/max length, valores)

### Casos Edge
- [ ] Recursos no encontrados (404)
- [ ] Datos duplicados
- [ ] Operaciones idempotentes

### Errores
- [ ] Manejo apropiado de errores de BD
- [ ] Mensajes de error claros y específicos

---

## 🐛 Debugging de Tests

### Test Específico Falla

```bash
# Ejecutar solo ese test con output verbose
pytest tests/routers/test_auth.py::TestLogin::test_login_success -vv

# Con print statements
pytest tests/routers/test_auth.py::TestLogin::test_login_success -s

# Con debugger
pytest tests/routers/test_auth.py::TestLogin::test_login_success --pdb
```

### Todos los Tests de un Módulo Fallan

```bash
# Ver stack traces completos
pytest tests/routers/test_auth.py -vv --tb=long

# Ver solo el primer fallo
pytest tests/routers/test_auth.py -x
```

### Base de Datos en Tests

```python
# Activar logging de SQL en conftest.py
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True  # 🔍 Muestra todas las queries SQL
)
```

---

## 📊 Cobertura de Tests

### Generar Reporte de Cobertura

```bash
# Generar reporte HTML
pytest --cov=app --cov-report=html

# Abrir reporte
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Objetivo de Cobertura

- **Crítico (100%):** `security.py`, `auth.py`
- **Alto (>80%):** Routers principales
- **Medio (>60%):** Utilidades y helpers
- **Bajo:** Configuración, main.py

---

## 🧘 Mejores Prácticas Zen

### 1. Un Test = Una Responsabilidad

❌ **Mal:**
```python
def test_create_and_update_user():
    # Crea usuario
    # Actualiza usuario
    # Elimina usuario
    # ❌ Hace demasiado
```

✅ **Bien:**
```python
def test_create_user_success():
    # Solo crea usuario

def test_update_user_success():
    # Solo actualiza usuario
```

### 2. Nombres Descriptivos

❌ **Mal:**
```python
def test_1():
def test_error():
def test_usuario():
```

✅ **Bien:**
```python
def test_login_wrong_password_fails():
def test_create_user_duplicate_email_fails():
def test_get_habito_requires_authentication():
```

### 3. Asserts Explícitos

❌ **Mal:**
```python
assert response.status_code  # ¿Qué esperamos?
assert data  # ¿Qué debe contener?
```

✅ **Bien:**
```python
assert response.status_code == 201
assert "access_token" in data
assert data["user"]["email"] == "test@example.com"
```

### 4. Fixtures Claras

❌ **Mal:**
```python
@pytest.fixture
def user():
    # ¿Qué tipo de usuario?
    # ¿Con qué datos?
```

✅ **Bien:**
```python
@pytest_asyncio.fixture
async def test_user(test_db_session: AsyncSession) -> usuario:
    """
    Crea un usuario de prueba en la base de datos.

    Returns:
        usuario con email=test@example.com y ver_futuro=False
    """
```

---

## 📚 Referencias

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [The Zen of Python (PEP 20)](https://www.python.org/dev/peps/pep-0020/)

---

🧘 **"Un test que falla es un maestro. Un test que pasa es un alumno. Una suite completa es la iluminación."** - Maestro Zen
