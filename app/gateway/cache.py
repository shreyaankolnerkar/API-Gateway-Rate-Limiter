import hashlib

from app.core.redis import redis_client


def cache_key(url: str, params: dict):
    raw = f"{url}?{params}"
    return "cache:" + hashlib.md5(raw.encode()).hexdigest()


async def get_cache(key: str):
    return await redis_client.get(key)


async def set_cache(key: str, value: bytes, ttl: int):
    await redis_client.setex(key, ttl, value)
