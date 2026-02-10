import time

import httpx
from fastapi import APIRouter, Depends, Request, Response

from app.core.security import get_api_key
from app.gateway.cache import cache_key, get_cache, set_cache
from app.gateway.circuit import check_circuit, record_failure, record_success
from app.gateway.rate_limiter import allow_request_token_bucket
from app.workers.loggers import log_request

router = APIRouter()
UPSTREAM = "https://httpbin.org"


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request, api_key=Depends(get_api_key)):
    allow_request_token_bucket(api_key.key, rate=1, capacity=api_key.tier.rate_limit)

    url = f"{UPSTREAM}/{path}"
    key = cache_key(url, dict(request.query_params))

    if request.method == "GET":
        cached = get_cache(key)
        if cached:
            return Response(content=cached, media_type="application/json")

    check_circuit("httpbin")
    start = time.time()

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                request.method,
                url,
                headers=dict(request.headers),
                content=await request.body(),
                params=dict(request.query_params),
            )
            record_success("httpbin")
        except:
            record_failure("httpbin")
            raise

    latency = int((time.time() - start) * 1000)

    await log_request(
        {
            "api_key": api_key.key,
            "path": path,
            "status_code": resp.status_code,
            "latency_ms": latency,
        }
    )

    if request.method == "GET":
        set_cache(key, resp.content, ttl=30)

    return Response(
        content=resp.content, status_code=resp.status_code, headers=dict(resp.headers)
    )
