"""
Tests para los endpoints de autenticación.

Principios Zen aplicados:
- Tests explícitos y descriptivos
- Un test = una responsabilidad
- Nombres claros que documentan el comportamiento esperado
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import usuario
from app.security import hash_password


class TestRegister:
    """Tests para el endpoint de registro de usuarios."""

    @pytest.mark.asyncio
    async def test_register_new_user_success(self, test_client: AsyncClient):
        """Test: Debe registrar un nuevo usuario exitosamente."""
        response = await test_client.post(
            "/auth/register",
            json={
                "nombre": "nuevo_usuario",
                "email": "nuevo@example.com",
                "password": "Password123",
                "ver_futuro": False
            }
        )

        assert response.status_code == 201
        data = response.json()

        # Verificar estructura de respuesta
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

        # Verificar datos del usuario
        user_data = data["user"]
        assert user_data["nombre"] == "nuevo_usuario"
        assert user_data["email"] == "nuevo@example.com"
        assert user_data["ver_futuro"] is False
        assert "id" in user_data
        assert "created_at" in user_data

        # Verificar que NO se retorna la contraseña
        assert "contrasena" not in user_data
        assert "password" not in user_data

    @pytest.mark.asyncio
    async def test_register_duplicate_email_fails(
        self,
        test_client: AsyncClient,
        test_user: usuario
    ):
        """Test: No debe permitir registrar un email duplicado."""
        response = await test_client.post(
            "/auth/register",
            json={
                "nombre": "otro_usuario",
                "email": "test@example.com",  # Email ya existe
                "password": "Password123",
                "ver_futuro": False
            }
        )

        assert response.status_code == 400
        assert "ya está registrado" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_duplicate_nombre_fails(
        self,
        test_client: AsyncClient,
        test_user: usuario
    ):
        """Test: No debe permitir registrar un nombre duplicado."""
        response = await test_client.post(
            "/auth/register",
            json={
                "nombre": "test_user",  # Nombre ya existe
                "email": "otro@example.com",
                "password": "Password123",
                "ver_futuro": False
            }
        )

        assert response.status_code == 400
        assert "ya está en uso" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_invalid_email_fails(self, test_client: AsyncClient):
        """Test: Debe rechazar emails inválidos."""
        response = await test_client.post(
            "/auth/register",
            json={
                "nombre": "usuario",
                "email": "email_invalido",  # Email sin @
                "password": "Password123",
                "ver_futuro": False
            }
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_short_password_fails(self, test_client: AsyncClient):
        """Test: Debe rechazar contraseñas cortas (< 8 caracteres)."""
        response = await test_client.post(
            "/auth/register",
            json={
                "nombre": "usuario",
                "email": "user@example.com",
                "password": "12345",  # Muy corta
                "ver_futuro": False
            }
        )

        assert response.status_code == 422  # Validation error


class TestLogin:
    """Tests para el endpoint de login."""

    @pytest.mark.asyncio
    async def test_login_success(self, test_client: AsyncClient, test_user: usuario):
        """Test: Debe autenticar un usuario con credenciales correctas."""
        response = await test_client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verificar estructura de respuesta
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

        # Verificar que el token es un string no vacío
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_login_wrong_password_fails(
        self,
        test_client: AsyncClient,
        test_user: usuario
    ):
        """Test: Debe rechazar contraseña incorrecta."""
        response = await test_client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword123"
            }
        )

        assert response.status_code == 401
        assert "incorrectos" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user_fails(self, test_client: AsyncClient):
        """Test: Debe rechazar email no registrado."""
        response = await test_client.post(
            "/auth/login",
            json={
                "email": "noexiste@example.com",
                "password": "SomePassword123"
            }
        )

        assert response.status_code == 401
        assert "incorrectos" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_invalid_email_format_fails(self, test_client: AsyncClient):
        """Test: Debe rechazar formato de email inválido."""
        response = await test_client.post(
            "/auth/login",
            json={
                "email": "email_invalido",
                "password": "SomePassword123"
            }
        )

        assert response.status_code == 422  # Validation error


class TestGetMe:
    """Tests para el endpoint que obtiene el usuario actual."""

    @pytest.mark.asyncio
    async def test_get_me_success(
        self,
        test_client: AsyncClient,
        test_user: usuario,
        auth_headers: dict
    ):
        """Test: Debe retornar datos del usuario autenticado."""
        response = await test_client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verificar datos del usuario
        assert data["nombre"] == "test_user"
        assert data["email"] == "test@example.com"
        assert data["ver_futuro"] is False
        assert "id" in data
        assert "created_at" in data

        # Verificar que NO se retorna la contraseña
        assert "contrasena" not in data
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_get_me_without_auth_fails(self, test_client: AsyncClient):
        """Test: Debe rechazar petición sin autenticación."""
        response = await test_client.get("/auth/me")

        assert response.status_code == 401  # Unauthorized (no hay token)

    @pytest.mark.asyncio
    async def test_get_me_with_invalid_token_fails(self, test_client: AsyncClient):
        """Test: Debe rechazar token inválido."""
        response = await test_client.get(
            "/auth/me",
            headers={"Authorization": "Bearer token_invalido"}
        )

        assert response.status_code == 401  # Unauthorized


class TestUpdateMe:
    """Tests para el endpoint de actualización del usuario actual."""

    @pytest.mark.asyncio
    async def test_update_me_nombre_success(
        self,
        test_client: AsyncClient,
        test_user: usuario,
        auth_headers: dict
    ):
        """Test: Debe actualizar el nombre del usuario."""
        response = await test_client.put(
            "/auth/me",
            headers=auth_headers,
            json={"nombre": "nuevo_nombre"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "nuevo_nombre"
        assert data["email"] == "test@example.com"  # No cambió

    @pytest.mark.asyncio
    async def test_update_me_email_success(
        self,
        test_client: AsyncClient,
        test_user: usuario,
        auth_headers: dict
    ):
        """Test: Debe actualizar el email del usuario."""
        response = await test_client.put(
            "/auth/me",
            headers=auth_headers,
            json={"email": "nuevo@example.com"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "nuevo@example.com"
        assert data["nombre"] == "test_user"  # No cambió

    @pytest.mark.asyncio
    async def test_update_me_ver_futuro_success(
        self,
        test_client: AsyncClient,
        test_user: usuario,
        auth_headers: dict
    ):
        """Test: Debe actualizar la configuración ver_futuro."""
        response = await test_client.put(
            "/auth/me",
            headers=auth_headers,
            json={"ver_futuro": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ver_futuro"] is True

    @pytest.mark.asyncio
    async def test_update_me_duplicate_email_fails(
        self,
        test_client: AsyncClient,
        test_user: usuario,
        test_user_with_future: usuario,
        auth_headers: dict
    ):
        """Test: No debe permitir cambiar a un email ya en uso."""
        response = await test_client.put(
            "/auth/me",
            headers=auth_headers,
            json={"email": "future@example.com"}  # Email del otro usuario
        )

        assert response.status_code == 400
        assert "ya está en uso" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_me_duplicate_nombre_fails(
        self,
        test_client: AsyncClient,
        test_user: usuario,
        test_user_with_future: usuario,
        auth_headers: dict
    ):
        """Test: No debe permitir cambiar a un nombre ya en uso."""
        response = await test_client.put(
            "/auth/me",
            headers=auth_headers,
            json={"nombre": "future_user"}  # Nombre del otro usuario
        )

        assert response.status_code == 400
        assert "ya está en uso" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_me_without_auth_fails(self, test_client: AsyncClient):
        """Test: Debe rechazar actualización sin autenticación."""
        response = await test_client.put(
            "/auth/me",
            json={"nombre": "nuevo_nombre"}
        )

        assert response.status_code == 401  # Unauthorized (no hay token)
