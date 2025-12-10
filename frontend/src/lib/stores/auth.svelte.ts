/**
 * Store de autenticación usando Svelte 5 runes
 * Maneja el estado de autenticación, token y usuario actual
 */
import type { Usuario } from '$lib/api';

interface AuthState {
  isAuthenticated: boolean;
  usuario: Usuario | null;
  token: string | null;
}

// Claves para localStorage
const TOKEN_KEY = 'auth_token';
const USUARIO_KEY = 'auth_usuario';

// Inicializar el estado desde localStorage si existe
function getInitialState(): AuthState {
  if (typeof window === 'undefined') {
    return {
      isAuthenticated: false,
      usuario: null,
      token: null
    };
  }

  const token = localStorage.getItem(TOKEN_KEY);
  const usuarioStr = localStorage.getItem(USUARIO_KEY);

  if (token && usuarioStr) {
    try {
      const usuario = JSON.parse(usuarioStr);
      return {
        isAuthenticated: true,
        usuario,
        token
      };
    } catch (e) {
      // Si hay error al parsear, limpiar localStorage
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USUARIO_KEY);
    }
  }

  return {
    isAuthenticated: false,
    usuario: null,
    token: null
  };
}

// Estado reactivo usando runes de Svelte 5
const state = $state<AuthState>(getInitialState());

/**
 * Store de autenticación
 */
export const authStore = {
  // Getters reactivos
  get isAuthenticated() {
    return state.isAuthenticated;
  },
  get usuario() {
    return state.usuario;
  },
  get token() {
    return state.token;
  },

  /**
   * Inicia sesión guardando el token y el usuario
   */
  login(token: string, usuario: Usuario) {
    state.isAuthenticated = true;
    state.usuario = usuario;
    state.token = token;

    // Guardar en localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USUARIO_KEY, JSON.stringify(usuario));
    }
  },

  /**
   * Cierra sesión eliminando el token y el usuario
   */
  logout() {
    state.isAuthenticated = false;
    state.usuario = null;
    state.token = null;

    // Limpiar localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USUARIO_KEY);
    }
  },

  /**
   * Actualiza los datos del usuario
   */
  updateUsuario(usuario: Usuario) {
    state.usuario = usuario;

    // Actualizar en localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem(USUARIO_KEY, JSON.stringify(usuario));
    }
  }
};
