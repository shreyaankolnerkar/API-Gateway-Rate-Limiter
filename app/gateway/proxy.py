import time

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.core.redis import redis_client
from app.core.runtime import log_queue
from app.core.security import get_api_key
from app.gateway.cache import cache_key as make_cache_key
from app.gateway.cache import get_cache, set_cache
from app.gateway.circuit import check_circuit, record_failure, record_success
from app.gateway.rate_limiter import allow_request_token_bucket

router = APIRouter()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(path: str, request: Request, api_key=Depends(get_api_key)):
    service = "httpbin"

    await allow_request_token_bucket(api_key.key, rate=10, capacity=10)
    await check_circuit(service)

    url = f"https://httpbin.org/{path}"

    start = time.time()
    cache_status = None
    cache_k = None
    cache_ttl = None
    circuit_state = "CLOSED"
    upstream_error_type = "None"

    # -------- CACHE CHECK --------
    if request.method == "GET":
        cache_k = make_cache_key(url, dict(request.query_params))
        cached = await get_cache(cache_k)

        if cached:
            cache_status = "HIT"
            try:
                cache_ttl = await redis_client.ttl(cache_k)
            except Exception:
                cache_ttl = None

            latency_ms = int((time.time() - start) * 1000)

            await log_queue.put(
                {
                    "api_key": api_key.key,
                    "path": path,
                    "status_code": 200,
                    "cache_status": cache_status,
                    "cache_key": cache_k,
                    "cache_ttl": cache_ttl,
                    "circuit_state": circuit_state,
                    "upstream_latency_ms": latency_ms,
                    "upstream_error_type": upstream_error_type,
                }
            )

            return Response(content=cached, media_type="application/json")

        cache_status = "MISS"

    # -------- UPSTREAM CALL --------
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
        circuit_state = "CLOSED"

    except httpx.ReadTimeout:
        upstream_error_type = "timeout"
        await record_failure(service)

        latency_ms = int((time.time() - start) * 1000)

        await log_queue.put(
            {
                "api_key": api_key.key,
                "path": path,
                "status_code": 504,
                "cache_status": cache_status,
                "cache_key": cache_k,
                "cache_ttl": cache_ttl,
                "circuit_state": "OPEN",
                "upstream_latency_ms": latency_ms,
                "upstream_error_type": upstream_error_type,
            }
        )

        raise HTTPException(504, "Upstream timeout")

    except httpx.ConnectError:
        upstream_error_type = "connection_error"
        await record_failure(service)

        latency_ms = int((time.time() - start) * 1000)

        await log_queue.put(
            {
                "api_key": api_key.key,
                "path": path,
                "status_code": 502,
                "cache_status": cache_status,
                "cache_key": cache_k,
                "cache_ttl": cache_ttl,
                "circuit_state": "OPEN",
                "upstream_latency_ms": latency_ms,
                "upstream_error_type": upstream_error_type,
            }
        )

        raise HTTPException(502, "Upstream connection error")

    except Exception:
        upstream_error_type = "unknown_error"
        await record_failure(service)

        latency_ms = int((time.time() - start) * 1000)

        await log_queue.put(
            {
                "api_key": api_key.key,
                "path": path,
                "status_code": 500,
                "cache_status": cache_status,
                "cache_key": cache_k,
                "cache_ttl": cache_ttl,
                "circuit_state": "OPEN",
                "upstream_latency_ms": latency_ms,
                "upstream_error_type": upstream_error_type,
            }
        )

        raise HTTPException(500, "Unknown upstream error")

    # -------- SUCCESS PATH --------
    latency_ms = int((time.time() - start) * 1000)

    if cache_k and resp.status_code == 200:
        await set_cache(cache_k, resp.content, ttl=30)
        cache_ttl = 30

    await log_queue.put(
        {
            "api_key": api_key.key,
            "path": path,
            "status_code": resp.status_code,
            "cache_status": cache_status,
            "cache_key": cache_k,
            "cache_ttl": cache_ttl,
            "circuit_state": circuit_state,
            "upstream_latency_ms": latency_ms,
            "upstream_error_type": None,
        }
    )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type="application/json",
    )
