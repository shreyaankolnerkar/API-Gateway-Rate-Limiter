import json

from app.core.redis import redis_client
from app.core.runtime import log_queue
from app.db.models import RequestLog
from app.db.session import SessionLocal


async def logger_worker():
    while True:
        log_item = await log_queue.get()
        db = SessionLocal()
        try:
            # Save to Redis
            await redis_client.rpush("log_queue", json.dumps(log_item))

            # Save to Postgres
            db.add(
                RequestLog(
                    api_key=log_item["api_key"],
                    path=log_item["path"],
                    status_code=log_item["status_code"],
                )
            )
            db.commit()

        except Exception as e:
            db.rollback()
            print("Logger worker error:", e)
        finally:
            db.close()
            log_queue.task_done()
