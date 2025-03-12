# Testes de integração para a aplicação principal com inversão de dependência
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.clima import verificar_chuva
from unittest.mock import AsyncMock, patch
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


client = TestClient(app)

def test_version_header():
    response = client.post("/pedido", json={"id": 1, "itens": ["pizza"], "total": 50.0})
    assert response.headers["X-API-Version"] == "2.1.0"
    assert response.json()["version"] == "2.1.0"

@pytest.mark.asyncio
async def test_fazer_pedido_sem_chuva():
    async def override_verificar_chuva():
        return False
    app.dependency_overrides[verificar_chuva] = override_verificar_chuva
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        response = await ac.post("/pedido", json={"id": 1, "itens": ["pizza"], "total": 50.0})
    del app.dependency_overrides[verificar_chuva]
    assert response.status_code == 200
    assert response.json()["total"] == 50.0
    assert response.json()["taxa_entrega"] == 0.0

@pytest.mark.asyncio
async def test_fazer_pedido_com_chuva():
    async def override_verificar_chuva():
        return True
    app.dependency_overrides[verificar_chuva] = override_verificar_chuva
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        response = await ac.post("/pedido", json={"id": 2, "itens": ["hamburguer"], "total": 30.0})
    del app.dependency_overrides[verificar_chuva]
    assert response.status_code == 200
    assert response.json()["total"] == 35.0
    assert response.json()["taxa_entrega"] == 5.0