#!/bin/bash

# Script para crear 10 hábitos de prueba en el sistema Marco

API_URL="http://127.0.0.1:8000/api"
EMAIL="jorge@jorge.com"
PASSWORD="12345678"

echo "🚀 Iniciando creación de hábitos de prueba..."
echo ""

# Paso 1: Login
echo "🔐 Haciendo login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
USER_NAME=$(echo $LOGIN_RESPONSE | grep -o '"nombre":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Error al hacer login"
    echo $LOGIN_RESPONSE
    exit 1
fi

echo "✅ Login exitoso! Usuario: $USER_NAME"
echo ""

# Paso 2: Obtener categorías
echo "📁 Obteniendo categorías..."
CATEGORIAS_RESPONSE=$(curl -s -X GET "$API_URL/categorias/" \
  -H "Authorization: Bearer $TOKEN")

CATEGORIA_ID=$(echo $CATEGORIAS_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$CATEGORIA_ID" ]; then
    echo "⚠️  No hay categorías. Creando una categoría de prueba..."
    CREATE_CAT_RESPONSE=$(curl -s -X POST "$API_URL/categorias/" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"nombre": "General"}')

    CATEGORIA_ID=$(echo $CREATE_CAT_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
    echo "✅ Categoría 'General' creada con ID: $CATEGORIA_ID"
else
    echo "✅ Usando categoría ID: $CATEGORIA_ID"
fi

echo ""
echo "🎯 Creando 10 hábitos de prueba..."
echo ""

# Colores y hábitos
declare -a HABITOS=(
  '{"nombre":"Ejercicio matutino","descripcion":"Hacer 30 minutos de ejercicio cada mañana","unidad_medida":"minutos","meta_diaria":30,"dias":"[\"L\", \"M\", \"X\", \"J\", \"V\"]","color":"#e94560","activo":1}'
  '{"nombre":"Leer libros","descripcion":"Leer al menos 20 páginas al día","unidad_medida":"páginas","meta_diaria":20,"dias":"[\"L\", \"M\", \"X\", \"J\", \"V\", \"S\", \"D\"]","color":"#00ff88","activo":1}'
  '{"nombre":"Meditar","descripcion":"Práctica de meditación diaria","unidad_medida":"minutos","meta_diaria":15,"dias":"[\"L\", \"M\", \"X\", \"J\", \"V\", \"S\", \"D\"]","color":"#533483","activo":1}'
  '{"nombre":"Tomar agua","descripcion":"Beber suficiente agua durante el día","unidad_medida":"vasos","meta_diaria":8,"dias":"[\"L\", \"M\", \"X\", \"J\", \"V\", \"S\", \"D\"]","color":"#ff6b6b","activo":1}'
  '{"nombre":"Estudiar programación","descripcion":"Practicar código y aprender nuevas tecnologías","unidad_medida":"horas","meta_diaria":2,"dias":"[\"L\", \"M\", \"X\", \"J\", \"V\"]","color":"#4ecdc4","activo":1}'
  '{"nombre":"Cocinar en casa","descripcion":"Preparar comidas saludables","unidad_medida":"comidas","meta_diaria":2,"dias":"[\"L\", \"M\", \"X\", \"J\", \"V\", \"S\", \"D\"]","color":"#ffe66d","activo":1}'
  '{"nombre":"Caminar","descripcion":"Dar un paseo diario","unidad_medida":"pasos","meta_diaria":10000,"dias":"[\"L\", \"M\", \"X\", \"J\", \"V\", \"S\", \"D\"]","color":"#a8dadc","activo":1}'
  '{"nombre":"Escribir diario","descripcion":"Reflexionar por escrito sobre el día","unidad_medida":"entradas","meta_diaria":1,"dias":"[\"L\", \"M\", \"X\", \"J\", \"V\", \"S\", \"D\"]","color":"#f4a261","activo":1}'
  '{"nombre":"Practicar inglés","descripcion":"Estudiar y practicar inglés","unidad_medida":"minutos","meta_diaria":30,"dias":"[\"L\", \"M\", \"X\", \"J\", \"V\"]","color":"#2a9d8f","activo":1}'
  '{"nombre":"Dormir temprano","descripcion":"Acostarse antes de las 11 PM","unidad_medida":"días","meta_diaria":1,"dias":"[\"L\", \"M\", \"X\", \"J\", \"V\", \"S\", \"D\"]","color":"#e76f51","activo":1}'
)

# Crear cada hábito
for i in "${!HABITOS[@]}"; do
  HABITO="${HABITOS[$i]}"
  # Agregar categoria_id al JSON
  HABITO_WITH_CAT=$(echo $HABITO | sed "s/\"activo\":1/\"activo\":1,\"categoria_id\":$CATEGORIA_ID/")

  RESPONSE=$(curl -s -X POST "$API_URL/habitos/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$HABITO_WITH_CAT")

  NOMBRE=$(echo $RESPONSE | grep -o '"nombre":"[^"]*' | cut -d'"' -f4)

  if [ ! -z "$NOMBRE" ]; then
    echo "  $((i+1)). ✅ $NOMBRE"
  else
    echo "  $((i+1)). ❌ Error al crear hábito"
    echo "     $RESPONSE"
  fi
done

echo ""
echo "🎉 ¡Proceso completado! Se crearon hábitos para el usuario $USER_NAME"
echo "🌐 Puedes verlos en: http://localhost:5173/habitos"
