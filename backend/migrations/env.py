"""
Configuración de Alembic para migraciones de base de datos.

Este archivo conecta Alembic con la configuración de la aplicación
y los modelos SQLAlchemy para autogenerar migraciones.
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Importar la configuración y modelos de la aplicación
from app.config import get_settings
from app.database import Base
# Importar todos los modelos para que Alembic los detecte
from app import models  # noqa: F401

# Configuración de Alembic
config = context.config

# Configurar logging desde el archivo .ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Obtener la URL de la base de datos desde la configuración de la app
settings = get_settings()
# Alembic necesita la URL async para las migraciones
config.set_main_option("sqlalchemy.url", settings.database_url)

# Metadata de los modelos para autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Ejecutar migraciones en modo 'offline'.

    Genera scripts SQL sin conectar a la base de datos.
    Útil para revisar los cambios antes de aplicarlos.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Ejecutar las migraciones con una conexión activa."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Ejecutar migraciones en modo 'online' con async engine.

    Crea un engine async y ejecuta las migraciones dentro
    de una conexión.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Punto de entrada para migraciones online."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
