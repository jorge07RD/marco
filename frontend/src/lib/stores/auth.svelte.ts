/**
 * Store de autenticación global usando Svelte 5 Runes
 *
 * Maneja el estado del usuario autenticado, login, logout, y verificación de token.
 */

import { obtenerToken, obtenerUsuarioActual, logout as apiLogout } from '$lib/api';
import type { Usuario } from '$lib/api';

class AuthStore {
  // Estado reactivo del usuario (null si no está autenticado)
  user = $state<Usuario | null>(null);

  // Estado de carga inicial
  loading = $state(true);

  // Derived state: si está autenticado
  get isAuthenticated() {
    return this.user !== null;
  }

  /**
   * Inicializa el store verificando si hay un token válido
   * Se debe llamar en el layout raíz de la aplicación
   */
  async init() {
    const token = obtenerToken();

    // Si no hay token, no está autenticado
    if (!token) {
      this.loading = false;
      return;
    }

    try {
      // Verificar el token obteniendo los datos del usuario
      this.user = await obtenerUsuarioActual();
    } catch (error) {
      console.error('Error al verificar token:', error);
      // Si el token es inválido, hacer logout
      apiLogout();
      this.user = null;
    } finally {
      this.loading = false;
    }
  }

  /**
   * Establece el usuario autenticado
   * Se llama después de login o registro exitoso
   */
  setUser(user: Usuario) {
    this.user = user;
  }

  /**
   * Cierra la sesión del usuario
   */
  logout() {
    this.user = null;
    apiLogout();
  }

  /**
   * Actualiza los datos del usuario en el store
   */
  updateUser(updates: Partial<Usuario>) {
    if (this.user) {
      this.user = { ...this.user, ...updates };
    }
  }
}

// Exportar instancia única del store
export const authStore = new AuthStore();
