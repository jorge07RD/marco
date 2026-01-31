# 🔔 Sistema de Notificaciones Push

> Sistema completo de notificaciones push programadas para Marco Habit Tracker

## 🎯 ¿Qué es esto?

Este sistema permite a los usuarios:
- ✅ Recibir **notificaciones push** en su navegador
- ⏰ Configurar **recordatorios diarios** automáticos
- 📱 Recibir notificaciones **incluso con el navegador cerrado**
- 🌍 Configurar **zona horaria** y hora de recordatorio
- 🔔 Probar notificaciones instantáneamente

## 🚀 Inicio Rápido

### 1. Ejecutar Script de Setup
```bash
./setup_notifications.sh
```

### 2. Migrar Base de Datos
```bash
cd backend
sqlite3 app.db < migrations_add_notifications.sql
```

### 3. Instalar Dependencias
```bash
cd backend
uv sync
```

### 4. Iniciar Aplicación
```bash
# Backend
cd backend
uv run uvicorn app.main:app --reload

# Frontend (otra terminal)
cd frontend
npm run dev
```

### 5. Probar
1. Ir a **Ajustes** (⚙️)
2. Activar **"Notificaciones push"**
3. Permitir notificaciones en el navegador
4. Click en **"Enviar notificación de prueba"**

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [**NOTIFICACIONES_SETUP.md**](NOTIFICACIONES_SETUP.md) | 📖 Guía completa paso a paso |
| [**RESUMEN_NOTIFICACIONES.md**](RESUMEN_NOTIFICACIONES.md) | 📊 Resumen ejecutivo visual |
| [**IMPLEMENTACION_NOTIFICACIONES.md**](IMPLEMENTACION_NOTIFICACIONES.md) | 🔧 Documentación técnica |
| [**CHECKLIST_NOTIFICACIONES.md**](CHECKLIST_NOTIFICACIONES.md) | ✅ Lista de verificación |

## 🎨 Interfaz de Usuario

```
┌─────────────────────────────────────────┐
│          🔔 Notificaciones              │
├─────────────────────────────────────────┤
│                                         │
│  Notificaciones push          ●  ON    │
│  Recibe alertas de tus hábitos          │
│                                         │
│  Recordatorios diarios        ●  ON    │
│  Te recordamos completar tus hábitos    │
│                                         │
│  Hora del recordatorio:  [08:00]        │
│  Zona horaria: [America/Mexico_City]    │
│                                         │
│  [ 🔔 Enviar notificación de prueba ]  │
│                                         │
└─────────────────────────────────────────┘
```

## 🔧 Arquitectura

### Backend (FastAPI)
```
├── models.py              → Campos notificaciones en Usuario
├── schemas.py             → Schemas PushSubscription
├── config.py              → Claves VAPID
├── routers/
│   └── notifications.py   → API endpoints
└── services/
    └── scheduler.py       → Recordatorios automáticos
```

### Frontend (Svelte)
```
├── static/
│   └── sw.js                 → Service Worker
└── src/
    ├── lib/
    │   └── notifications.ts  → Lógica notificaciones
    └── routes/
        └── settings/
            └── +page.svelte  → UI configuración
```

## 🌐 Endpoints API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/notifications/vapid-public-key` | Obtener clave pública |
| POST | `/api/notifications/subscribe` | Registrar suscripción |
| DELETE | `/api/notifications/unsubscribe` | Cancelar suscripción |
| POST | `/api/notifications/test` | Enviar notificación prueba |

## 🗄️ Base de Datos

### Nueva Tabla
```sql
CREATE TABLE push_subscriptions (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    endpoint VARCHAR UNIQUE,
    p256dh_key VARCHAR,
    auth_key VARCHAR,
    created_at DATETIME
);
```

### Campos Agregados a `usuarios`
```sql
ALTER TABLE usuarios ADD COLUMN notificaciones_activas BOOLEAN;
ALTER TABLE usuarios ADD COLUMN recordatorios_activos BOOLEAN;
ALTER TABLE usuarios ADD COLUMN hora_recordatorio VARCHAR;
ALTER TABLE usuarios ADD COLUMN timezone VARCHAR;
```

## ⚙️ Configuración Requerida

### Variables de Entorno (`backend/.env`)
```env
VAPID_PUBLIC_KEY=<tu_clave_publica>
VAPID_PRIVATE_KEY=<tu_clave_privada>
VAPID_CLAIMS_EMAIL=mailto:tu@email.com
```

### Generar Claves VAPID
```bash
npx web-push generate-vapid-keys
```

## 🧪 Pruebas

### Test Manual
1. Activar notificaciones en Ajustes
2. Enviar notificación de prueba
3. Verificar que llega correctamente

### Test de Recordatorios
1. Configurar hora 2 minutos adelante
2. Activar recordatorios
3. Esperar a que llegue la hora
4. Verificar notificación automática

## 🐛 Problemas Comunes

### "Tu navegador no soporta notificaciones"
- Usar Chrome, Firefox, Edge o Safari actualizado
- No funciona en modo incógnito

### "VAPID keys no configuradas"
- Verificar archivo `.env`
- Reiniciar el servidor backend

### Notificaciones no llegan
- Verificar permisos del navegador
- Ver Service Worker en DevTools
- Revisar logs del backend

## 📱 Compatibilidad

| Navegador | Desktop | Mobile |
|-----------|:-------:|:------:|
| Chrome | ✅ | ✅ |
| Firefox | ✅ | ✅ |
| Edge | ✅ | ✅ |
| Safari | ✅ (16+) | ✅ (16.4+) |

## 🔐 Seguridad

- ✅ Autenticación JWT en todos los endpoints
- ✅ Claves VAPID únicas por instalación
- ✅ Verificación de permisos del navegador
- ✅ Limpieza automática de suscripciones expiradas

## 📦 Dependencias Agregadas

### Backend
```toml
pywebpush>=2.0.0      # Envío de notificaciones
apscheduler>=3.10.0   # Scheduler de tareas
pytz>=2024.1          # Zonas horarias
```

### Frontend
Ninguna (usa APIs nativas del navegador)

## 🎓 Tecnologías

- **Web Push API**: Notificaciones del navegador
- **Service Workers**: Ejecución en segundo plano
- **VAPID**: Autenticación de servidor
- **APScheduler**: Tareas programadas
- **pytz**: Manejo de zonas horarias

## 🔮 Mejoras Futuras

- [ ] Notificaciones de logros/rachas
- [ ] Múltiples recordatorios al día
- [ ] Rich notifications con imágenes
- [ ] Estadísticas de notificaciones
- [ ] Modo "No molestar"

## 📞 Ayuda

**¿Necesitas ayuda?**
1. Lee [NOTIFICACIONES_SETUP.md](NOTIFICACIONES_SETUP.md) - Guía completa
2. Revisa [Troubleshooting](#-problemas-comunes)
3. Verifica logs del servidor
4. Revisa consola del navegador (F12)

## ✅ Estado

```
╔════════════════════════════════════════╗
║  ✅ SISTEMA COMPLETAMENTE FUNCIONAL   ║
║                                        ║
║  • Código implementado 100%            ║
║  • Documentación completa              ║
║  • Scripts de ayuda incluidos          ║
║  • Listo para usar                     ║
╚════════════════════════════════════════╝
```

---

**Desarrollado para Marco Habit Tracker**  
**Enero 2026**
