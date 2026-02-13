from fastapi import HTTPException

from app.core.redis import redis_client

FAIL_LIMIT = 5
TIMEOUT = 30


async def check_circuit(service: str):
    fails_raw = await redis_client.get(f"cb:{service}:fails")
    fails = int(fails_raw or 0)

    opened = await redis_client.get(f"cb:{service}:open")
    if opened and fails >= FAIL_LIMIT:
        raise HTTPException(503, "Circuit open")


async def record_success(service: str):
    await redis_client.delete(f"cb:{service}:fails")


async def record_failure(service: str):
    key = f"cb:{service}:fails"
    fails = await redis_client.incr(key)
    if fails >= FAIL_LIMIT:
        await redis_client.setex(f"cb:{service}:open", TIMEOUT, 1)


async def is_circuit_open(service: str) -> bool:
    state = await redis_client.get(f"circuit:{service}:state")
    return state == "OPEN"
