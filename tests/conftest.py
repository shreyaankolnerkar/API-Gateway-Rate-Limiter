import asyncio

import pytest
from httpx import AsyncClient

import app.core.runtime as runtime
from app.main import app


@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test123"}


@pytest.fixture
async def client():

    await app.router.startup()
    async with AsyncClient(app=app, base_url="https://httpbin.org/service") as ac:
        yield ac

    await app.router.shutdown()


@pytest.fixture
def mock_redis(monkeypatch):
    class DummyRedis:
        async def get(self, key):
            return None

        async def set(self, key, value):
            return True

    monkeypatch.setattr("app.core.redis", DummyRedis())


@pytest.fixture(autouse=True)
def reset_log_queue(monkeypatch):
    test_queue = asyncio.Queue()
    monkeypatch.setattr(runtime, "log_queue", test_queue)
    return test_queue
