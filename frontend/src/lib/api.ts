const API_BASE = 'http://127.0.0.1:8000/api';

/**
 * Obtiene los headers de autenticación si hay un token guardado
 */
function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('auth_token');
  if (token) {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  }
  return {
    'Content-Type': 'application/json'
  };
}

// ==================== Habito ====================
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
  descripcion?: string;
  categoria_id: number;
  usuario_id: number;
  unidad_medida: string;
  meta_diaria: number;
  dias: string;
  color: string;
  activo?: number;
}

export interface HabitoUpdate {
  nombre?: string;
  descripcion?: string;
  categoria_id?: number;
  unidad_medida?: string;
  meta_diaria?: number;
  dias?: string;
  color?: string;
  activo?: number;
}

// ==================== Usuario ====================
export interface Usuario {
  id: number;
  nombre: string;
  email: string;
  ver_futuro: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface UsuarioUpdate {
  nombre?: string;
  email?: string;
  ver_futuro?: boolean;
}

// ==================== Categoria ====================
export interface Categoria {
  id: number;
  nombre: string;
  created_at: string;
  updated_at: string | null;
}

// ==================== Registro y Progreso ====================
export interface ProgresoHabito {
  id: number;
  registro_id: number;
  habito_id: number;
  valor: number;
  completado: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface Registro {
  id: number;
  usuario_id: number;
  fecha: string;
  notas: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface RegistroConProgresos extends Registro {
  progresos: ProgresoHabito[];
}

// ==================== Habitos API ====================
export async function getHabitos(): Promise<Habito[]> {
  const res = await fetch(`${API_BASE}/habitos`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Error al obtener hábitos');
  return res.json();
}

export async function getMyHabitos(): Promise<Habito[]> {
  const res = await fetch(`${API_BASE}/habitos/me`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Error al obtener hábitos del usuario');
  return res.json();
}

export async function getHabitosByUsuario(usuarioId: number): Promise<Habito[]> {
  const res = await fetch(`${API_BASE}/habitos/usuario/${usuarioId}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Error al obtener hábitos del usuario');
  return res.json();
}

export async function getHabito(id: number): Promise<Habito> {
  const res = await fetch(`${API_BASE}/habitos/${id}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Error al obtener hábito');
  return res.json();
}

export async function createHabito(habito: HabitoCreate): Promise<Habito> {
  const res = await fetch(`${API_BASE}/habitos/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(habito)
  });
  if (!res.ok) throw new Error('Error al crear hábito');
  return res.json();
}

export async function updateHabito(id: number, habito: HabitoUpdate): Promise<Habito> {
  const res = await fetch(`${API_BASE}/habitos/${id}/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(habito)
  });
  if (!res.ok) throw new Error('Error al actualizar hábito');
  return res.json();
}

export async function deleteHabito(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/habitos/${id}/`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Error al eliminar hábito');
}

// ==================== Categorias API ====================
export async function getCategorias(): Promise<Categoria[]> {
  const res = await fetch(`${API_BASE}/categorias`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Error al obtener categorías');
  return res.json();
}

export async function getCategoria(id: number): Promise<Categoria> {
  const res = await fetch(`${API_BASE}/categorias/${id}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Error al obtener categoría');
  return res.json();
}

// ==================== Usuarios API ====================
export async function getUsuarios(): Promise<Usuario[]> {
  const res = await fetch(`${API_BASE}/usuarios`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Error al obtener usuarios');
  return res.json();
}

export async function getCurrentUser(): Promise<Usuario> {
  const res = await fetch(`${API_BASE}/usuarios/me`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Error al obtener usuario actual');
  return res.json();
}

export async function getUsuario(id: number): Promise<Usuario> {
  const res = await fetch(`${API_BASE}/usuarios/${id}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Error al obtener usuario');
  return res.json();
}

export async function updateCurrentUser(data: UsuarioUpdate): Promise<Usuario> {
  const res = await fetch(`${API_BASE}/usuarios/me`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Error al actualizar usuario');
  return res.json();
}

export async function updateUsuario(id: number, data: UsuarioUpdate): Promise<Usuario> {
  const res = await fetch(`${API_BASE}/usuarios/${id}/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Error al actualizar usuario');
  return res.json();
}

// ==================== Registros API ====================
export async function getRegistroPorFecha(usuarioId: number, fecha: string): Promise<RegistroConProgresos> {
  const res = await fetch(`${API_BASE}/registros/usuario/${usuarioId}/fecha/${fecha}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Error al obtener registro');
  }
  return res.json();
}

export async function toggleProgreso(progresoId: number): Promise<ProgresoHabito> {
  const res = await fetch(`${API_BASE}/registros/progreso/toggle/${progresoId}/`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Error al actualizar progreso');
  return res.json();
}

export async function updateProgreso(progresoId: number, data: { valor?: number; completado?: boolean }): Promise<ProgresoHabito> {
  const res = await fetch(`${API_BASE}/registros/progreso/${progresoId}/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Error al actualizar progreso');
  return res.json();
}

// ==================== Auth API ====================
export interface LoginRequest {
  email: string;
  contrasena: string;
}

export interface RegisterRequest {
  nombre: string;
  email: string;
  contrasena: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  usuario: Usuario;
}

export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials)
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Error al iniciar sesión');
  }

  return res.json();
}

export async function register(userData: RegisterRequest): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Error al registrarse');
  }

  return res.json();
}
