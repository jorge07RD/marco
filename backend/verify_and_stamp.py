"""
Script para verificar y marcar la base de datos con la migración baseline.

Este script verifica si la base de datos ya tiene las tablas existentes
y si es así, la marca con la revisión baseline para que Alembic pueda
continuar con las migraciones futuras.
"""
import asyncio
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import get_settings
import sys

async def verify_and_stamp():
    """Verifica si la DB tiene tablas y la marca con baseline si es necesario."""
    settings = get_settings()
    
    print("🔍 Verificando estado de la base de datos...")
    print(f"📍 DATABASE_URL: {settings.database_url[:50]}...")
    
    # Crear engine para verificar
    engine = create_async_engine(settings.database_url, echo=False)
    
    try:
        async with engine.connect() as conn:
            # Verificar si existe la tabla alembic_version
            result = await conn.execute(
                text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version')")
            )
            has_alembic = result.scalar()
            
            if not has_alembic:
                print("⚠️  Tabla alembic_version no existe")
                
                # Verificar si existen las tablas de la aplicación
                result = await conn.execute(
                    text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='usuarios')")
                )
                has_usuarios = result.scalar()
                
                if has_usuarios:
                    print("✅ La base de datos tiene tablas existentes")
                    print("🏷️  Marcando base de datos con revisión baseline: 0a5df8ebbac4")
                    
                    # Crear tabla alembic_version y marcar con baseline
                    await conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"))
                    await conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('0a5df8ebbac4')"))
                    await conn.commit()
                    
                    print("✅ Base de datos marcada correctamente")
                    return True
                else:
                    print("ℹ️  Base de datos vacía - se ejecutarán todas las migraciones")
                    return True
            else:
                # Verificar qué revisión tiene
                result = await conn.execute(text("SELECT version_num FROM alembic_version"))
                version = result.scalar()
                print(f"✅ Base de datos ya tiene revisión: {version}")
                return True
                
    except Exception as e:
        print(f"❌ Error al verificar base de datos: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(verify_and_stamp())
    sys.exit(0 if success else 1)
