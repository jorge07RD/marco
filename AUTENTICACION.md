# 🔐 Sistema de Autenticación - Proyecto Marco

## ✅ Lo que se ha implementado

### Backend Completo

#### 1. **Módulo de Seguridad** (`backend/app/security.py`)
- ✅ Hashing de contraseñas con bcrypt
- ✅ Generación de tokens JWT
- ✅ Verificación de tokens
- ✅ Dependencia `get_current_user()` para proteger endpoints

#### 2. **Endpoints de Autenticación** (`backend/app/routers/auth.py`)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/auth/register` | POST | Registrar nuevo usuario |
| `/api/auth/login` | POST | Iniciar sesión |
| `/api/auth/me` | GET | Obtener usuario autenticado |

#### 3. **Schemas Actualizados** (`backend/app/schemas.py`)
- ✅ `LoginRequest` - Para login
- ✅ `RegisterRequest` - Para registro
- ✅ `TokenResponse` - Respuesta con token y datos de usuario
- ✅ `HabitoCreate` - Ya no requiere `usuario_id` (se toma del token)

#### 4. **Routers Protegidos**
- ✅ `backend/app/routers/habitos.py` - Todos los endpoints protegidos
- ✅ `backend/app/routers/registros.py` - Todos los endpoints protegidos
- ✅ **IMPORTANTE**: Cada usuario solo ve sus propios datos

---

## 📡 API Reference - Endpoints de Autenticación

### 1. Registrar Usuario

```http
POST /api/auth/register
Content-Type: application/json

{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "password": "MiPassword123",
  "ver_futuro": false
}
```

**Respuesta exitosa (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "ver_futuro": false,
    "created_at": "2025-12-10T10:00:00",
    "updated_at": null
  }
}
```

**Errores:**
- `400` - Email ya registrado o nombre en uso
- `422` - Datos de validación incorrectos

---

### 2. Iniciar Sesión

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "juan@example.com",
  "password": "MiPassword123"
}
```

**Respuesta exitosa (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "ver_futuro": false,
    "created_at": "2025-12-10T10:00:00",
    "updated_at": null
  }
}
```

**Errores:**
- `401` - Email o contraseña incorrectos

---

### 3. Obtener Usuario Actual

```http
GET /api/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "ver_futuro": false,
  "created_at": "2025-12-10T10:00:00",
  "updated_at": null
}
```

**Errores:**
- `401` - Token inválido o expirado

---

## 🔒 Endpoints Protegidos

**TODOS los siguientes endpoints ahora requieren autenticación:**

### Hábitos
- `GET /api/habitos/` - Lista hábitos del usuario autenticado
- `GET /api/habitos/{habito_id}` - Obtiene hábito (solo si pertenece al usuario)
- `POST /api/habitos/` - Crea hábito para el usuario autenticado
- `PUT /api/habitos/{habito_id}` - Actualiza hábito propio
- `DELETE /api/habitos/{habito_id}` - Elimina hábito propio

### Registros
- `GET /api/registros/` - Lista registros del usuario autenticado
- `GET /api/registros/fecha/{fecha}` - Obtiene/crea registro del usuario para fecha
- `PUT /api/registros/progreso/{progreso_id}` - Actualiza progreso
- `POST /api/registros/progreso/toggle/{progreso_id}` - Alterna completado

### Análisis
- `GET /api/analisis/rendimiento?fecha_inicio={fecha}&fecha_fin={fecha}` - Obtiene rendimiento por día del usuario
- `GET /api/analisis/cumplimiento?fecha_inicio={fecha}&fecha_fin={fecha}` - Obtiene cumplimiento de hábitos del usuario

---

## 🚀 Integración con Frontend

### 1. Crear Cliente API con Autenticación

```typescript
// frontend/src/lib/api.ts

const API_URL = "http://127.0.0.1:8000/api";

// ==================== Auth Token Management ====================
export function guardarToken(token: string): void {
  localStorage.setItem('access_token', token);
}

export function obtenerToken(): string | null {
  return localStorage.setItem('access_token');
}

export function eliminarToken(): void {
  localStorage.removeItem('access_token');
}

// ==================== Fetch con Auth ====================
async function fetchConAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const token = obtenerToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Agregar token si existe
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${url}`, {
    ...options,
    headers,
  });

  // Si el token es inválido, redirigir a login
  if (response.status === 401) {
    eliminarToken();
    window.location.href = '/login';
    throw new Error('Sesión expirada');
  }

  return response;
}

// ==================== Types ====================
export interface Usuario {
  id: number;
  nombre: string;
  email: string;
  ver_futuro: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: Usuario;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  nombre: string;
  email: string;
  password: string;
  ver_futuro?: boolean;
}

export interface Habito {
  id: number;
  nombre: string;
  descripcion: string | null;
  categoria_id: number;
  usuario_id: number;
  unidad_medida: string;
  meta_diaria: number;
  dias: string;
  color: string;
  activo: number;
  created_at: string;
  updated_at: string | null;
}

export interface HabitoCreate {
  nombre: string;
  descripcion?: string | null;
  categoria_id: number;
  unidad_medida: string;
  meta_diaria: number;
  dias: string;
  color: string;
  activo?: number;
}

// ==================== Auth API ====================
export async function registrar(data: RegisterRequest): Promise<TokenResponse> {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al registrar');
  }

  const tokenResponse = await response.json();
  guardarToken(tokenResponse.access_token);
  return tokenResponse;
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al iniciar sesión');
  }

  const tokenResponse = await response.json();
  guardarToken(tokenResponse.access_token);
  return tokenResponse;
}

export async function obtenerUsuarioActual(): Promise<Usuario> {
  const response = await fetchConAuth('/auth/me');

  if (!response.ok) {
    throw new Error('Error al obtener usuario');
  }

  return response.json();
}

export function logout(): void {
  eliminarToken();
  window.location.href = '/login';
}

// ==================== Hábitos API ====================
export async function listarHabitos(): Promise<Habito[]> {
  const response = await fetchConAuth('/habitos/');

  if (!response.ok) {
    throw new Error('Error al listar hábitos');
  }

  return response.json();
}

export async function crearHabito(habito: HabitoCreate): Promise<Habito> {
  const response = await fetchConAuth('/habitos/', {
    method: 'POST',
    body: JSON.stringify(habito),
  });

  if (!response.ok) {
    throw new Error('Error al crear hábito');
  }

  return response.json();
}

export async function eliminarHabito(id: number): Promise<void> {
  const response = await fetchConAuth(`/habitos/${id}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Error al eliminar hábito');
  }
}

// ... más funciones de API
```

---

### 2. Crear Store de Autenticación

```typescript
// frontend/src/lib/stores/auth.svelte.ts

import { obtenerToken, obtenerUsuarioActual, logout } from '$lib/api';
import type { Usuario } from '$lib/api';

class AuthStore {
  user = $state<Usuario | null>(null);
  loading = $state(true);
  isAuthenticated = $derived(this.user !== null);

  async init() {
    const token = obtenerToken();

    if (!token) {
      this.loading = false;
      return;
    }

    try {
      this.user = await obtenerUsuarioActual();
    } catch (error) {
      console.error('Error al cargar usuario:', error);
      logout();
    } finally {
      this.loading = false;
    }
  }

  setUser(user: Usuario) {
    this.user = user;
  }

  logout() {
    this.user = null;
    logout();
  }
}

export const authStore = new AuthStore();
```

---

### 3. Página de Login

```svelte
<!-- frontend/src/routes/login/+page.svelte -->
<script lang="ts">
  import { goto } from '$app/navigation';
  import { login } from '$lib/api';
  import { authStore } from '$lib/stores/auth.svelte';

  let email = $state('');
  let password = $state('');
  let loading = $state(false);
  let error = $state<string | null>(null);

  async function handleLogin(e: Event) {
    e.preventDefault();
    loading = true;
    error = null;

    try {
      const response = await login({ email, password });
      authStore.setUser(response.user);
      goto('/');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error desconocido';
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen bg-[#0E0D0D] flex items-center justify-center p-4">
  <div class="bg-[#1a1a1a] border border-[#533483] rounded-lg p-8 max-w-md w-full">
    <h1 class="text-3xl font-bold text-white mb-6 text-center">
      Iniciar Sesión
    </h1>

    {#if error}
      <div class="bg-red-500/10 border border-red-500 text-red-500 p-3 rounded-md mb-4">
        {error}
      </div>
    {/if}

    <form onsubmit={handleLogin} class="space-y-4">
      <div>
        <label for="email" class="block text-sm font-medium text-white mb-2">
          Email
        </label>
        <input
          id="email"
          type="email"
          bind:value={email}
          required
          disabled={loading}
          class="w-full bg-[#0E0D0D] border border-[#533483] text-white px-4 py-2
                 rounded-md focus:outline-none focus:ring-2 focus:ring-[#e94560]"
        />
      </div>

      <div>
        <label for="password" class="block text-sm font-medium text-white mb-2">
          Contraseña
        </label>
        <input
          id="password"
          type="password"
          bind:value={password}
          required
          disabled={loading}
          class="w-full bg-[#0E0D0D] border border-[#533483] text-white px-4 py-2
                 rounded-md focus:outline-none focus:ring-2 focus:ring-[#e94560]"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        class="w-full bg-[#e94560] text-white py-2 px-4 rounded-md font-medium
               hover:bg-[#d13851] transition-colors disabled:opacity-50
               disabled:cursor-not-allowed"
      >
        {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
      </button>
    </form>

    <p class="text-[#A0A0A0] text-center mt-6">
      ¿No tienes cuenta?
      <a href="/register" class="text-[#e94560] hover:underline">
        Regístrate aquí
      </a>
    </p>
  </div>
</div>
```

---

### 4. Página de Registro

```svelte
<!-- frontend/src/routes/register/+page.svelte -->
<script lang="ts">
  import { goto } from '$app/navigation';
  import { registrar } from '$lib/api';
  import { authStore } from '$lib/stores/auth.svelte';

  let nombre = $state('');
  let email = $state('');
  let password = $state('');
  let confirmPassword = $state('');
  let loading = $state(false);
  let error = $state<string | null>(null);

  let passwordsMatch = $derived(password === confirmPassword);
  let formValid = $derived(
    nombre.length > 0 &&
    email.length > 0 &&
    password.length >= 8 &&
    passwordsMatch
  );

  async function handleRegister(e: Event) {
    e.preventDefault();

    if (!formValid) return;

    loading = true;
    error = null;

    try {
      const response = await registrar({ nombre, email, password });
      authStore.setUser(response.user);
      goto('/');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error desconocido';
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen bg-[#0E0D0D] flex items-center justify-center p-4">
  <div class="bg-[#1a1a1a] border border-[#533483] rounded-lg p-8 max-w-md w-full">
    <h1 class="text-3xl font-bold text-white mb-6 text-center">
      Crear Cuenta
    </h1>

    {#if error}
      <div class="bg-red-500/10 border border-red-500 text-red-500 p-3 rounded-md mb-4">
        {error}
      </div>
    {/if}

    <form onsubmit={handleRegister} class="space-y-4">
      <div>
        <label for="nombre" class="block text-sm font-medium text-white mb-2">
          Nombre
        </label>
        <input
          id="nombre"
          type="text"
          bind:value={nombre}
          required
          disabled={loading}
          class="w-full bg-[#0E0D0D] border border-[#533483] text-white px-4 py-2
                 rounded-md focus:outline-none focus:ring-2 focus:ring-[#e94560]"
        />
      </div>

      <div>
        <label for="email" class="block text-sm font-medium text-white mb-2">
          Email
        </label>
        <input
          id="email"
          type="email"
          bind:value={email}
          required
          disabled={loading}
          class="w-full bg-[#0E0D0D] border border-[#533483] text-white px-4 py-2
                 rounded-md focus:outline-none focus:ring-2 focus:ring-[#e94560]"
        />
      </div>

      <div>
        <label for="password" class="block text-sm font-medium text-white mb-2">
          Contraseña (mínimo 8 caracteres)
        </label>
        <input
          id="password"
          type="password"
          bind:value={password}
          required
          minlength="8"
          disabled={loading}
          class="w-full bg-[#0E0D0D] border border-[#533483] text-white px-4 py-2
                 rounded-md focus:outline-none focus:ring-2 focus:ring-[#e94560]"
        />
      </div>

      <div>
        <label for="confirmPassword" class="block text-sm font-medium text-white mb-2">
          Confirmar Contraseña
        </label>
        <input
          id="confirmPassword"
          type="password"
          bind:value={confirmPassword}
          required
          disabled={loading}
          class="w-full bg-[#0E0D0D] border border-[#533483] text-white px-4 py-2
                 rounded-md focus:outline-none focus:ring-2 focus:ring-[#e94560]
                 {confirmPassword && !passwordsMatch ? 'border-red-500' : ''}"
        />
        {#if confirmPassword && !passwordsMatch}
          <p class="text-red-500 text-sm mt-1">Las contraseñas no coinciden</p>
        {/if}
      </div>

      <button
        type="submit"
        disabled={!formValid || loading}
        class="w-full bg-[#e94560] text-white py-2 px-4 rounded-md font-medium
               hover:bg-[#d13851] transition-colors disabled:opacity-50
               disabled:cursor-not-allowed"
      >
        {loading ? 'Creando cuenta...' : 'Crear Cuenta'}
      </button>
    </form>

    <p class="text-[#A0A0A0] text-center mt-6">
      ¿Ya tienes cuenta?
      <a href="/login" class="text-[#e94560] hover:underline">
        Inicia sesión aquí
      </a>
    </p>
  </div>
</div>
```

---

### 5. Proteger Rutas con Layout

```svelte
<!-- frontend/src/routes/+layout.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { authStore } from '$lib/stores/auth.svelte';

  const publicRoutes = ['/login', '/register'];

  onMount(async () => {
    await authStore.init();

    // Redirigir a login si no está autenticado y no está en ruta pública
    if (!authStore.isAuthenticated && !publicRoutes.includes($page.url.pathname)) {
      goto('/login');
    }

    // Redirigir a home si está autenticado y trata de acceder a login/register
    if (authStore.isAuthenticated && publicRoutes.includes($page.url.pathname)) {
      goto('/');
    }
  });
</script>

{#if authStore.loading}
  <div class="min-h-screen bg-[#0E0D0D] flex items-center justify-center">
    <p class="text-white">Cargando...</p>
  </div>
{:else}
  <slot />
{/if}
```

---

## 🧪 Probar la Implementación

### 1. Iniciar el Backend

```bash
cd backend
uv run uvicorn app.main:app --reload
```

### 2. Probar en Swagger

Abre http://127.0.0.1:8000/docs y prueba:

1. **Registrar usuario**:
   - Endpoint: `POST /api/auth/register`
   - Body: `{"nombre": "Test", "email": "test@test.com", "password": "password123"}`
   - Copia el `access_token` de la respuesta

2. **Autorizar en Swagger**:
   - Click en "Authorize" (candado)
   - Pega el token: `Bearer {tu_token}`
   - Click "Authorize"

3. **Probar endpoint protegido**:
   - `GET /api/habitos/` - Debería funcionar y retornar array vacío
   - `POST /api/habitos/` - Crea un hábito (ya no necesitas `usuario_id`)

---

## 📝 Cambios Importantes

### ⚠️ BREAKING CHANGES

1. **`POST /api/habitos/`** ya NO requiere `usuario_id` en el body
   - Antes: `{"nombre": "...", "usuario_id": 1, ...}`
   - Ahora: `{"nombre": "...", ...}` (el usuario_id se toma del token)

2. **`GET /api/habitos/`** ya NO tiene parámetro `usuario_id`
   - Antes: `GET /api/habitos/usuario/1`
   - Ahora: `GET /api/habitos/` (retorna solo hábitos del usuario autenticado)

3. **`GET /api/registros/fecha/{fecha}`** ya NO tiene `usuario_id` en la URL
   - Antes: `GET /api/registros/usuario/1/fecha/2025-12-10`
   - Ahora: `GET /api/registros/fecha/2025-12-10`

---

## 🔧 Configuración de Producción

### Variables de Entorno (`.env`)

```env
# Backend (.env en backend/)
SECRET_KEY=tu-secret-key-muy-segura-generada-con-openssl-rand-hex-32
DATABASE_URL=sqlite+aiosqlite:///./app.db
DEBUG=False
```

### Generar SECRET_KEY segura

```bash
openssl rand -hex 32
```

---

## ✅ Checklist de Implementación Frontend

- [ ] Crear `lib/api.ts` con funciones de autenticación
- [ ] Crear `lib/stores/auth.svelte.ts` con store de usuario
- [ ] Crear página `/login`
- [ ] Crear página `/register`
- [ ] Actualizar `+layout.svelte` para proteger rutas
- [ ] Actualizar todas las llamadas API para usar `fetchConAuth()`
- [ ] Remover `usuario_id` hardcodeado de formularios
- [ ] Agregar botón de "Cerrar sesión" en el nav
- [ ] Manejar token expirado (redirect a /login)
- [ ] Mostrar nombre de usuario en el navbar

---

## 🐛 Troubleshooting

### Error 401 en todas las peticiones
- Verifica que el token esté en localStorage
- Verifica que el header `Authorization` tenga formato: `Bearer {token}`
- Verifica que el token no haya expirado (expira en 7 días)

### Email ya registrado
- El sistema valida unicidad de email y nombre
- Usa emails únicos para cada usuario

### CORS Error
- Verifica que el frontend esté corriendo en puerto 5173
- Si cambias el puerto, actualiza `backend/app/main.py` en CORS

---

## 🎉 Próximos Pasos Sugeridos

1. **Mejorar UX**:
   - Mostrar nombre de usuario en navbar
   - Botón de "Cerrar sesión"
   - Página de perfil para editar datos

2. **Seguridad**:
   - Implementar refresh tokens
   - Rate limiting en login
   - Recuperación de contraseña

3. **Features**:
   - "Recordarme" en login
   - Cambiar contraseña
   - Eliminar cuenta

---

**¡El sistema de autenticación está listo para usarse!** 🚀

Todos los datos están ahora separados por usuario y protegidos con JWT.
