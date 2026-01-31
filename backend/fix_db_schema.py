"""
Script para verificar y agregar columnas faltantes de notificaciones.

Este script verifica si las columnas de notificaciones existen en la tabla usuarios
y las agrega si faltan, para solucionar problemas de migraciones no aplicadas.
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import get_settings

async def fix_missing_columns():
    """Verifica y agrega columnas faltantes."""
    settings = get_settings()
    
    print("🔧 Verificando columnas de notificaciones...")
    print(f"📍 DATABASE_URL: {settings.database_url[:50]}...")
    
    engine = create_async_engine(settings.database_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Verificar si existen las columnas
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='usuarios' 
                AND column_name IN (
                    'notificaciones_activas', 
                    'recordatorios_activos', 
                    'hora_recordatorio', 
                    'timezone'
                )
            """))
            existing_columns = {row[0] for row in result.fetchall()}
            
            required_columns = {
                'notificaciones_activas': 'BOOLEAN DEFAULT FALSE',
                'recordatorios_activos': 'BOOLEAN DEFAULT FALSE',
                'hora_recordatorio': "VARCHAR DEFAULT '08:00'",
                'timezone': "VARCHAR DEFAULT 'America/Santo_Domingo'"
            }
            
            for col_name, col_def in required_columns.items():
                if col_name not in existing_columns:
                    print(f"➕ Agregando columna: {col_name}")
                    await conn.execute(text(f"ALTER TABLE usuarios ADD COLUMN {col_name} {col_def}"))
                else:
                    print(f"✅ Columna {col_name} ya existe")
            
            # Verificar tabla push_subscriptions
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_name='push_subscriptions'
                )
            """))
            has_push_table = result.scalar()
            
            if not has_push_table:
                print("📋 Creando tabla push_subscriptions...")
                await conn.execute(text("""
                    CREATE TABLE push_subscriptions (
                        id SERIAL PRIMARY KEY,
                        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                        endpoint VARCHAR NOT NULL,
                        p256dh_key VARCHAR NOT NULL,
                        auth_key VARCHAR NOT NULL,
                        user_agent VARCHAR,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE,
                        UNIQUE(usuario_id, endpoint)
                    )
                """))
                print("✅ Tabla push_subscriptions creada")
            else:
                print("✅ Tabla push_subscriptions ya existe")
            
            print("\n🎉 Todas las columnas y tablas verificadas/creadas correctamente")
            return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    import sys
    success = asyncio.run(fix_missing_columns())
    sys.exit(0 if success else 1)
