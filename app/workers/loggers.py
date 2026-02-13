import json

from app.core.redis import redis_client
from app.core.runtime import log_queue
from app.db.models import RequestLog
from app.db.session import SessionLocal


async def logger_worker():
    while True:
        log_item = await log_queue.get()
        print("LOG ITEM RECEIVED:", log_item)
        db = SessionLocal()
        try:

            await redis_client.rpush("log_queue", json.dumps(log_item))

            db.add(
                RequestLog(
                    api_key=log_item.get("api_key"),
                    path=log_item.get("path"),
                    status_code=log_item.get("status_code"),
                    cache_status=log_item.get("cache_status"),
                    cache_key=log_item.get("cache_key"),
                    cache_ttl=log_item.get("cache_ttl"),
                    circuit_state=log_item.get("circuit_state"),
                    circuit_blocked=False,
                    upstream_latency_ms=log_item.get("upstream_latency_ms"),
                    upstream_error_type=log_item.get("upstream_error_type"),
                )
            )
            db.commit()

        except Exception as e:
            db.rollback()
            print("Logger worker error:", e)
        finally:
            db.close()
            log_queue.task_done()
