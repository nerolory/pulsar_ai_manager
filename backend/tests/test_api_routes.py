"""Smoke tests for HTTP API routes with MockProvider."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client(patch_db_path):
    from app.configs import settings

    settings.mock_mode = True

    from app.database import init_db

    await init_db()

    import app.providers
    from app.providers.factory import ProviderConfig, ProviderFactory
    from app.state import set_provider

    app.providers.register_all()
    set_provider(ProviderFactory.create(ProviderConfig(provider="mock")))

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_ok(client):
    response = await client.get("/api/v1/settings/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["mock_mode"] is True


@pytest.mark.asyncio
async def test_providers_list(client):
    response = await client.get("/api/v1/settings/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "mock" in data["providers"]


@pytest.mark.asyncio
async def test_capabilities(client):
    response = await client.get("/api/v1/settings/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["streaming"] is True


@pytest.mark.asyncio
async def test_local_llm_models_list(client):
    response = await client.get("/api/v1/settings/models?provider=local_llm")
    assert response.status_code == 200
    assert "models" in response.json()


@pytest.mark.asyncio
async def test_admin_system_check(client):
    response = await client.get("/api/v1/admin/system-check")
    assert response.status_code == 200
    data = response.json()
    assert "specs" in data
    assert "tier" in data


@pytest.mark.asyncio
async def test_chat_stream_mock(client):
    payload = {
        "messages": [{"role": "user", "content": "ping"}],
        "temperature": 0.7,
        "max_tokens": 64,
        "top_p": 1.0,
        "use_context": False,
    }
    response = await client.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 200
    assert len(response.text) > 0
