import { browser } from '$app/environment';
import { goto } from '$app/navigation';

export const ssr = false; // Disable SSR for client-side auth

export async function load({ url }) {
  if (browser) {
    const token = localStorage.getItem('auth_token');
    const publicRoutes = ['/login', '/register'];
    const isPublicRoute = publicRoutes.includes(url.pathname);

    // Si no hay token y no está en una ruta pública, redireccionar al login
    if (!token && !isPublicRoute) {
      goto('/login');
      return {};
    }

    // Si hay token y está en login/register, redireccionar al home
    if (token && isPublicRoute) {
      goto('/');
      return {};
    }
  }

  return {};
}
