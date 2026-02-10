import httpx
from fastapi import APIRouter, Depends, Request, Response

from app.core.runtime import log_queue
from app.core.security import get_api_key
from app.gateway.cache import cache_key, get_cache, set_cache
from app.gateway.circuit import check_circuit, record_failure, record_success
from app.gateway.rate_limiter import allow_request_token_bucket

router = APIRouter()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(path: str, request: Request, api_key=Depends(get_api_key)):
    service = "httpbin"

    await allow_request_token_bucket(api_key.key, rate=10, capacity=10)
    await check_circuit(service)

    url = f"https://httpbin.org/{path}"
    cache_k = None

    if request.method == "GET":
        cache_k = cache_key(url, dict(request.query_params))
        cached = await get_cache(cache_k)
        if cached:
            return Response(content=cached, media_type="application/json")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                request.method,
                url,
                headers=dict(request.headers),
                content=await request.body(),
                timeout=10.0,
            )
        await record_success(service)
    except Exception:
        await record_failure(service)
        raise

    log = {
        "api_key": api_key.key,
        "path": path,
        "status_code": resp.status_code,
    }

    await log_queue.put(log)

    if cache_k and resp.status_code == 200:
        await set_cache(cache_k, resp.content, ttl=30)

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type="application/json",
    )
