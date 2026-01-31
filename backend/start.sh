#!/bin/bash
set -e

echo "=================================="
echo "🔄 Iniciando aplicación Marco"
echo "=================================="

echo ""
echo "📊 Verificando configuración de base de datos..."
echo "DATABASE_URL: ${DATABASE_URL:-No configurada}"

echo ""
echo "🔄 Ejecutando migraciones de Alembic..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migraciones completadas exitosamente"
else
    echo "❌ Error en las migraciones"
    exit 1
fi

echo ""
echo "🚀 Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
