#!/usr/bin/env python3
"""
Script para crear 10 hábitos de prueba en el sistema Marco.
"""

import requests
import json

# Configuración
API_URL = "http://127.0.0.1:8000/api"
EMAIL = "jorge@jorge.com"
PASSWORD = "12345678"

# Colores para los hábitos
COLORS = [
    "#e94560",  # Rojo
    "#00ff88",  # Verde
    "#533483",  # Púrpura
    "#ff6b6b",  # Rojo claro
    "#4ecdc4",  # Turquesa
    "#ffe66d",  # Amarillo
    "#a8dadc",  # Azul claro
    "#f4a261",  # Naranja
    "#2a9d8f",  # Verde azulado
    "#e76f51",  # Coral
]

# Hábitos de prueba
HABITOS = [
    {
        "nombre": "Ejercicio matutino",
        "descripcion": "Hacer 30 minutos de ejercicio cada mañana",
        "unidad_medida": "minutos",
        "meta_diaria": 30,
        "dias": '["L", "M", "X", "J", "V"]',
        "color": COLORS[0],
    },
    {
        "nombre": "Leer libros",
        "descripcion": "Leer al menos 20 páginas al día",
        "unidad_medida": "páginas",
        "meta_diaria": 20,
        "dias": '["L", "M", "X", "J", "V", "S", "D"]',
        "color": COLORS[1],
    },
    {
        "nombre": "Meditar",
        "descripcion": "Práctica de meditación diaria",
        "unidad_medida": "minutos",
        "meta_diaria": 15,
        "dias": '["L", "M", "X", "J", "V", "S", "D"]',
        "color": COLORS[2],
    },
    {
        "nombre": "Tomar agua",
        "descripcion": "Beber suficiente agua durante el día",
        "unidad_medida": "vasos",
        "meta_diaria": 8,
        "dias": '["L", "M", "X", "J", "V", "S", "D"]',
        "color": COLORS[3],
    },
    {
        "nombre": "Estudiar programación",
        "descripcion": "Practicar código y aprender nuevas tecnologías",
        "unidad_medida": "horas",
        "meta_diaria": 2,
        "dias": '["L", "M", "X", "J", "V"]',
        "color": COLORS[4],
    },
    {
        "nombre": "Cocinar en casa",
        "descripcion": "Preparar comidas saludables",
        "unidad_medida": "comidas",
        "meta_diaria": 2,
        "dias": '["L", "M", "X", "J", "V", "S", "D"]',
        "color": COLORS[5],
    },
    {
        "nombre": "Caminar",
        "descripcion": "Dar un paseo diario",
        "unidad_medida": "pasos",
        "meta_diaria": 10000,
        "dias": '["L", "M", "X", "J", "V", "S", "D"]',
        "color": COLORS[6],
    },
    {
        "nombre": "Escribir diario",
        "descripcion": "Reflexionar por escrito sobre el día",
        "unidad_medida": "entradas",
        "meta_diaria": 1,
        "dias": '["L", "M", "X", "J", "V", "S", "D"]',
        "color": COLORS[7],
    },
    {
        "nombre": "Practicar inglés",
        "descripcion": "Estudiar y practicar inglés",
        "unidad_medida": "minutos",
        "meta_diaria": 30,
        "dias": '["L", "M", "X", "J", "V"]',
        "color": COLORS[8],
    },
    {
        "nombre": "Dormir temprano",
        "descripcion": "Acostarse antes de las 11 PM",
        "unidad_medida": "días",
        "meta_diaria": 1,
        "dias": '["L", "M", "X", "J", "V", "S", "D"]',
        "color": COLORS[9],
    },
]


def main():
    print("🚀 Iniciando creación de hábitos de prueba...\n")

    # Paso 1: Login
    print("🔐 Haciendo login...")
    login_response = requests.post(
        f"{API_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )

    if login_response.status_code != 200:
        print(f"❌ Error al hacer login: {login_response.status_code}")
        print(login_response.json())
        return

    token_data = login_response.json()
    token = token_data["access_token"]
    print(f"✅ Login exitoso! Usuario: {token_data['user']['nombre']}\n")

    # Headers con autenticación
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Paso 2: Obtener categorías
    print("📁 Obteniendo categorías...")
    categorias_response = requests.get(f"{API_URL}/categorias/", headers=headers)

    if categorias_response.status_code != 200:
        print(f"❌ Error al obtener categorías: {categorias_response.status_code}")
        return

    categorias = categorias_response.json()

    if not categorias:
        print("⚠️  No hay categorías. Creando una categoría de prueba...")
        create_cat_response = requests.post(
            f"{API_URL}/categorias/",
            headers=headers,
            json={"nombre": "General"}
        )
        if create_cat_response.status_code == 200:
            categoria_id = create_cat_response.json()["id"]
            print(f"✅ Categoría 'General' creada con ID: {categoria_id}")
        else:
            print(f"❌ Error al crear categoría: {create_cat_response.status_code}")
            return
    else:
        categoria_id = categorias[0]["id"]
        print(f"✅ Usando categoría: {categorias[0]['nombre']} (ID: {categoria_id})\n")

    # Paso 3: Crear hábitos
    print("🎯 Creando 10 hábitos de prueba...\n")

    for i, habito_data in enumerate(HABITOS, 1):
        habito_data["categoria_id"] = categoria_id

        response = requests.post(
            f"{API_URL}/habitos/",
            headers=headers,
            json=habito_data
        )

        if response.status_code == 200:
            habito = response.json()
            print(f"  {i}. ✅ {habito['nombre']} - {habito['descripcion']}")
        else:
            print(f"  {i}. ❌ Error al crear '{habito_data['nombre']}': {response.status_code}")
            print(f"      {response.json()}")

    print(f"\n🎉 ¡Proceso completado! Se crearon hábitos para el usuario {token_data['user']['nombre']}")
    print(f"🌐 Puedes verlos en: http://localhost:5173/habitos")


if __name__ == "__main__":
    main()
