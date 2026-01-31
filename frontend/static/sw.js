/**
 * Service Worker para notificaciones push
 * Marco Habit Tracker
 */

// Versión del service worker para cache busting
const SW_VERSION = '1.0.0';

// Evento de instalación
self.addEventListener('install', (event) => {
  console.log('[SW] Service Worker instalado, versión:', SW_VERSION);
  // Activar inmediatamente sin esperar
  self.skipWaiting();
});

// Evento de activación
self.addEventListener('activate', (event) => {
  console.log('[SW] Service Worker activado');
  // Tomar control de todas las páginas inmediatamente
  event.waitUntil(clients.claim());
});

// Evento de notificación push
self.addEventListener('push', (event) => {
  console.log('[SW] Push recibido');

  let data = {
    title: 'Marco Habit Tracker',
    body: 'Tienes una notificación',
    icon: '/favicon.png',
    badge: '/favicon.png',
    tag: 'marco-notification',
    data: { url: '/' }
  };

  // Intentar parsear los datos del push
  if (event.data) {
    try {
      const payload = event.data.json();
      data = {
        title: payload.title || data.title,
        body: payload.body || data.body,
        icon: payload.icon || data.icon,
        badge: payload.badge || data.badge,
        tag: payload.tag || data.tag,
        data: payload.data || data.data
      };
    } catch (e) {
      console.error('[SW] Error parseando datos push:', e);
      // Usar datos por defecto si falla el parsing
      data.body = event.data.text() || data.body;
    }
  }

  const options = {
    body: data.body,
    icon: data.icon,
    badge: data.badge,
    tag: data.tag,
    data: data.data,
    vibrate: [100, 50, 100],
    requireInteraction: false,
    actions: [
      {
        action: 'open',
        title: 'Abrir'
      },
      {
        action: 'dismiss',
        title: 'Cerrar'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Evento de clic en notificación
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Clic en notificación:', event.action);

  event.notification.close();

  // Si el usuario hizo clic en "dismiss", no hacer nada más
  if (event.action === 'dismiss') {
    return;
  }

  // URL a abrir (por defecto la raíz)
  const urlToOpen = event.notification.data?.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((windowClients) => {
        // Buscar si ya hay una ventana abierta con la app
        for (const client of windowClients) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            // Navegar a la URL y enfocar
            client.navigate(urlToOpen);
            return client.focus();
          }
        }
        // Si no hay ventana abierta, abrir una nueva
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

// Evento de cierre de notificación
self.addEventListener('notificationclose', (event) => {
  console.log('[SW] Notificación cerrada');
});

// Manejar errores de suscripción push
self.addEventListener('pushsubscriptionchange', (event) => {
  console.log('[SW] Suscripción push cambió');
  // Aquí se podría intentar re-suscribir automáticamente
  // pero por ahora solo logueamos el evento
});
