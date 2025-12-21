"""
Tests para los endpoints de categorías.

Principios Zen aplicados:
- Tests explícitos que documentan el comportamiento
- Early returns en validaciones
- Nombres descriptivos
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import categorias


class TestGetCategorias:
    """Tests para el endpoint de listado de categorías."""

    @pytest.mark.asyncio
    async def test_get_categorias_empty_list(self, test_client: AsyncClient):
        """Test: Debe retornar lista vacía si no hay categorías."""
        response = await test_client.get("/categorias/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_get_categorias_with_data(
        self,
        test_client: AsyncClient,
        test_categoria: categorias
    ):
        """Test: Debe retornar lista de categorías."""
        response = await test_client.get("/categorias/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["nombre"] == "Salud"
        assert "id" in data[0]
        assert "created_at" in data[0]

    @pytest.mark.asyncio
    async def test_get_categorias_pagination(
        self,
        test_client: AsyncClient,
        test_db_session: AsyncSession
    ):
        """Test: Debe respetar parámetros de paginación."""
        # Crear múltiples categorías
        categorias_list = [
            categorias(nombre=f"Categoria {i}")
            for i in range(15)
        ]
        test_db_session.add_all(categorias_list)
        await test_db_session.commit()

        # Test con limit
        response = await test_client.get("/categorias/?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        # Test con skip y limit
        response = await test_client.get("/categorias/?skip=5&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5


class TestGetCategoria:
    """Tests para el endpoint de obtención de categoría por ID."""

    @pytest.mark.asyncio
    async def test_get_categoria_success(
        self,
        test_client: AsyncClient,
        test_categoria: categorias
    ):
        """Test: Debe retornar categoría existente."""
        response = await test_client.get(f"/categorias/{test_categoria.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_categoria.id
        assert data["nombre"] == "Salud"
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_get_categoria_not_found(self, test_client: AsyncClient):
        """Test: Debe retornar 404 si la categoría no existe."""
        response = await test_client.get("/categorias/999")

        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"]


class TestCreateCategoria:
    """Tests para el endpoint de creación de categorías."""

    @pytest.mark.asyncio
    async def test_create_categoria_success(self, test_client: AsyncClient):
        """Test: Debe crear una nueva categoría."""
        response = await test_client.post(
            "/categorias/",
            json={"nombre": "Ejercicio"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Ejercicio"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_categoria_invalid_name_empty(
        self,
        test_client: AsyncClient
    ):
        """Test: Debe rechazar nombre vacío."""
        response = await test_client.post(
            "/categorias/",
            json={"nombre": ""}
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_categoria_invalid_name_too_long(
        self,
        test_client: AsyncClient
    ):
        """Test: Debe rechazar nombre demasiado largo."""
        nombre_largo = "x" * 150  # Más de 100 caracteres

        response = await test_client.post(
            "/categorias/",
            json={"nombre": nombre_largo}
        )

        assert response.status_code == 422  # Validation error


class TestUpdateCategoria:
    """Tests para el endpoint de actualización de categorías."""

    @pytest.mark.asyncio
    async def test_update_categoria_success(
        self,
        test_client: AsyncClient,
        test_categoria: categorias
    ):
        """Test: Debe actualizar una categoría existente."""
        response = await test_client.put(
            f"/categorias/{test_categoria.id}",
            json={"nombre": "Salud Mental"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_categoria.id
        assert data["nombre"] == "Salud Mental"

    @pytest.mark.asyncio
    async def test_update_categoria_not_found(self, test_client: AsyncClient):
        """Test: Debe retornar 404 al actualizar categoría inexistente."""
        response = await test_client.put(
            "/categorias/999",
            json={"nombre": "Nueva"}
        )

        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_categoria_partial_update(
        self,
        test_client: AsyncClient,
        test_categoria: categorias
    ):
        """Test: Debe permitir actualización parcial (solo campos enviados)."""
        # No enviar nada (actualización vacía debería funcionar)
        response = await test_client.put(
            f"/categorias/{test_categoria.id}",
            json={}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Salud"  # No cambió


class TestDeleteCategoria:
    """Tests para el endpoint de eliminación de categorías."""

    @pytest.mark.asyncio
    async def test_delete_categoria_success(
        self,
        test_client: AsyncClient,
        test_categoria: categorias
    ):
        """Test: Debe eliminar una categoría existente."""
        response = await test_client.delete(f"/categorias/{test_categoria.id}")

        assert response.status_code == 204

        # Verificar que ya no existe
        get_response = await test_client.get(f"/categorias/{test_categoria.id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_categoria_not_found(self, test_client: AsyncClient):
        """Test: Debe retornar 404 al eliminar categoría inexistente."""
        response = await test_client.delete("/categorias/999")

        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_categoria_idempotent(
        self,
        test_client: AsyncClient,
        test_categoria: categorias
    ):
        """Test: Eliminar dos veces la misma categoría debe fallar la segunda vez."""
        # Primera eliminación
        response = await test_client.delete(f"/categorias/{test_categoria.id}")
        assert response.status_code == 204

        # Segunda eliminación
        response = await test_client.delete(f"/categorias/{test_categoria.id}")
        assert response.status_code == 404
