from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

# Obtener la configuración de la aplicación
settings = get_settings()

logger.info(f"🔌 Configurando motor de base de datos...")
logger.info(f"🗄️  Database URL (primeros 60 chars): {settings.database_url[:60]}...")

# Crear el motor de base de datos asíncrono
try:
    engine = create_async_engine(
        settings.database_url,  # URL de conexión a la base de datos
        echo=settings.debug,    # Mostrar queries SQL si debug está activo
        pool_pre_ping=True,     # Verificar conexiones antes de usarlas
        pool_recycle=3600,      # Reciclar conexiones cada hora
    )
    logger.info("✅ Motor de base de datos creado exitosamente")
except Exception as e:
    logger.error(f"❌ Error al crear motor de base de datos: {str(e)}")
    raise

# Crear la fábrica de sesiones asíncronas
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Los objetos no expiran después de commit
)


# Clase base para todos los modelos ORM
class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """
    Generador de dependencia para obtener una sesión de base de datos.
    Maneja automáticamente commit, rollback y cierre de la sesión.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()  # Confirmar cambios si no hay errores
        except Exception:
            await session.rollback()  # Revertir cambios si hay error
            raise
        finally:
            await session.close()  # Cerrar la sesión siempre


async def init_db():
    """
    Inicializar la base de datos creando todas las tablas definidas en los modelos.
    """
    try:
        logger.info("🔧 Iniciando creación de tablas...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tablas de base de datos creadas/verificadas exitosamente")
    except Exception as e:
        logger.error(f"❌ Error al inicializar base de datos: {str(e)}")
        logger.error(f"💡 Verifica que la base de datos sea accesible desde Cloud Run")
        raise
