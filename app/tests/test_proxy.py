import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_proxy(httpx_mock):
    httpx_mock.add_response(url="https://httpbin.org/get", json={"ok": True})
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.get("/proxy/get", headers={"X-Api-Key": "test123"})
    assert res.status_code == 200
