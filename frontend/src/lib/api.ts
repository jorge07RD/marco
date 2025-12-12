// URL base de la API cargada desde variables de entorno
// En desarrollo: http://127.0.0.1:8000/api
// En producción: configurar VITE_API_URL en .env
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

// ==================== Auth Token Management ====================
export function guardarToken(token: string): void {
  localStorage.setItem('access_token', token);
}

export function obtenerToken(): string | null {
  return localStorage.getItem('access_token');
}

export function eliminarToken(): void {
  localStorage.removeItem('access_token');
}

// ==================== Fetch con Autenticación ====================
async function fetchConAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const token = obtenerToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  // Agregar token si existe
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
  });

  // Si el token es inválido (401), redirigir a login
  if (response.status === 401) {
    eliminarToken();
    // Redirigir a login
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
  }

  return response;
}

// ==================== Types ====================

// Auth Types
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

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: Usuario;
}

// Usuario
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

// Habito
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
  // ⚠️ Ya no se incluye usuario_id - se toma del token
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

// Categoria
export interface Categoria {
  id: number;
  nombre: string;
  created_at: string;
  updated_at: string | null;
}

// Registro y Progreso
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

// ==================== Auth API ====================

/**
 * Registra un nuevo usuario en el sistema
 */
export async function registrar(data: RegisterRequest): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al registrar usuario');
  }

  const tokenResponse: TokenResponse = await response.json();
  guardarToken(tokenResponse.access_token);
  return tokenResponse;
}

/**
 * Inicia sesión con email y contraseña
 */
export async function login(data: LoginRequest): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al iniciar sesión');
  }

  const tokenResponse: TokenResponse = await response.json();
  guardarToken(tokenResponse.access_token);
  return tokenResponse;
}

/**
 * Obtiene el usuario autenticado actual
 */
export async function obtenerUsuarioActual(): Promise<Usuario> {
  const response = await fetchConAuth('/auth/me');

  if (!response.ok) {
    throw new Error('Error al obtener usuario actual');
  }

  return response.json();
}

/**
 * Cierra la sesión del usuario
 */
export function logout(): void {
  eliminarToken();
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

// ==================== Habitos API (Protegidos) ====================

/**
 * Obtiene todos los hábitos del usuario autenticado
 */
export async function getHabitos(): Promise<Habito[]> {
  const response = await fetchConAuth('/habitos/');

  if (!response.ok) {
    throw new Error('Error al obtener hábitos');
  }

  return response.json();
}

/**
 * Obtiene un hábito específico por ID (solo si pertenece al usuario)
 */
export async function getHabito(id: number): Promise<Habito> {
  const response = await fetchConAuth(`/habitos/${id}`);

  if (!response.ok) {
    throw new Error('Error al obtener hábito');
  }

  return response.json();
}

/**
 * Crea un nuevo hábito para el usuario autenticado
 */
export async function createHabito(habito: HabitoCreate): Promise<Habito> {
  const response = await fetchConAuth('/habitos/', {
    method: 'POST',
    body: JSON.stringify(habito),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al crear hábito');
  }

  return response.json();
}

/**
 * Actualiza un hábito existente
 */
export async function updateHabito(id: number, habito: HabitoUpdate): Promise<Habito> {
  const response = await fetchConAuth(`/habitos/${id}`, {
    method: 'PUT',
    body: JSON.stringify(habito),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al actualizar hábito');
  }

  return response.json();
}

/**
 * Elimina un hábito
 */
export async function deleteHabito(id: number): Promise<void> {
  const response = await fetchConAuth(`/habitos/${id}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Error al eliminar hábito');
  }
}

// ==================== Categorias API ====================

/**
 * Obtiene todas las categorías
 */
export async function getCategorias(): Promise<Categoria[]> {
  const response = await fetchConAuth('/categorias/');

  if (!response.ok) {
    throw new Error('Error al obtener categorías');
  }

  return response.json();
}

/**
 * Obtiene una categoría por ID
 */
export async function getCategoria(id: number): Promise<Categoria> {
  const response = await fetchConAuth(`/categorias/${id}`);

  if (!response.ok) {
    throw new Error('Error al obtener categoría');
  }

  return response.json();
}

// ==================== Registros API (Protegidos) ====================

/**
 * Obtiene o crea el registro del usuario autenticado para una fecha
 */
export async function getRegistroPorFecha(fecha: string): Promise<RegistroConProgresos> {
  const response = await fetchConAuth(`/registros/fecha/${fecha}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al obtener registro');
  }

  return response.json();
}

/**
 * Alterna el estado completado de un progreso
 */
export async function toggleProgreso(progresoId: number): Promise<ProgresoHabito> {
  const response = await fetchConAuth(`/registros/progreso/toggle/${progresoId}`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error('Error al actualizar progreso');
  }

  return response.json();
}

/**
 * Actualiza el valor o completado de un progreso
 */
export async function updateProgreso(
  progresoId: number,
  data: { valor?: number; completado?: boolean }
): Promise<ProgresoHabito> {
  const response = await fetchConAuth(`/registros/progreso/${progresoId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Error al actualizar progreso');
  }

  return response.json();
}

// ==================== Usuarios API ====================

/**
 * Actualiza datos del usuario autenticado actual
 */
export async function updateUsuario(data: UsuarioUpdate): Promise<Usuario> {
  const response = await fetchConAuth('/auth/me', {
    method: 'PUT',
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al actualizar usuario');
  }

  return response.json();
}

// ==================== Analytics API ====================

/**
 * Tipo para rendimiento por día
 */
export interface RendimientoDia {
  fecha: string;
  habitos: number;
  habitos_completados: number;
}

/**
 * Tipo para cumplimiento de hábitos
 */
export interface CumplimientoHabito {
  fecha: string;
  nombre_habito: string;
  habitos_completados: number;
  total_habitos: number;
  color: string;
}

/**
 * Obtiene el rendimiento de hábitos por día en un rango de fechas
 */
export async function getRendimientoPorDia(
  fechaInicio: string,
  fechaFin: string
): Promise<RendimientoDia[]> {
  const response = await fetchConAuth(
    `/analisis/rendimiento?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al obtener rendimiento por día');
  }

  return response.json();
}

/**
 * Obtiene el cumplimiento de cada hábito en un rango de fechas
 */
export async function getCumplimientoHabitos(
  fechaInicio: string,
  fechaFin: string
): Promise<CumplimientoHabito[]> {
  const response = await fetchConAuth(
    `/analisis/cumplimiento?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al obtener cumplimiento de hábitos');
  }

  return response.json();
}

// ==================== Charts / Series (stubs) ====================

export interface ChartPoint {
  label: string;
  value: number;
  series: string;
}

export interface ChartSeries {
  categories: string[];
  data: number[];
}

export interface ChartData {
  series: string[];
}

// Dev-friendly stub implementations to satisfy imports during build.
// These return empty data and no-op for create/delete. Replace with real API calls if backend endpoints exist.

export async function getSeries(): Promise<string[]> {
  return Promise.resolve([]);
}

export async function getSeriesData(name: string): Promise<ChartSeries> {
  return Promise.resolve({ categories: [], data: [] });
}

export async function getChartData(name: string): Promise<ChartData> {
  const s = await getSeries();
  return Promise.resolve({ series: s });
}

export async function createBulkChartData(points: ChartPoint[]): Promise<void> {
  return Promise.resolve();
}

export async function deleteSeries(name: string): Promise<void> {
  return Promise.resolve();
}

// ==================== Items API (stubs) ====================

export interface Item {
  id: number;
  name: string;
  description?: string;
  value: number;
  category?: string;
  created_at: string;
}

export interface ItemCreate {
  name: string;
  description?: string;
  value: number;
  category?: string;
}

export async function getItems(): Promise<Item[]> {
  return Promise.resolve([]);
}

export async function createItem(data: ItemCreate): Promise<Item> {
  return Promise.resolve({ id: 0, name: data.name, description: data.description ?? '', value: data.value, category: data.category ?? '', created_at: new Date().toISOString() });
}

export async function deleteItem(id: number): Promise<void> {
  return Promise.resolve();
}

// ==================== Convenience wrappers ====================

export async function getHabitosByUsuario(usuarioId: number): Promise<Habito[]> {
  // Backend endpoints likely return habits for the authenticated user; this stub returns all habits.
  return getHabitos();
}

