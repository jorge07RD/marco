"""
Tests para los endpoints de hábitos.

Principios Zen aplicados:
- Tests explícitos y descriptivos
- Verificación de autenticación y autorización
- Tests de casos edge
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import usuario, categorias, habitos


@pytest_asyncio.fixture
async def test_habito(
    test_db_session: AsyncSession,
    test_user: usuario,
    test_categoria: categorias
) -> habitos:
    """Crea un hábito de prueba."""
    habito = habitos(
        nombre="Correr",
        descripcion="Correr 30 minutos",
        categoria_id=test_categoria.id,
        usuario_id=test_user.id,
        unidad_medida="minutos",
        meta_diaria=30.0,
        dias='["L", "M", "X", "J", "V"]',  # Lunes a Viernes
        color="#FF5733",
        activo=1
    )
    test_db_session.add(habito)
    await test_db_session.commit()
    await test_db_session.refresh(habito)
    return habito


class TestGetHabitos:
    """Tests para el endpoint de listado de hábitos."""

    @pytest.mark.asyncio
    async def test_get_habitos_requires_auth(self, test_client: AsyncClient):
        """Test: Debe requerir autenticación."""
        response = await test_client.get("/habitos/")

        assert response.status_code == 403  # Forbidden

    @pytest.mark.asyncio
    async def test_get_habitos_empty_list(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test: Debe retornar lista vacía si el usuario no tiene hábitos."""
        response = await test_client.get("/habitos/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_get_habitos_only_own_habits(
        self,
        test_client: AsyncClient,
        test_db_session: AsyncSession,
        test_user: usuario,
        test_user_with_future: usuario,
        test_categoria: categorias,
        auth_headers: dict
    ):
        """Test: Debe retornar solo los hábitos del usuario autenticado."""
        # Crear hábito para test_user
        habito_own = habitos(
            nombre="Mi Hábito",
            categoria_id=test_categoria.id,
            usuario_id=test_user.id,
            unidad_medida="veces",
            meta_diaria=1.0,
            dias='["L"]',
            color="#000000",
            activo=1
        )
        test_db_session.add(habito_own)

        # Crear hábito para otro usuario
        habito_other = habitos(
            nombre="Hábito de Otro",
            categoria_id=test_categoria.id,
            usuario_id=test_user_with_future.id,
            unidad_medida="veces",
            meta_diaria=1.0,
            dias='["L"]',
            color="#FFFFFF",
            activo=1
        )
        test_db_session.add(habito_other)
        await test_db_session.commit()

        # Verificar que solo retorna los propios
        response = await test_client.get("/habitos/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["nombre"] == "Mi Hábito"


class TestGetHabito:
    """Tests para el endpoint de obtención de hábito por ID."""

    @pytest.mark.asyncio
    async def test_get_habito_success(
        self,
        test_client: AsyncClient,
        test_habito: habitos,
        auth_headers: dict
    ):
        """Test: Debe retornar el hábito solicitado."""
        response = await test_client.get(
            f"/habitos/{test_habito.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_habito.id
        assert data["nombre"] == "Correr"
        assert data["meta_diaria"] == 30.0

    @pytest.mark.asyncio
    async def test_get_habito_not_found(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test: Debe retornar 404 si el hábito no existe."""
        response = await test_client.get("/habitos/999", headers=auth_headers)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_habito_other_user_not_found(
        self,
        test_client: AsyncClient,
        test_db_session: AsyncSession,
        test_user_with_future: usuario,
        test_categoria: categorias,
        auth_headers: dict
    ):
        """Test: No debe permitir ver hábitos de otros usuarios."""
        # Crear hábito de otro usuario
        other_habito = habitos(
            nombre="Hábito de Otro",
            categoria_id=test_categoria.id,
            usuario_id=test_user_with_future.id,
            unidad_medida="veces",
            meta_diaria=1.0,
            dias='["L"]',
            color="#FFFFFF",
            activo=1
        )
        test_db_session.add(other_habito)
        await test_db_session.commit()
        await test_db_session.refresh(other_habito)

        # Intentar obtener hábito de otro usuario
        response = await test_client.get(
            f"/habitos/{other_habito.id}",
            headers=auth_headers
        )

        assert response.status_code == 404  # No encontrado


class TestCreateHabito:
    """Tests para el endpoint de creación de hábitos."""

    @pytest.mark.asyncio
    async def test_create_habito_success(
        self,
        test_client: AsyncClient,
        test_categoria: categorias,
        auth_headers: dict
    ):
        """Test: Debe crear un nuevo hábito."""
        response = await test_client.post(
            "/habitos/",
            headers=auth_headers,
            json={
                "nombre": "Meditar",
                "descripcion": "Meditación diaria",
                "categoria_id": test_categoria.id,
                "unidad_medida": "minutos",
                "meta_diaria": 20.0,
                "dias": '["L", "M", "X", "J", "V", "S", "D"]',
                "color": "#00FF00",
                "activo": 1
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Meditar"
        assert data["meta_diaria"] == 20.0
        assert "id" in data
        assert "usuario_id" in data

    @pytest.mark.asyncio
    async def test_create_habito_requires_auth(
        self,
        test_client: AsyncClient,
        test_categoria: categorias
    ):
        """Test: Debe requerir autenticación."""
        response = await test_client.post(
            "/habitos/",
            json={
                "nombre": "Meditar",
                "categoria_id": test_categoria.id,
                "unidad_medida": "minutos",
                "meta_diaria": 20.0,
                "dias": '["L"]',
                "color": "#00FF00",
                "activo": 1
            }
        )

        assert response.status_code == 403  # Forbidden

    @pytest.mark.asyncio
    async def test_create_habito_invalid_categoria(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test: Debe fallar con categoría inexistente."""
        response = await test_client.post(
            "/habitos/",
            headers=auth_headers,
            json={
                "nombre": "Meditar",
                "categoria_id": 999,  # No existe
                "unidad_medida": "minutos",
                "meta_diaria": 20.0,
                "dias": '["L"]',
                "color": "#00FF00",
                "activo": 1
            }
        )

        # Puede fallar con 422 (validación) o error de integridad
        assert response.status_code in [422, 500]


class TestUpdateHabito:
    """Tests para el endpoint de actualización de hábitos."""

    @pytest.mark.asyncio
    async def test_update_habito_success(
        self,
        test_client: AsyncClient,
        test_habito: habitos,
        auth_headers: dict
    ):
        """Test: Debe actualizar un hábito existente."""
        response = await test_client.put(
            f"/habitos/{test_habito.id}",
            headers=auth_headers,
            json={
                "nombre": "Correr (Actualizado)",
                "meta_diaria": 45.0
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Correr (Actualizado)"
        assert data["meta_diaria"] == 45.0

    @pytest.mark.asyncio
    async def test_update_habito_not_found(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test: Debe retornar 404 al actualizar hábito inexistente."""
        response = await test_client.put(
            "/habitos/999",
            headers=auth_headers,
            json={"nombre": "Nuevo"}
        )

        assert response.status_code == 404


class TestDeleteHabito:
    """Tests para el endpoint de eliminación de hábitos."""

    @pytest.mark.asyncio
    async def test_delete_habito_success(
        self,
        test_client: AsyncClient,
        test_habito: habitos,
        auth_headers: dict
    ):
        """Test: Debe eliminar un hábito existente."""
        response = await test_client.delete(
            f"/habitos/{test_habito.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verificar que ya no existe
        get_response = await test_client.get(
            f"/habitos/{test_habito.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_habito_not_found(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test: Debe retornar 404 al eliminar hábito inexistente."""
        response = await test_client.delete(
            "/habitos/999",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_habito_requires_auth(
        self,
        test_client: AsyncClient,
        test_habito: habitos
    ):
        """Test: Debe requerir autenticación."""
        response = await test_client.delete(f"/habitos/{test_habito.id}")

        assert response.status_code == 403  # Forbidden
