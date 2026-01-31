#!/bin/bash
# Script para ejecutar migraciones de Alembic en producción

set -e

echo "🔄 Ejecutando migraciones de Alembic..."
echo ""

# Variables de entorno (ajusta según tu configuración)
export DATABASE_URL="postgresql+asyncpg://postgres:x4jaDXDfOsqnSc@marco-pro.cpgy0aesyzqd.sa-east-1.rds.amazonaws.com:5432/marco"

cd /home/jorge/pp/marco/backend

echo "📋 Historial de migraciones actual:"
alembic history

echo ""
echo "📊 Versión actual de la base de datos:"
alembic current

echo ""
echo "⬆️  Aplicando migraciones pendientes..."
alembic upgrade head

echo ""
echo "✅ Migraciones completadas"
echo ""
echo "📊 Versión final de la base de datos:"
alembic current
