#!/bin/bash
set -e

echo "=================================="
echo "🔄 Iniciando aplicación Marco"
echo "=================================="

echo ""
echo "📊 Verificando configuración de base de datos..."
echo "DATABASE_URL: ${DATABASE_URL:-No configurada}"

echo ""echo "🔍 Verificando y preparando base de datos para migraciones..."
python verify_and_stamp.py

echo ""echo "� Verificando versión actual de Alembic..."
alembic current || echo "⚠️  No hay versión actual (primera migración)"

echo ""
echo "🔄 Ejecutando migraciones de Alembic..."
alembic upgrade head -v

echo ""
echo "✅ Migraciones completadas exitosamente"

echo ""
echo "🔍 Versión actual después de migración..."
alembic current

echo ""
echo "🚀 Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
