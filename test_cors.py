#!/usr/bin/env python3
"""Script para probar el endpoint y ver el error exacto."""
import requests
import json

# URL de tu API en Cloud Run
BASE_URL = "https://marco-242884135694.southamerica-east1.run.app"

print("🧪 Probando endpoint de login...\n")

# Datos de prueba
data = {
    "identifier": "test@test.com",
    "password": "test123"
}

headers = {
    "Content-Type": "application/json",
    "Origin": "http://localhost:5173"
}

try:
    print(f"📤 Enviando POST a {BASE_URL}/api/auth/login")
    print(f"📦 Data: {json.dumps(data, indent=2)}")
    print(f"📋 Headers: {json.dumps(headers, indent=2)}\n")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=data,
        headers=headers,
        timeout=10
    )
    
    print(f"📥 Status Code: {response.status_code}")
    print(f"📋 Response Headers:")
    for key, value in response.headers.items():
        if 'access-control' in key.lower() or 'cors' in key.lower():
            print(f"  {key}: {value}")
    
    print(f"\n📄 Response Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
        
except requests.exceptions.RequestException as e:
    print(f"❌ Error de conexión: {e}")

print("\n" + "="*60)
print("🧪 Probando endpoint de health...\n")

try:
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"📥 Status Code: {response.status_code}")
    print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")
