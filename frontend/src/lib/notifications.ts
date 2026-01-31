/**
 * Utilidades para manejar notificaciones push en el frontend
 */

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Verifica si el navegador soporta notificaciones push
 */
export function isNotificationSupported(): boolean {
  return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
}

/**
 * Verifica si ya hay una suscripción activa
 */
export async function isSubscribed(): Promise<boolean> {
  if (!isNotificationSupported()) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    return subscription !== null;
  } catch (error) {
    console.error('Error verificando suscripción:', error);
    return false;
  }
}

/**
 * Obtiene la clave pública VAPID del servidor
 */
async function getVapidPublicKey(): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/notifications/vapid-public-key`);
  if (!response.ok) {
    throw new Error('Error obteniendo clave VAPID');
  }
  const data = await response.json();
  return data.publicKey;
}

/**
 * Convierte una cadena base64 a Uint8Array (necesario para VAPID)
 */
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

/**
 * Registra el Service Worker si no está registrado
 */
async function registerServiceWorker(): Promise<ServiceWorkerRegistration> {
  const registration = await navigator.serviceWorker.register('/sw.js', {
    scope: '/'
  });
  
  console.log('Service Worker registrado:', registration);
  
  // Esperar a que esté listo
  await navigator.serviceWorker.ready;
  
  return registration;
}

/**
 * Suscribe al usuario a las notificaciones push
 * @param token - Token JWT del usuario
 */
export async function subscribeToPush(token: string): Promise<boolean> {
  if (!isNotificationSupported()) {
    throw new Error('Tu navegador no soporta notificaciones push');
  }

  try {
    // Solicitar permiso de notificaciones
    const permission = await Notification.requestPermission();
    
    if (permission !== 'granted') {
      throw new Error('Permiso de notificaciones denegado');
    }

    // Registrar Service Worker
    const registration = await registerServiceWorker();

    // Obtener clave pública VAPID
    const vapidPublicKey = await getVapidPublicKey();
    const applicationServerKey = urlBase64ToUint8Array(vapidPublicKey);

    // Crear suscripción
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: applicationServerKey
    });

    // Enviar suscripción al servidor
    const response = await fetch(`${API_BASE_URL}/notifications/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(subscription)
    });

    if (!response.ok) {
      throw new Error('Error al guardar la suscripción en el servidor');
    }

    console.log('Suscripción creada correctamente');
    return true;

  } catch (error) {
    console.error('Error suscribiendo a notificaciones:', error);
    throw error;
  }
}

/**
 * Cancela la suscripción a notificaciones push
 * @param token - Token JWT del usuario
 */
export async function unsubscribeFromPush(token: string): Promise<boolean> {
  if (!isNotificationSupported()) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();

    if (!subscription) {
      console.log('No hay suscripción activa');
      return true;
    }

    // Eliminar suscripción del navegador
    await subscription.unsubscribe();

    // Eliminar suscripción del servidor
    const response = await fetch(
      `${API_BASE_URL}/notifications/unsubscribe?endpoint=${encodeURIComponent(subscription.endpoint)}`,
      {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      console.error('Error eliminando suscripción del servidor');
    }

    console.log('Suscripción cancelada correctamente');
    return true;

  } catch (error) {
    console.error('Error cancelando suscripción:', error);
    throw error;
  }
}

/**
 * Envía una notificación de prueba
 * @param token - Token JWT del usuario
 */
export async function sendTestNotification(token: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/notifications/test`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error enviando notificación de prueba');
  }

  const result = await response.json();
  console.log(result.message);
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
