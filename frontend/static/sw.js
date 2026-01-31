// Service Worker para manejar notificaciones push
// Este archivo debe estar en /static para ser accesible

self.addEventListener('install', (event) => {
  console.log('Service Worker instalado');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activado');
  event.waitUntil(self.clients.claim());
});

// Escuchar evento push
self.addEventListener('push', (event) => {
  console.log('Notificación push recibida');
  
  let notificationData = {
    title: '🎯 Marco Habit Tracker',
    body: 'Tienes una nueva notificación',
    icon: '/favicon.ico',
    badge: '/favicon.ico',
    tag: 'default'
  };
  
  // Si hay datos en el push, parsearlos
  if (event.data) {
    try {
      notificationData = event.data.json();
    } catch (e) {
      console.error('Error parseando datos de notificación:', e);
    }
  }
  
  const promiseChain = self.registration.showNotification(
    notificationData.title,
    {
      body: notificationData.body,
      icon: notificationData.icon || '/favicon.ico',
      badge: notificationData.badge || '/favicon.ico',
      tag: notificationData.tag || 'default',
      requireInteraction: false,
      data: {
        dateOfArrival: Date.now(),
        primaryKey: notificationData.tag
      }
    }
  );
  
  event.waitUntil(promiseChain);
});

// Escuchar clic en notificación
self.addEventListener('notificationclick', (event) => {
  console.log('Notificación clickeada');
  
  event.notification.close();
  
  // Abrir o enfocar la aplicación
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Si ya hay una ventana abierta, enfocarla
        for (let i = 0; i < clientList.length; i++) {
          const client = clientList[i];
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            return client.focus();
          }
        }
        // Si no hay ventana abierta, abrir una nueva
        if (self.clients.openWindow) {
          return self.clients.openWindow('/');
        }
      })
  );
});

// Manejo de errores de push
self.addEventListener('pushsubscriptionchange', (event) => {
  console.log('Suscripción push cambió');
  
  event.waitUntil(
    self.registration.pushManager.subscribe(event.oldSubscription.options)
      .then((subscription) => {
        // Enviar nueva suscripción al servidor
        return fetch('/api/notifications/subscribe', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(subscription)
        });
      })
  );
});
