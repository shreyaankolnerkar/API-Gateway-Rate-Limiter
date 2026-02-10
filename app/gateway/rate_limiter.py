import time

from fastapi import HTTPException, status

from app.core.redis import redis_client


async def allow_request_token_bucket(api_key: str, rate: int, capacity: int):
    key = f"bucket:{api_key}"
    now = time.time()

    data = await redis_client.hgetall(key)

    if data:
        tokens = float(data.get(b"tokens", capacity))
        last = float(data.get(b"last", now))
    else:
        tokens = capacity
        last = now

    # refill tokens based on time passed
    refill = (now - last) * rate
    tokens = min(capacity, tokens + refill)

    if tokens < 1:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
        )

    tokens -= 1

    await redis_client.hset(key, mapping={"tokens": tokens, "last": now})
    await redis_client.expire(key, 3600)

    return True
