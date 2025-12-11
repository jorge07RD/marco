#!/usr/bin/env python3
"""Script para marcar algunos hábitos como completados para testing."""

import sqlite3
import random

# Conectar a la base de datos
conn = sqlite3.connect('/home/jorge/pp/marco/backend/app.db')
cursor = conn.cursor()

# Obtener todos los progresos
cursor.execute("""
    SELECT id FROM progreso_habitos
    WHERE completado = 0
    ORDER BY RANDOM()
    LIMIT 30
""")

progresos = cursor.fetchall()

print(f"Marcando {len(progresos)} hábitos como completados...")

# Marcar algunos como completados con valores aleatorios
for (progreso_id,) in progresos:
    completado = 1
    valor = random.randint(1, 10)

    cursor.execute("""
        UPDATE progreso_habitos
        SET completado = ?, valor = ?
        WHERE id = ?
    """, (completado, valor, progreso_id))

conn.commit()
conn.close()

print("✅ Hábitos marcados como completados!")
print("Ahora recarga la página de análisis en tu navegador.")
