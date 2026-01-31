# 🔔 Sistema de Notificaciones Push - Guía de Configuración

## ✅ Implementación Completada

Se ha implementado exitosamente un sistema completo de notificaciones push para la aplicación de seguimiento de hábitos.

## 📋 Pasos para Activar el Sistema

### 1. Instalar Dependencias del Backend

```bash
cd backend
uv sync
```

Esto instalará las nuevas dependencias:
- `pywebpush>=2.0.0` - Para enviar notificaciones push
- `apscheduler>=3.10.0` - Para programar recordatorios
- `pytz>=2024.1` - Para manejo de zonas horarias

### 2. Generar Claves VAPID

Las claves VAPID son necesarias para la autenticación de notificaciones push:

```bash
npx web-push generate-vapid-keys
```

Este comando generará dos claves:
- **Public Key**: Para el frontend (suscripción)
- **Private Key**: Para el backend (envío de notificaciones)

### 3. Configurar Variables de Entorno

Crear o actualizar el archivo `backend/.env` con las claves VAPID:

```env
# Notificaciones Push - VAPID Keys
VAPID_PUBLIC_KEY=<tu_clave_publica_aqui>
VAPID_PRIVATE_KEY=<tu_clave_privada_aqui>
VAPID_CLAIMS_EMAIL=mailto:tu@email.com
```

**Importante:** Reemplaza los valores con las claves generadas en el paso anterior.

### 4. Migrar la Base de Datos

Ejecutar el script SQL para agregar las nuevas tablas y columnas:

```bash
cd backend
sqlite3 app.db < migrations_add_notifications.sql
```

O manualmente desde SQLite:

```bash
sqlite3 app.db
.read migrations_add_notifications.sql
.quit
```

### 5. Verificar Migraciones

Confirmar que las columnas se agregaron correctamente:

```bash
sqlite3 app.db "PRAGMA table_info(usuarios);"
sqlite3 app.db "PRAGMA table_info(push_subscriptions);"
```

Deberías ver las nuevas columnas en `usuarios`:
- `notificaciones_activas`
- `recordatorios_activos`
- `hora_recordatorio`
- `timezone`

Y la nueva tabla `push_subscriptions` con sus columnas.

### 6. Iniciar el Backend

```bash
cd backend
uv run uvicorn app.main:app --reload
```

En la consola deberías ver:
```
✅ Scheduler de recordatorios iniciado (ejecuta cada minuto)
```

### 7. Iniciar el Frontend

```bash
cd frontend
npm run dev
```

## 🧪 Probar el Sistema

### 1. Activar Notificaciones

1. Ir a **Ajustes** (⚙️) en la aplicación
2. En la sección **🔔 Notificaciones**:
   - Activar el toggle "Notificaciones push"
   - El navegador solicitará permiso → **Permitir**
   - Debería aparecer un mensaje de éxito

### 2. Configurar Recordatorios

1. Activar el toggle "Recordatorios diarios"
2. Configurar la hora deseada (ej: 08:00)
3. Seleccionar tu zona horaria
4. Click en "Guardar cambios"

### 3. Enviar Notificación de Prueba

1. Click en el botón **"🔔 Enviar notificación de prueba"**
2. Deberías recibir una notificación instantánea
3. Si no aparece, revisar:
   - Permisos del navegador
   - Consola de desarrollo (F12)
   - Logs del backend

### 4. Probar Recordatorios Automáticos

Para probar que los recordatorios funcionan:

1. Configurar la hora a 1-2 minutos en el futuro
2. Activar recordatorios
3. Esperar a que llegue la hora configurada
4. Deberías recibir la notificación automáticamente

## 📁 Archivos Modificados/Creados

### Backend

| Archivo | Tipo |
|---------|------|
| `backend/app/models.py` | Modificado - Agregados campos de notificaciones |
| `backend/app/schemas.py` | Modificado - Nuevos schemas para push |
| `backend/app/config.py` | Modificado - Configuración VAPID |
| `backend/app/main.py` | Modificado - Integración del scheduler |
| `backend/pyproject.toml` | Modificado - Nuevas dependencias |
| `backend/app/routers/notifications.py` | Creado - Endpoints de notificaciones |
| `backend/app/services/scheduler.py` | Creado - Lógica del scheduler |
| `backend/migrations_add_notifications.sql` | Creado - Script de migración |

### Frontend

| Archivo | Tipo |
|---------|------|
| `frontend/static/sw.js` | Creado - Service Worker |
| `frontend/src/lib/notifications.ts` | Creado - Utilidades de notificaciones |
| `frontend/src/lib/api.ts` | Modificado - Interfaces actualizadas |
| `frontend/src/routes/settings/+page.svelte` | Modificado - UI de configuración |

## 🔧 Endpoints Disponibles

### GET `/api/notifications/vapid-public-key`
Retorna la clave pública VAPID para suscribirse.

### POST `/api/notifications/subscribe`
Registra una suscripción push para el usuario autenticado.

**Body:**
```json
{
  "endpoint": "https://fcm.googleapis.com/fcm/send/...",
  "keys": {
    "p256dh": "BKxN...",
    "auth": "qwer..."
  }
}
```

### DELETE `/api/notifications/unsubscribe`
Elimina una suscripción push.

**Query params:** `endpoint`

### POST `/api/notifications/test`
Envía una notificación de prueba al usuario autenticado.

## ⚙️ Funcionamiento del Scheduler

El scheduler ejecuta la función `check_and_send_reminders()` cada minuto:

1. Busca usuarios con `recordatorios_activos=True`
2. Convierte la hora actual a la timezone del usuario
3. Compara con `hora_recordatorio`
4. Si coincide, envía notificación a todas sus suscripciones

**Nota:** Los recordatorios se envían una vez por minuto cuando coincide la hora.

## 🐛 Troubleshooting

### "VAPID keys no configuradas"
- Verificar que las claves estén en `.env`
- Reiniciar el servidor backend
- Confirmar que el archivo `.env` esté en `backend/.env`

### Notificaciones no llegan
- Verificar permisos del navegador (ícono de candado en la barra de direcciones)
- Revisar Service Worker: `chrome://serviceworker-internals/` (Chrome)
- Ver consola del navegador (F12)
- Ver logs del backend

### "Tu navegador no soporta notificaciones"
- Usar Chrome, Firefox, Edge o Safari actualizado
- No funciona en modo incógnito/privado
- Requiere HTTPS en producción (localhost funciona en desarrollo)

### Recordatorios no automáticos
- Verificar que el scheduler esté activo (ver logs al iniciar backend)
- Confirmar zona horaria correcta
- Revisar que `recordatorios_activos=True` en la BD

## 📱 Soporte de Navegadores

| Navegador | Desktop | Mobile |
|-----------|---------|--------|
| Chrome | ✅ | ✅ |
| Firefox | ✅ | ✅ |
| Edge | ✅ | ✅ |
| Safari | ✅ (macOS 16+) | ✅ (iOS 16.4+) |
| Opera | ✅ | ✅ |

## 🚀 Próximos Pasos (Opcional)

1. **Personalizar mensajes**: Editar los mensajes en `scheduler.py`
2. **Estadísticas**: Agregar tracking de notificaciones enviadas
3. **Tipos de notificaciones**: Implementar diferentes tipos (logros, rachas, etc.)
4. **Configuración avanzada**: Permitir múltiples recordatorios al día
5. **Rich notifications**: Agregar imágenes y acciones a las notificaciones

## 📚 Referencias

- [Web Push API - MDN](https://developer.mozilla.org/es/docs/Web/API/Push_API)
- [Service Workers - MDN](https://developer.mozilla.org/es/docs/Web/API/Service_Worker_API)
- [pywebpush - GitHub](https://github.com/web-push-libs/pywebpush)
- [APScheduler - Docs](https://apscheduler.readthedocs.io/)

---

✅ **Sistema listo para usar**. Sigue los pasos de configuración y disfruta de las notificaciones push en tu aplicación de hábitos.
