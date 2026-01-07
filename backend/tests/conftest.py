"""
Configuración global de pytest y fixtures compartidas.

Este archivo contiene fixtures que se pueden usar en todos los tests.
"""

import asyncio
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import usuario, categorias
from app.security import hash_password


# URL de base de datos en memoria para tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Crea un event loop para toda la sesión de tests.

    Necesario para tests asíncronos con pytest-asyncio.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_engine():
    """
    Crea un engine de SQLAlchemy para tests con base de datos en memoria.

    Yields:
        AsyncEngine: Engine configurado para tests
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Necesario para SQLite en memoria
        echo=False  # Cambiar a True para debug de SQL
    )

    # Crear todas las tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Limpiar
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Crea una sesión de base de datos para cada test.

    Args:
        test_engine: Engine de base de datos de test

    Yields:
        AsyncSession: Sesión de base de datos aislada para el test
    """
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()  # Rollback para limpiar después del test


@pytest_asyncio.fixture
async def test_client(test_db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Crea un cliente HTTP async para tests de endpoints.

    Args:
        test_db_session: Sesión de base de datos de test

    Yields:
        AsyncClient: Cliente HTTP configurado para tests
    """
    # Override de la dependencia get_db para usar la sesión de test
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Limpiar override
    app.dependency_overrides.clear()


@pytest.fixture
def sync_test_client(test_db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """
    Crea un cliente HTTP síncrono para tests simples.

    Args:
        test_db_session: Sesión de base de datos de test

    Yields:
        TestClient: Cliente HTTP síncrono
    """
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_db_session: AsyncSession) -> usuario:
    """
    Crea un usuario de prueba en la base de datos.

    Args:
        test_db_session: Sesión de base de datos de test

    Returns:
        usuario: Usuario de prueba creado
    """
    user = usuario(
        nombre="test_user",
        email="test@example.com",
        contrasena=hash_password("TestPassword123"),
        ver_futuro=False
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_with_future(test_db_session: AsyncSession) -> usuario:
    """
    Crea un usuario de prueba con permiso para ver fechas futuras.

    Args:
        test_db_session: Sesión de base de datos de test

    Returns:
        usuario: Usuario con ver_futuro=True
    """
    user = usuario(
        nombre="future_user",
        email="future@example.com",
        contrasena=hash_password("FuturePassword123"),
        ver_futuro=True
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_token(test_client: AsyncClient, test_user: usuario) -> str:
    """
    Obtiene un token de autenticación para el usuario de prueba.

    Args:
        test_client: Cliente HTTP de test
        test_user: Usuario de prueba

    Returns:
        str: Token JWT de autenticación
    """
    response = await test_client.post(
        "/auth/login",
        json={
            "identifier": "test@example.com",
            "password": "TestPassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]


@pytest_asyncio.fixture
async def auth_headers(auth_token: str) -> dict:
    """
    Crea headers de autenticación con el token.

    Args:
        auth_token: Token JWT de autenticación

    Returns:
        dict: Headers con Authorization Bearer
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture
async def test_categoria(test_db_session: AsyncSession) -> categorias:
    """
    Crea una categoría de prueba en la base de datos.

    Args:
        test_db_session: Sesión de base de datos de test

    Returns:
        categorias: Categoría de prueba creada
    """
    categoria = categorias(nombre="Salud")
    test_db_session.add(categoria)
    await test_db_session.commit()
    await test_db_session.refresh(categoria)
    return categoria
