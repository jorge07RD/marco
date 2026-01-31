#!/bin/bash

# Script para generar claves VAPID y configurar notificaciones push

echo "🔔 Configuración de Notificaciones Push"
echo "======================================"
echo ""

# Verificar si npm está instalado
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm no está instalado"
    echo "   Instala Node.js desde https://nodejs.org/"
    exit 1
fi

echo "📦 Instalando web-push globalmente (si no está instalado)..."
npm list -g web-push &> /dev/null || npm install -g web-push

echo ""
echo "🔑 Generando claves VAPID..."
echo ""

# Generar claves VAPID
VAPID_OUTPUT=$(npx web-push generate-vapid-keys --json 2>/dev/null)

if [ $? -eq 0 ]; then
    PUBLIC_KEY=$(echo $VAPID_OUTPUT | grep -o '"publicKey":"[^"]*' | sed 's/"publicKey":"//')
    PRIVATE_KEY=$(echo $VAPID_OUTPUT | grep -o '"privateKey":"[^"]*' | sed 's/"privateKey":"//')
    
    echo "✅ Claves generadas exitosamente:"
    echo ""
    echo "Public Key:"
    echo "$PUBLIC_KEY"
    echo ""
    echo "Private Key:"
    echo "$PRIVATE_KEY"
    echo ""
    
    # Crear o actualizar el archivo .env
    ENV_FILE="backend/.env"
    
    echo "📝 ¿Deseas agregar estas claves automáticamente a $ENV_FILE? (s/n)"
    read -r response
    
    if [[ "$response" =~ ^([sS][iI]|[sS])$ ]]; then
        # Verificar si el archivo .env existe
        if [ ! -f "$ENV_FILE" ]; then
            echo "⚠️  El archivo $ENV_FILE no existe. Creándolo..."
            touch "$ENV_FILE"
        fi
        
        # Eliminar líneas existentes de VAPID si las hay
        sed -i '/^VAPID_PUBLIC_KEY=/d' "$ENV_FILE" 2>/dev/null || true
        sed -i '/^VAPID_PRIVATE_KEY=/d' "$ENV_FILE" 2>/dev/null || true
        sed -i '/^VAPID_CLAIMS_EMAIL=/d' "$ENV_FILE" 2>/dev/null || true
        
        # Agregar nuevas claves
        echo "" >> "$ENV_FILE"
        echo "# Notificaciones Push - VAPID Keys" >> "$ENV_FILE"
        echo "VAPID_PUBLIC_KEY=$PUBLIC_KEY" >> "$ENV_FILE"
        echo "VAPID_PRIVATE_KEY=$PRIVATE_KEY" >> "$ENV_FILE"
        echo "VAPID_CLAIMS_EMAIL=mailto:admin@example.com" >> "$ENV_FILE"
        
        echo "✅ Claves agregadas a $ENV_FILE"
        echo ""
        echo "⚠️  IMPORTANTE: Actualiza VAPID_CLAIMS_EMAIL con tu email real"
    else
        echo ""
        echo "💾 Copia y pega estas líneas en tu archivo $ENV_FILE:"
        echo ""
        echo "VAPID_PUBLIC_KEY=$PUBLIC_KEY"
        echo "VAPID_PRIVATE_KEY=$PRIVATE_KEY"
        echo "VAPID_CLAIMS_EMAIL=mailto:tu@email.com"
    fi
    
    echo ""
    echo "📋 Siguientes pasos:"
    echo "   1. Ejecutar migración SQL: sqlite3 backend/app.db < backend/migrations_add_notifications.sql"
    echo "   2. Instalar dependencias: cd backend && uv sync"
    echo "   3. Iniciar backend: cd backend && uv run uvicorn app.main:app --reload"
    echo "   4. Iniciar frontend: cd frontend && npm run dev"
    echo ""
    echo "✅ ¡Listo! Revisa NOTIFICACIONES_SETUP.md para más detalles"
    
else
    echo "❌ Error generando claves VAPID"
    echo "   Intenta manualmente: npx web-push generate-vapid-keys"
    exit 1
fi
