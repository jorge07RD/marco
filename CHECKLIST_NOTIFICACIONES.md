# ✅ Checklist de Implementación de Notificaciones Push

Usa este checklist para verificar que todo esté correctamente implementado y configurado.

## 📋 Backend

### Código
- [x] `backend/app/models.py` - Modelo Usuario actualizado con campos de notificaciones
- [x] `backend/app/models.py` - Modelo PushSubscription creado
- [x] `backend/app/schemas.py` - Schemas de Usuario actualizados
- [x] `backend/app/schemas.py` - Schemas de PushSubscription creados
- [x] `backend/app/config.py` - Variables VAPID agregadas
- [x] `backend/app/routers/notifications.py` - Router completo creado
- [x] `backend/app/services/scheduler.py` - Scheduler implementado
- [x] `backend/app/main.py` - Router y scheduler integrados
- [x] `backend/pyproject.toml` - Dependencias agregadas

### Archivos Auxiliares
- [x] `backend/migrations_add_notifications.sql` - Script de migración creado

## 📋 Frontend

### Código
- [x] `frontend/static/sw.js` - Service Worker implementado
- [x] `frontend/src/lib/notifications.ts` - Utilidades completas
- [x] `frontend/src/lib/api.ts` - Interfaces actualizadas
- [x] `frontend/src/routes/settings/+page.svelte` - UI completa

## 📋 Documentación

- [x] `NOTIFICACIONES_SETUP.md` - Guía completa de configuración
- [x] `IMPLEMENTACION_NOTIFICACIONES.md` - Resumen de implementación
- [x] `setup_notifications.sh` - Script automatizado

## 🔧 Configuración Requerida (Por Hacer)

### 1. Instalar Dependencias Backend
```bash
cd backend
uv sync
```
- [ ] Dependencias instaladas correctamente
- [ ] Sin errores de importación

### 2. Generar Claves VAPID
```bash
./setup_notifications.sh
```
O manualmente:
```bash
npx web-push generate-vapid-keys
```
- [ ] Claves VAPID generadas
- [ ] Public key copiada
- [ ] Private key copiada

### 3. Configurar Variables de Entorno
Editar `backend/.env`:
```env
VAPID_PUBLIC_KEY=<tu_clave_publica>
VAPID_PRIVATE_KEY=<tu_clave_privada>
VAPID_CLAIMS_EMAIL=mailto:tu@email.com
```
- [ ] `VAPID_PUBLIC_KEY` configurada
- [ ] `VAPID_PRIVATE_KEY` configurada
- [ ] `VAPID_CLAIMS_EMAIL` configurado con email real

### 4. Migrar Base de Datos
```bash
cd backend
sqlite3 app.db < migrations_add_notifications.sql
```
- [ ] Migración ejecutada sin errores
- [ ] Tabla `push_subscriptions` creada
- [ ] Columnas de notificaciones agregadas a `usuarios`

Verificar:
```bash
sqlite3 app.db "PRAGMA table_info(usuarios);"
sqlite3 app.db "PRAGMA table_info(push_subscriptions);"
```
- [ ] Columna `notificaciones_activas` existe
- [ ] Columna `recordatorios_activos` existe
- [ ] Columna `hora_recordatorio` existe
- [ ] Columna `timezone` existe
- [ ] Tabla `push_subscriptions` tiene todas las columnas

## 🧪 Pruebas

### Iniciar Aplicación
```bash
# Terminal 1
cd backend
uv run uvicorn app.main:app --reload

# Terminal 2
cd frontend
npm run dev
```

- [ ] Backend inicia sin errores
- [ ] Mensaje "Scheduler de recordatorios iniciado" aparece
- [ ] Frontend inicia sin errores
- [ ] No hay errores en consola del navegador

### Probar Funcionalidad

#### Paso 1: Verificar Endpoints
Abrir http://localhost:8000/docs
- [ ] Endpoint `/api/notifications/vapid-public-key` visible
- [ ] Endpoint `/api/notifications/subscribe` visible
- [ ] Endpoint `/api/notifications/unsubscribe` visible
- [ ] Endpoint `/api/notifications/test` visible

#### Paso 2: Obtener Clave Pública
GET http://localhost:8000/api/notifications/vapid-public-key
- [ ] Retorna `{"publicKey": "..."}`
- [ ] La clave coincide con la configurada en `.env`

#### Paso 3: Probar UI
1. Abrir http://localhost:5173
2. Iniciar sesión
3. Ir a Ajustes (⚙️)

- [ ] Sección "🔔 Notificaciones" visible
- [ ] Toggle "Notificaciones push" funciona
- [ ] Toggle "Recordatorios diarios" funciona (cuando notificaciones están activas)
- [ ] Selector de hora funciona
- [ ] Selector de zona horaria funciona
- [ ] Botón "Guardar cambios" funciona

#### Paso 4: Activar Notificaciones
1. Click en toggle "Notificaciones push"
2. Permitir notificaciones cuando el navegador pregunte

- [ ] Permiso otorgado correctamente
- [ ] Toggle permanece activado
- [ ] Mensaje de éxito aparece
- [ ] Service Worker registrado (ver en DevTools > Application > Service Workers)

#### Paso 5: Probar Notificación
1. Click en "🔔 Enviar notificación de prueba"

- [ ] Notificación aparece en el sistema
- [ ] Título: "🎯 Notificación de Prueba"
- [ ] Cuerpo: "¡Tu sistema de notificaciones funciona correctamente!"
- [ ] Click en notificación enfoca/abre la aplicación

#### Paso 6: Probar Recordatorios Automáticos
1. Configurar hora a 1-2 minutos en el futuro
2. Activar "Recordatorios diarios"
3. Click en "Guardar cambios"
4. Esperar a que llegue la hora

- [ ] Notificación automática recibida
- [ ] Título: "🎯 ¡Hora de revisar tus hábitos!"
- [ ] Hora correcta según zona horaria configurada

## 🐛 Troubleshooting

### Backend no inicia
- [ ] Verificar que las dependencias estén instaladas: `uv sync`
- [ ] Verificar que el archivo `.env` exista
- [ ] Verificar que las claves VAPID estén configuradas

### Frontend no se suscribe
- [ ] Verificar permisos del navegador (ícono de candado en URL)
- [ ] Verificar que Service Worker esté registrado
- [ ] Abrir DevTools > Console y buscar errores
- [ ] Verificar que VAPID public key sea válida

### Notificaciones no llegan
- [ ] Verificar que el backend esté corriendo
- [ ] Verificar que el scheduler esté activo (ver logs)
- [ ] Verificar zona horaria configurada
- [ ] Verificar hora configurada vs hora actual

### Error "VAPID keys no configuradas"
- [ ] Verificar archivo `.env`
- [ ] Reiniciar el servidor backend
- [ ] Verificar que las claves no tengan espacios o saltos de línea

## 📊 Estado Final

Marcar cuando todo esté completo:

- [ ] ✅ Backend configurado y funcionando
- [ ] ✅ Frontend configurado y funcionando
- [ ] ✅ Base de datos migrada
- [ ] ✅ Notificaciones de prueba funcionan
- [ ] ✅ Recordatorios automáticos funcionan
- [ ] ✅ Sin errores en consola
- [ ] ✅ Sin errores en logs del backend

## 🎉 Sistema Listo

Cuando todas las casillas estén marcadas, el sistema de notificaciones push está **completamente funcional y listo para producción**.

---

**Nota**: Este checklist puede imprimirse o usarse como guía durante la implementación.
