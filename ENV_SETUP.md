# 🔧 Configuración de Variables de Entorno

Esta guía explica cómo configurar las variables de entorno para el proyecto Marco.

## 📋 Índice

- [Backend (.env)](#-backend-env)
- [Frontend (.env)](#-frontend-env)
- [Configuración de Producción](#-configuración-de-producción)
- [Variables de Entorno Disponibles](#-variables-de-entorno-disponibles)

---

## 🔙 Backend (.env)

### Paso 1: Crear el archivo .env

```bash
cd backend
cp .env.example .env
```

### Paso 2: Generar SECRET_KEY segura

**IMPORTANTE:** Genera una clave secreta única para producción:

```bash
openssl rand -hex 32
```

### Paso 3: Configurar variables

Edita `backend/.env` con tus valores:

```env
# SEGURIDAD (¡CAMBIAR EN PRODUCCIÓN!)
SECRET_KEY=tu-clave-super-secreta-aqui-32-caracteres-hex

# BASE DE DATOS
DATABASE_URL=sqlite+aiosqlite:///./app.db

# SERVIDOR
HOST=127.0.0.1
PORT=8000
RELOAD=true

# CORS - Orígenes permitidos (separados por comas)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 días
JWT_ALGORITHM=HS256

# ENTORNO
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# APLICACIÓN
APP_NAME=Marco Habit Tracker
API_VERSION=2.0.0
API_DESCRIPTION=API para seguimiento de hábitos con autenticación JWT
```

---

## 🎨 Frontend (.env)

### Paso 1: Crear el archivo .env

```bash
cd frontend
cp .env.example .env
```

### Paso 2: Configurar variables

Edita `frontend/.env`:

```env
# API BACKEND
VITE_API_URL=http://127.0.0.1:8000/api

# APLICACIÓN
VITE_APP_NAME=Marco Habit Tracker
VITE_APP_VERSION=2.0.0

# ENTORNO
VITE_ENVIRONMENT=development

# CARACTERÍSTICAS
VITE_DEBUG=true
VITE_SHOW_VERSION=true
```

---

## 🚀 Configuración de Producción

### Backend - Producción

```env
# SEGURIDAD
SECRET_KEY=clave-generada-con-openssl-rand-hex-32

# BASE DE DATOS
DATABASE_URL=postgresql+asyncpg://user:password@localhost/marco_db

# SERVIDOR
HOST=0.0.0.0
PORT=8000
RELOAD=false

# CORS
CORS_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=10080
JWT_ALGORITHM=HS256

# ENTORNO
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

### Frontend - Producción

```env
# API BACKEND
VITE_API_URL=https://api.tu-dominio.com/api

# APLICACIÓN
VITE_APP_NAME=Marco Habit Tracker
VITE_APP_VERSION=2.0.0

# ENTORNO
VITE_ENVIRONMENT=production

# CARACTERÍSTICAS
VITE_DEBUG=false
VITE_SHOW_VERSION=true
```

---

## 📚 Variables de Entorno Disponibles

### Backend

| Variable | Tipo | Default | Descripción |
|----------|------|---------|-------------|
| `SECRET_KEY` | string | ⚠️ Cambiar | Clave secreta para JWT (32 caracteres hex) |
| `DATABASE_URL` | string | SQLite local | URL de conexión a la base de datos |
| `HOST` | string | `127.0.0.1` | Host del servidor |
| `PORT` | int | `8000` | Puerto del servidor |
| `RELOAD` | bool | `true` | Recarga automática en desarrollo |
| `CORS_ORIGINS` | string | localhost | Orígenes CORS permitidos (separados por coma) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `10080` | Tiempo de expiración del token (7 días) |
| `JWT_ALGORITHM` | string | `HS256` | Algoritmo de encriptación JWT |
| `ENVIRONMENT` | string | `development` | Ambiente: development, staging, production |
| `DEBUG` | bool | `true` | Modo debug |
| `LOG_LEVEL` | string | `INFO` | Nivel de log: DEBUG, INFO, WARNING, ERROR |
| `APP_NAME` | string | Marco... | Nombre de la aplicación |
| `API_VERSION` | string | `2.0.0` | Versión de la API |
| `API_DESCRIPTION` | string | API para... | Descripción de la API |

### Frontend

| Variable | Tipo | Default | Descripción |
|----------|------|---------|-------------|
| `VITE_API_URL` | string | `http://127.0.0.1:8000/api` | URL base de la API backend |
| `VITE_APP_NAME` | string | Marco... | Nombre de la aplicación |
| `VITE_APP_VERSION` | string | `2.0.0` | Versión de la aplicación |
| `VITE_ENVIRONMENT` | string | `development` | Ambiente de ejecución |
| `VITE_DEBUG` | bool | `true` | Habilitar debug en consola |
| `VITE_SHOW_VERSION` | bool | `true` | Mostrar versión en footer |

---

## 🔒 Seguridad

### ⚠️ Importante

1. **NUNCA** subas archivos `.env` a Git
2. **SIEMPRE** usa `.env.example` como plantilla
3. **GENERA** una `SECRET_KEY` única para cada entorno
4. **CAMBIA** las claves por defecto en producción
5. **USA** HTTPS en producción

### Verificar SECRET_KEY

```bash
# Debe tener 64 caracteres (32 bytes en hex)
echo "tu-secret-key" | wc -c
```

### Rotar SECRET_KEY

Si necesitas cambiar la `SECRET_KEY`:

1. Genera una nueva clave: `openssl rand -hex 32`
2. Actualiza `.env` con la nueva clave
3. Reinicia el servidor
4. ⚠️ Todos los tokens JWT existentes se invalidarán

---

## 🐛 Troubleshooting

### Backend no carga las variables

```bash
# Verificar que existe .env
ls -la backend/.env

# Verificar contenido
cat backend/.env

# Verificar que pydantic-settings está instalado
cd backend && uv pip list | grep pydantic-settings
```

### Frontend no carga las variables

```bash
# Las variables DEBEN empezar con VITE_
# Verificar archivo
cat frontend/.env

# Reiniciar servidor de desarrollo
pnpm dev
```

### CORS Errors

Asegúrate de que el origen del frontend esté en `CORS_ORIGINS`:

```env
# Ejemplo correcto
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

## 📝 Notas Adicionales

- Las variables con prefijo `VITE_` están disponibles en el frontend
- Las variables sin prefijo son solo para el backend
- Los cambios en `.env` requieren reiniciar el servidor
- Usa `.env.local` para sobrescribir valores localmente (no se sube a Git)

---

**💡 Tip:** Mantén `.env.example` actualizado cuando agregues nuevas variables

