-- Migración para agregar soporte de notificaciones push
-- Ejecutar con: sqlite3 app.db < migrations_add_notifications.sql

-- Agregar columnas de notificaciones a la tabla usuarios
ALTER TABLE usuarios ADD COLUMN notificaciones_activas BOOLEAN DEFAULT 0;
ALTER TABLE usuarios ADD COLUMN recordatorios_activos BOOLEAN DEFAULT 0;
ALTER TABLE usuarios ADD COLUMN hora_recordatorio VARCHAR DEFAULT '08:00';
ALTER TABLE usuarios ADD COLUMN timezone VARCHAR DEFAULT 'America/Mexico_City';

-- Crear tabla de suscripciones push
CREATE TABLE push_subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    endpoint VARCHAR NOT NULL UNIQUE,
    p256dh_key VARCHAR NOT NULL,
    auth_key VARCHAR NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Crear índice para búsquedas rápidas por usuario
CREATE INDEX idx_push_subscriptions_usuario_id ON push_subscriptions(usuario_id);
