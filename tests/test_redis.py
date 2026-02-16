import pytest

from app.core.redis import redis_client


@pytest.mark.asyncio
async def test_redis_set_get():
    await redis_client.set("test_key", "hello")
    value = await redis_client.get("test_key")

    assert value == "hello"
