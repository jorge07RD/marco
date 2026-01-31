/**
 * Servicio de notificaciones push para el frontend
 * Marco Habit Tracker
 */

import { obtenerToken } from './api';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

// Zonas horarias soportadas
export const TIMEZONES = [
  { value: 'America/Santo_Domingo', label: 'Rep. Dominicana (AST)' },
  { value: 'America/New_York', label: 'Nueva York (EST)' },
  { value: 'America/Los_Angeles', label: 'Los Angeles (PST)' },
  { value: 'America/Mexico_City', label: 'Mexico (CST)' },
  { value: 'America/Bogota', label: 'Colombia (COT)' },
  { value: 'America/Lima', label: 'Peru (PET)' },
  { value: 'America/Santiago', label: 'Chile (CLT)' },
  { value: 'America/Argentina/Buenos_Aires', label: 'Argentina (ART)' },
  { value: 'Europe/Madrid', label: 'Espana (CET)' },
  { value: 'Europe/London', label: 'Reino Unido (GMT)' }
];

export interface NotificationPreferences {
  notificaciones_activas: boolean;
  hora_recordatorio: string;
  timezone: string;
}

export interface PushSubscription {
  id: number;
  usuario_id: number;
  endpoint: string;
  activa: boolean;
  created_at: string;
}

/**
 * Verifica si las notificaciones push están soportadas
 */
export function isPushSupported(): boolean {
  return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
}

/**
 * Obtiene el estado actual del permiso de notificaciones
 */
export function getNotificationPermission(): NotificationPermission {
  if (!('Notification' in window)) {
    return 'denied';
  }
  return Notification.permission;
}

/**
 * Solicita permiso para notificaciones
 */
export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!('Notification' in window)) {
    return 'denied';
  }
  return await Notification.requestPermission();
}

/**
 * Registra el service worker
 */
export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (!('serviceWorker' in navigator)) {
    console.warn('Service Worker no soportado');
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/'
    });
    console.log('Service Worker registrado:', registration.scope);
    return registration;
  } catch (error) {
    console.error('Error registrando Service Worker:', error);
    return null;
  }
}

/**
 * Obtiene la clave pública VAPID del servidor
 */
export async function getVapidPublicKey(): Promise<string | null> {
  try {
    const response = await fetch(`${API_BASE}/notifications/vapid-public-key`);
    if (!response.ok) {
      throw new Error('No se pudo obtener la clave VAPID');
    }
    const data = await response.json();
    return data.public_key;
  } catch (error) {
    console.error('Error obteniendo clave VAPID:', error);
    return null;
  }
}

/**
 * Convierte una clave VAPID base64 a Uint8Array
 */
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

/**
 * Suscribe al usuario a notificaciones push
 */
export async function subscribeToPush(): Promise<boolean> {
  console.log('[Push] Iniciando suscripción...');
  
  if (!isPushSupported()) {
    console.warn('[Push] Push no soportado');
    return false;
  }

  // Solicitar permiso si no está concedido
  const permission = await requestNotificationPermission();
  console.log('[Push] Permiso:', permission);
  
  if (permission !== 'granted') {
    console.warn('[Push] Permiso de notificaciones denegado');
    return false;
  }

  try {
    // Registrar service worker
    console.log('[Push] Registrando service worker...');
    const registration = await registerServiceWorker();
    if (!registration) {
      console.error('[Push] No se pudo registrar el service worker');
      return false;
    }
    console.log('[Push] Service worker registrado:', registration.scope);

    // Esperar a que el service worker esté activo
    console.log('[Push] Esperando service worker ready...');
    await navigator.serviceWorker.ready;
    console.log('[Push] Service worker ready');

    // Obtener clave VAPID
    console.log('[Push] Obteniendo clave VAPID...');
    const vapidKey = await getVapidPublicKey();
    if (!vapidKey) {
      console.error('[Push] No se pudo obtener la clave VAPID');
      return false;
    }
    console.log('[Push] Clave VAPID obtenida:', vapidKey.substring(0, 20) + '...');

    // Crear suscripción push
    console.log('[Push] Creando suscripción push...');
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidKey) as BufferSource
    });
    console.log('[Push] Suscripción creada:', subscription.endpoint);

    // Extraer datos de la suscripción
    const subscriptionJson = subscription.toJSON();
    const token = obtenerToken();

    if (!token) {
      console.error('[Push] No hay token de autenticación');
      return false;
    }
    console.log('[Push] Token de autenticación presente');

    // Enviar suscripción al servidor
    console.log('[Push] Enviando suscripción al servidor...');
    const response = await fetch(`${API_BASE}/notifications/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        endpoint: subscriptionJson.endpoint,
        p256dh_key: subscriptionJson.keys?.p256dh,
        auth_key: subscriptionJson.keys?.auth,
        user_agent: navigator.userAgent
      })
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('[Push] Error del servidor:', error);
      throw new Error(error.detail || 'Error al suscribirse');
    }

    console.log('[Push] Suscripción push creada exitosamente');
    return true;
  } catch (error) {
    console.error('[Push] Error en suscripción push:', error);
    return false;
  }
}

/**
 * Cancela la suscripción push
 */
export async function unsubscribeFromPush(): Promise<boolean> {
  if (!('serviceWorker' in navigator)) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();

    if (!subscription) {
      console.log('No hay suscripción activa');
      return true;
    }

    const endpoint = subscription.endpoint;
    const token = obtenerToken();

    // Cancelar suscripción en el navegador
    await subscription.unsubscribe();

    // Notificar al servidor
    if (token) {
      await fetch(`${API_BASE}/notifications/unsubscribe?endpoint=${encodeURIComponent(endpoint)}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    }

    console.log('Suscripción push cancelada');
    return true;
  } catch (error) {
    console.error('Error cancelando suscripción:', error);
    return false;
  }
}

/**
 * Verifica si hay una suscripción push activa
 */
export async function hasActivePushSubscription(): Promise<boolean> {
  if (!('serviceWorker' in navigator)) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    return subscription !== null;
  } catch (error) {
    return false;
  }
}

/**
 * Obtiene las preferencias de notificación del servidor
 */
export async function getNotificationPreferences(): Promise<NotificationPreferences | null> {
  const token = obtenerToken();
  if (!token) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE}/notifications/preferences`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Error obteniendo preferencias');
    }

    return await response.json();
  } catch (error) {
    console.error('Error obteniendo preferencias:', error);
    return null;
  }
}

/**
 * Actualiza las preferencias de notificación
 */
export async function updateNotificationPreferences(
  preferences: Partial<NotificationPreferences>
): Promise<NotificationPreferences | null> {
  const token = obtenerToken();
  if (!token) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE}/notifications/preferences`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(preferences)
    });

    if (!response.ok) {
      throw new Error('Error actualizando preferencias');
    }

    return await response.json();
  } catch (error) {
    console.error('Error actualizando preferencias:', error);
    return null;
  }
}

/**
 * Envía una notificación de prueba
 */
export async function sendTestNotification(
  title?: string,
  body?: string
): Promise<{ success: boolean; message: string }> {
  const token = obtenerToken();
  if (!token) {
    return { success: false, message: 'No hay sesión activa' };
  }

  try {
    const response = await fetch(`${API_BASE}/notifications/test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ title, body })
    });

    const data = await response.json();

    if (!response.ok) {
      return { success: false, message: data.detail || 'Error enviando notificación' };
    }

    return { success: true, message: data.message || 'Notificación enviada' };
  } catch (error) {
    console.error('Error enviando notificación de prueba:', error);
    return { success: false, message: 'Error de conexión' };
  }
}
